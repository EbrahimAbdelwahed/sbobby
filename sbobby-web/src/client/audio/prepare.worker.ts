import { FFmpeg } from '@ffmpeg/ffmpeg';
import { fetchFile } from '@ffmpeg/util';
import {
  AUDIO_CHUNK_BUDGET,
  AUDIO_RESOURCE_CAPS,
  isSupportedAudioFile,
  chunkTimeRange,
  validatePreparedChunk,
  validateSourceBounds,
  type AudioChunkBudget,
  type AudioSourceDescriptor
} from './chunk-budget';
import type { WorkerRequest, WorkerResponse, WorkerTelemetry } from './worker-protocol';

const ffmpeg = new FFmpeg();
let activeRequestId: string | null = null;
let abortRequested = false;
let loaded = false;
let activeAbortController: AbortController | null = null;

const PUBLIC_WORKER_ERRORS = new Set([
  'ABORTED',
  'BUDGET_CONTRACT',
  'CHUNK_DURATION_LIMIT',
  'CHUNK_MEDIA_TYPE',
  'CHUNK_OVERLAP_LIMIT',
  'CHUNK_OVERLAP_RANGE',
  'CHUNK_SIZE_LIMIT',
  'CHUNK_TIME_RANGE',
  'DURATION_UNAVAILABLE',
  'ENCODE_FAILED',
  'OUTPUT_LIMIT',
  'RESOURCE_CAP_LIMIT',
  'SOURCE_DURATION_LIMIT',
  'SOURCE_DURATION_TARGET',
  'SOURCE_SIZE_LIMIT',
  'UNSUPPORTED_AUDIO',
  'WALL_TIME_LIMIT'
]);

const now = () => performance.now();

function telemetry(phase: WorkerTelemetry['phase'], startedAt: number, inputBytes: number, chunksProduced: number, outputBytes: number, extra: Partial<WorkerTelemetry> = {}): WorkerTelemetry {
  return {
    phase,
    chunksProduced,
    inputBytes,
    outputBytes,
    elapsedMs: Math.round(now() - startedAt),
    peakBytesEstimate: Math.min(AUDIO_RESOURCE_CAPS.maxSourceBytes + AUDIO_CHUNK_BUDGET.maxAudioBytes * 2, inputBytes + outputBytes + AUDIO_CHUNK_BUDGET.maxAudioBytes * 2),
    ...extra
  };
}

async function ensureLoaded(requestId: string, startedAt: number, inputBytes: number): Promise<void> {
  if (loaded) return;
  self.postMessage({ type: 'ready', requestId, telemetry: telemetry('loading', startedAt, inputBytes, 0, 0) } satisfies WorkerResponse);
  await ffmpeg.load({
    // @ffmpeg/ffmpeg resolves relative worker URLs against its bundled
    // package URL. Use absolute same-origin URLs so Turbopack's worker
    // bundle cannot turn these into file:///ROOT/... paths.
    classWorkerURL: new URL('/ffmpeg/ffmpeg-worker.js', self.location.origin).href,
    coreURL: new URL('/ffmpeg/ffmpeg-core.esm.js', self.location.origin).href,
    wasmURL: new URL('/ffmpeg/ffmpeg-core.esm.wasm', self.location.origin).href
  });
  loaded = true;
}

function parseDuration(log: string): number {
  const match = log.match(/Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)/);
  if (!match) throw new Error('DURATION_UNAVAILABLE');
  const [, hours, minutes, seconds] = match;
  const duration = (Number(hours) * 3600 + Number(minutes) * 60 + Number(seconds)) * 1000;
  if (!Number.isFinite(duration) || duration <= 0) throw new Error('DURATION_UNAVAILABLE');
  return Math.round(duration);
}

