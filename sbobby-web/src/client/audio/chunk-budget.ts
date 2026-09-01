/**
 * The one audio transport contract for S00. Chunks are raw CBR mono MP3;
 * headers are sent separately so multipart overhead cannot invalidate the cap.
 */
export const AUDIO_CHUNK_BUDGET = {
  maxAudioBytes: 3_500_000,
  maxRequestBodyBytes: 3_500_000,
  maxResponseBytes: 1_000_000,
  overlapMs: 5_000,
  internalMediaType: 'audio/mpeg',
  internalExtension: 'mp3',
  chunkDurationMs: 450_000,
  sampleRate: 16_000,
  channels: 1,
  bitrate: '48k'
} as const;

export const AUDIO_RESOURCE_CAPS = {
  maxSourceBytes: 250 * 1024 * 1024,
  requiredFixtureDurationMs: 90 * 60 * 1000,
  targetDurationMs: 180 * 60 * 1000,
  maxDecodedSamples: 180 * 60 * 16_000,
  maxOutputBytes: 250 * 1024 * 1024,
  maxChunks: 64,
  maxWallTimeMs: 10 * 60 * 1000,
  maxResponseBytes: 1_000_000
} as const;

export type AudioChunkBudget = {
  maxAudioBytes: number;
  maxRequestBodyBytes: number;
  maxResponseBytes: number;
  overlapMs: number;
  internalMediaType: string;
};

export type AudioSourceDescriptor = {
  sizeBytes: number;
  nameHint: 'm4a' | 'mp3';
  mimeType: string;
  durationMs: number;
  decodedSamplesEstimate: number;
};

export type PreparedAudioChunk = {
  sequence: number;
  startMs: number;
  endMs: number;
  sourceStartMs: number;
  sourceEndMs: number;
  bytes: Uint8Array;
  mediaType: typeof AUDIO_CHUNK_BUDGET.internalMediaType;
};

export function isSupportedAudioFile(file: Pick<File, 'name' | 'type' | 'size'>): boolean {
  const name = file.name.toLowerCase();
  return file.size > 0 && (name.endsWith('.m4a') || name.endsWith('.mp3'));
}

export function validateSourceBounds(sizeBytes: number, durationMs?: number): void {
  if (!Number.isFinite(sizeBytes) || sizeBytes <= 0 || sizeBytes > AUDIO_RESOURCE_CAPS.maxSourceBytes) {
    throw new Error('SOURCE_SIZE_LIMIT');
  }
  if (durationMs !== undefined && (!Number.isFinite(durationMs) || durationMs <= 0)) {
    throw new Error('SOURCE_DURATION_LIMIT');
  }
  if (durationMs !== undefined && durationMs > AUDIO_RESOURCE_CAPS.targetDurationMs) {
    throw new Error('SOURCE_DURATION_TARGET');
  }
}

export function validatePreparedChunk(chunk: Pick<PreparedAudioChunk, 'bytes' | 'startMs' | 'endMs' | 'sourceStartMs' | 'sourceEndMs' | 'mediaType'>): void {
  if (chunk.bytes.byteLength <= 0 || chunk.bytes.byteLength > AUDIO_CHUNK_BUDGET.maxAudioBytes) {
    throw new Error('CHUNK_SIZE_LIMIT');
  }
  if (chunk.mediaType !== AUDIO_CHUNK_BUDGET.internalMediaType) {
    throw new Error('CHUNK_MEDIA_TYPE');
  }
  if (!Number.isSafeInteger(chunk.startMs) || !Number.isSafeInteger(chunk.endMs) || chunk.endMs <= chunk.startMs) {
    throw new Error('CHUNK_TIME_RANGE');
  }
  if (chunk.sourceStartMs < 0 || chunk.sourceStartMs > chunk.startMs || chunk.sourceEndMs < chunk.endMs || chunk.sourceEndMs <= chunk.sourceStartMs) {
    throw new Error('CHUNK_OVERLAP_RANGE');
  }
  if (chunk.startMs - chunk.sourceStartMs > AUDIO_CHUNK_BUDGET.overlapMs || chunk.sourceEndMs - chunk.endMs > AUDIO_CHUNK_BUDGET.overlapMs) throw new Error('CHUNK_OVERLAP_LIMIT');
  if (chunk.endMs - chunk.startMs > AUDIO_CHUNK_BUDGET.chunkDurationMs + AUDIO_CHUNK_BUDGET.overlapMs * 2) {
    throw new Error('CHUNK_DURATION_LIMIT');
  }
}

export function assertRequestBodySize(bytes: number): void {
  if (!Number.isInteger(bytes) || bytes <= 0 || bytes > AUDIO_CHUNK_BUDGET.maxRequestBodyBytes) {
    throw new Error('REQUEST_BODY_LIMIT');
  }
}

/** Canonical timeline: coverage is gap-free/non-overlapping; encoded source range overlaps by 5s. */
export function chunkTimeRange(durationMs: number, sequence: number): Pick<PreparedAudioChunk, 'startMs' | 'endMs' | 'sourceStartMs' | 'sourceEndMs'> {
  if (!Number.isFinite(durationMs) || durationMs <= 0 || !Number.isSafeInteger(sequence) || sequence < 0) throw new Error('CHUNK_TIME_RANGE');
  const startMs = sequence * AUDIO_CHUNK_BUDGET.chunkDurationMs;
  const endMs = Math.min(durationMs, startMs + AUDIO_CHUNK_BUDGET.chunkDurationMs);
  if (startMs >= durationMs) throw new Error('CHUNK_TIME_RANGE');
  return { startMs, endMs, sourceStartMs: Math.max(0, startMs - AUDIO_CHUNK_BUDGET.overlapMs), sourceEndMs: Math.min(durationMs, endMs + AUDIO_CHUNK_BUDGET.overlapMs) };
}
