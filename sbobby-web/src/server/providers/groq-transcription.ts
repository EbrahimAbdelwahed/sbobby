import { AUDIO_CHUNK_BUDGET, type PreparedAudioChunk } from '@/src/client/audio/chunk-budget';

export type TranscriptionSpan = { startMs: number; endMs: number; text: string };
export type GroqTranscription = { text: string; spans: TranscriptionSpan[] };

const PROVIDER_URL = 'https://api.groq.com/openai/v1/audio/transcriptions';
const PROVIDER_TIMEOUT_MS = 30_000;

export class GroqProviderError extends Error {
  constructor(public readonly kind: 'disabled' | 'timeout' | 'too_large' | 'rejected' | 'unavailable') {
    super(`GROQ_${kind.toUpperCase()}`);
  }
}

async function readBounded(response: Response): Promise<string> {
  if (!response.body) return '';
  const reader = response.body.getReader();
  const parts: Uint8Array[] = [];
  let total = 0;
  try {
    while (true) {
      const next = await reader.read();
      if (next.done) break;
      total += next.value.byteLength;
      if (total > AUDIO_CHUNK_BUDGET.maxResponseBytes) {
        await reader.cancel();
        throw new GroqProviderError('too_large');
      }
      parts.push(next.value);
    }
  } finally {
    reader.releaseLock();
  }
  const output = new Uint8Array(total);
  let offset = 0;
  for (const part of parts) {
    output.set(part, offset);
    offset += part.byteLength;
  }
  return new TextDecoder().decode(output);
}

function normalizePayload(payload: unknown): GroqTranscription {
  if (!payload || typeof payload !== 'object') throw new GroqProviderError('rejected');
  const record = payload as { text?: unknown; segments?: unknown };
  const text = typeof record.text === 'string' ? record.text : '';
  // Word timestamps are requested for the later transcript contract; S00 only
  // promotes segment spans and deliberately drops provider words here.
  const spans: TranscriptionSpan[] = [];
  if (Array.isArray(record.segments)) {
    for (const segment of record.segments) {
      if (!segment || typeof segment !== 'object') continue;
      const value = segment as { start?: unknown; end?: unknown; text?: unknown };
      const startMs = Math.max(0, Math.round(Number(value.start) * 1000));
      const endMs = Math.max(startMs, Math.round(Number(value.end) * 1000));
      if (Number.isFinite(startMs) && Number.isFinite(endMs) && endMs > startMs && typeof value.text === 'string') spans.push({ startMs, endMs, text: value.text.trim() });
    }
  }
  return { text, spans };
}

export async function transcribeChunk(chunk: PreparedAudioChunk): Promise<GroqTranscription> {
  const key = process.env.GROQ_API_KEY;
  if (process.env.PROVIDER_CALLS_ENABLED !== 'true' || !key) throw new GroqProviderError('disabled');
  if (chunk.bytes.byteLength > AUDIO_CHUNK_BUDGET.maxRequestBodyBytes) throw new GroqProviderError('too_large');
  const form = new FormData();
  form.append('file', new Blob([chunk.bytes.slice().buffer as ArrayBuffer], { type: AUDIO_CHUNK_BUDGET.internalMediaType }), 'chunk.mp3');
  form.append('model', 'whisper-large-v3');
  form.append('language', 'it');
  form.append('temperature', '0');
  form.append('response_format', 'verbose_json');
  form.append('timestamp_granularities[]', 'segment');
  form.append('timestamp_granularities[]', 'word');
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), PROVIDER_TIMEOUT_MS);
  try {
    let response: Response;
    try {
      response = await fetch(PROVIDER_URL, {
        method: 'POST',
        headers: { Authorization: `Bearer ${key}` },
        body: form,
        signal: controller.signal,
        cache: 'no-store'
      });
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') throw new GroqProviderError('timeout');
      throw new GroqProviderError('unavailable');
    }
    const body = await readBounded(response);
    if (!response.ok) throw new GroqProviderError(response.status === 408 || response.status === 504 ? 'timeout' : 'rejected');
    try {
      return normalizePayload(JSON.parse(body));
    } catch {
      throw new GroqProviderError('rejected');
    }
  } finally {
    clearTimeout(timer);
  }
}