async function inspectFile(file: File, requestId: string, startedAt: number): Promise<AudioSourceDescriptor> {
  if (!isSupportedAudioFile(file)) throw new Error('UNSUPPORTED_AUDIO');
  validateSourceBounds(file.size);
  await ensureLoaded(requestId, startedAt, file.size);
  const inputName = file.name.toLowerCase().endsWith('.m4a') ? 'source.m4a' : 'source.mp3';
  await ffmpeg.writeFile(inputName, await fetchFile(file));
  let output = '';
  const onLog = ({ message }: { message: string }) => {
    output += `${message}\n`;
  };
  ffmpeg.on('log', onLog);
  try {
    activeAbortController = new AbortController();
    // ffprobe writes the requested output file in the pinned browser build,
    // but its wrapper reports -1 even when the command completed. Trust the
    // bounded output file and validate its numeric duration below.
    await ffmpeg.ffprobe(['-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', inputName, '-o', 'duration.txt'], 120_000, { signal: activeAbortController.signal });
    const durationFile = await ffmpeg.readFile('duration.txt', 'utf8');
    const durationText = typeof durationFile === 'string' ? durationFile : new TextDecoder().decode(durationFile);
    const durationMs = Math.round(Number.parseFloat(durationText.trim()) * 1000);
    if (!Number.isFinite(durationMs) || durationMs <= 0) throw new Error('DURATION_UNAVAILABLE');
    validateSourceBounds(file.size, durationMs);
    return {
      sizeBytes: file.size,
      nameHint: inputName.endsWith('.m4a') ? 'm4a' : 'mp3',
      mimeType: file.type || 'application/octet-stream',
      durationMs,
      decodedSamplesEstimate: Math.ceil((durationMs / 1000) * AUDIO_CHUNK_BUDGET.sampleRate)
    };
  } catch (error) {
    // Some FFmpeg builds omit ffprobe output; the regular log remains a safe diagnostic.
    if (output) {
      const durationMs = parseDuration(output);
      validateSourceBounds(file.size, durationMs);
      return {
        sizeBytes: file.size,
        nameHint: inputName.endsWith('.m4a') ? 'm4a' : 'mp3',
        mimeType: file.type || 'application/octet-stream',
        durationMs,
        decodedSamplesEstimate: Math.ceil((durationMs / 1000) * AUDIO_CHUNK_BUDGET.sampleRate)
      };
    }
    throw error;
  } finally {
    activeAbortController = null;
    ffmpeg.off('log', onLog);
    await ffmpeg.deleteFile(inputName).catch(() => undefined);
    await ffmpeg.deleteFile('duration.txt').catch(() => undefined);
  }
}

async function prepareFile(file: File, requestId: string, budget: AudioChunkBudget, startedAt: number): Promise<void> {
  if (!isSupportedAudioFile(file)) throw new Error('UNSUPPORTED_AUDIO');
  validateSourceBounds(file.size);
  if (budget.internalMediaType !== AUDIO_CHUNK_BUDGET.internalMediaType || budget.maxAudioBytes !== AUDIO_CHUNK_BUDGET.maxAudioBytes || budget.overlapMs !== AUDIO_CHUNK_BUDGET.overlapMs) {
    throw new Error('BUDGET_CONTRACT');
  }
  await ensureLoaded(requestId, startedAt, file.size);
  const descriptor = await inspectFile(file, requestId, startedAt);
  const inputName = file.name.toLowerCase().endsWith('.m4a') ? 'source.m4a' : 'source.mp3';
  await ffmpeg.writeFile(inputName, await fetchFile(file));
  const durationMs = descriptor.durationMs;
  const count = Math.ceil(durationMs / AUDIO_CHUNK_BUDGET.chunkDurationMs);
  if (count > AUDIO_RESOURCE_CAPS.maxChunks || descriptor.decodedSamplesEstimate > AUDIO_RESOURCE_CAPS.maxDecodedSamples) throw new Error('RESOURCE_CAP_LIMIT');
  let outputBytes = 0;
  const started = startedAt;

  try {
    for (let sequence = 0; sequence < count; sequence += 1) {
      if (abortRequested || activeRequestId !== requestId) throw new Error('ABORTED');
      if (now() - started > AUDIO_RESOURCE_CAPS.maxWallTimeMs) throw new Error('WALL_TIME_LIMIT');
      const { startMs, endMs, sourceStartMs, sourceEndMs } = chunkTimeRange(durationMs, sequence);
      const startSeconds = (sourceStartMs / 1000).toFixed(3);
      const spanSeconds = ((sourceEndMs - sourceStartMs) / 1000).toFixed(3);
      const outputName = `chunk-${sequence}.mp3`;
      activeAbortController = new AbortController();
      const result = await ffmpeg.exec([
        '-ss', startSeconds,
        '-i', inputName,
        '-t', spanSeconds,
        '-vn',
        '-map_metadata', '-1',
        '-ac', String(AUDIO_CHUNK_BUDGET.channels),
        '-ar', String(AUDIO_CHUNK_BUDGET.sampleRate),
        '-c:a', 'libmp3lame',
        '-b:a', AUDIO_CHUNK_BUDGET.bitrate,
        '-write_xing', '0',
        outputName
      ], 120_000, { signal: activeAbortController.signal });
      activeAbortController = null;
      if (result !== 0) throw new Error('ENCODE_FAILED');
      const encoded = await ffmpeg.readFile(outputName);
      const bytes = typeof encoded === 'string' ? new TextEncoder().encode(encoded) : encoded;
      const chunk = {
        sequence,
        startMs,
        endMs,
        sourceStartMs,
        sourceEndMs,
        bytes,
        mediaType: AUDIO_CHUNK_BUDGET.internalMediaType
      };
      validatePreparedChunk(chunk);
      outputBytes += bytes.byteLength;
      if (outputBytes > AUDIO_RESOURCE_CAPS.maxOutputBytes) throw new Error('OUTPUT_LIMIT');
      const transferable = bytes.slice().buffer as ArrayBuffer;
      const response = {
        type: 'chunk',
        requestId,
        chunk: { ...chunk, bytes: transferable },
        telemetry: telemetry('encoding', startedAt, file.size, sequence + 1, outputBytes, { sequence })
      } satisfies WorkerResponse;
      self.postMessage(response, { transfer: [response.chunk.bytes] });
      await ffmpeg.deleteFile(outputName);
    }
  } finally {
    activeAbortController = null;
    await ffmpeg.deleteFile(inputName).catch(() => undefined);
  }
}

async function handle(request: WorkerRequest): Promise<void> {
  if (request.type === 'abort') {
    if (request.requestId === activeRequestId) {
      abortRequested = true;
      activeAbortController?.abort();
      ffmpeg.terminate();
      loaded = false;
    }
    return;
  }
  activeRequestId = request.requestId;
  abortRequested = false;
  const startedAt = now();
  const inputBytes = request.file.size;
  try {
    if (request.type === 'inspect') {
      const descriptor = await inspectFile(request.file, request.requestId, startedAt);
      self.postMessage({ type: 'descriptor', requestId: request.requestId, descriptor, telemetry: telemetry('complete', startedAt, inputBytes, 0, 0) } satisfies WorkerResponse);
    } else {
      await prepareFile(request.file, request.requestId, request.budget, startedAt);
      self.postMessage({ type: 'done', requestId: request.requestId, telemetry: telemetry('complete', startedAt, inputBytes, 0, 0) } satisfies WorkerResponse);
    }
  } catch (error) {
    // FFmpeg can include source paths or provider diagnostics in an Error.
    // Only stable, path-free public codes may cross the worker boundary.
    const candidate = error instanceof Error ? error.message : '';
    const code = PUBLIC_WORKER_ERRORS.has(candidate) ? candidate : 'WORKER_FAILED';
    self.postMessage({ type: 'error', requestId: request.requestId, code, telemetry: telemetry(code === 'ABORTED' ? 'aborted' : 'failed', startedAt, inputBytes, 0, 0) } satisfies WorkerResponse);
    if (code !== 'ABORTED' && ['RESOURCE_CAP_LIMIT', 'OUTPUT_LIMIT', 'WALL_TIME_LIMIT'].includes(code)) {
      ffmpeg.terminate();
      loaded = false;
    }
  } finally {
    activeRequestId = null;
    abortRequested = false;
    activeAbortController = null;
  }
}

self.onmessage = (event: MessageEvent<WorkerRequest>) => {
  void handle(event.data);
};
