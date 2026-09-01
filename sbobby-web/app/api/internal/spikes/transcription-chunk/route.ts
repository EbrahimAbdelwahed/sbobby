import { AUDIO_CHUNK_BUDGET, AUDIO_RESOURCE_CAPS, assertRequestBodySize, validatePreparedChunk, type PreparedAudioChunk } from '@/src/client/audio/chunk-budget';
import { checkPreviewOrigin } from '@/src/server/http/origin-guard';
import { GroqProviderError, transcribeChunk } from '@/src/server/providers/groq-transcription';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

let inFlight = false;

const responseHeaders = { 'Cache-Control': 'no-store, max-age=0', 'X-Content-Type-Options': 'nosniff' };

function json(data: Record<string, unknown>, status: number): Response {
  const payload = JSON.stringify(data);
  if (new TextEncoder().encode(payload).byteLength > AUDIO_CHUNK_BUDGET.maxResponseBytes && data.error !== 'RESPONSE_LIMIT') return Response.json({ error: 'RESPONSE_LIMIT' }, { status: 502, headers: responseHeaders });
  return new Response(payload, { status, headers: { ...responseHeaders, 'content-type': 'application/json; charset=utf-8' } });
}

function integerHeader(request: Request, name: string, fallback = NaN): number {
  const value = request.headers.get(name);
  return value === null ? fallback : Number(value);
}

async function boundedBody(request: Request): Promise<Uint8Array> {
  const length = Number(request.headers.get('content-length'));
  if (Number.isFinite(length) && length > AUDIO_CHUNK_BUDGET.maxRequestBodyBytes) throw new GroqProviderError('too_large');
  if (!request.body) return new Uint8Array(await request.arrayBuffer());
  const reader = request.body.getReader();
  const pieces: Uint8Array[] = [];
  let total = 0;
  try {
    while (true) {
      const next = await reader.read();
      if (next.done) break;
      total += next.value.byteLength;
      if (total > AUDIO_CHUNK_BUDGET.maxRequestBodyBytes) {
        await reader.cancel();
        throw new GroqProviderError('too_large');
      }
      pieces.push(next.value);
    }
  } finally {
    reader.releaseLock();
  }
  const body = new Uint8Array(total);
  let offset = 0;
  for (const piece of pieces) {
    body.set(piece, offset);
    offset += piece.byteLength;
  }
  return body;
}

function hasMp3Frame(bytes: Uint8Array): boolean {
  let start = 0;
  if (bytes.byteLength >= 10 && bytes[0] === 0x49 && bytes[1] === 0x44 && bytes[2] === 0x33) {
    const tagSize = (bytes[6] << 21) | (bytes[7] << 14) | (bytes[8] << 7) | bytes[9];
    const hasFooter = (bytes[5] & 0x10) !== 0;
    start = 10 + tagSize + (hasFooter ? 10 : 0);
    if (start > 65_536) return false;
  }
  for (let index = start; index + 3 < Math.min(bytes.byteLength, start + 4096); index += 1) {
    if (bytes[index] !== 0xff || (bytes[index + 1] & 0xe0) !== 0xe0) continue;
    const version = (bytes[index + 1] >> 3) & 0x03;
    const layer = (bytes[index + 1] >> 1) & 0x03;
    const bitrate = (bytes[index + 2] >> 4) & 0x0f;
    const sampleRate = (bytes[index + 2] >> 2) & 0x03;
    if (version !== 1 && layer !== 0 && bitrate !== 0 && bitrate !== 0x0f && sampleRate !== 0x03) return true;
  }
  return false;
}

export async function POST(request: Request): Promise<Response> {
  const origin = checkPreviewOrigin(request);
  if (!origin.ok) return json({ error: origin.code }, origin.status);
  if (process.env.PROVIDER_CALLS_ENABLED !== 'true' || !process.env.GROQ_API_KEY) return json({ error: 'PROVIDER_DISABLED' }, 503);
  if (inFlight) return json({ error: 'PROBE_BUSY' }, 429);
  if (request.headers.get('content-type') !== AUDIO_CHUNK_BUDGET.internalMediaType) return json({ error: 'UNSUPPORTED_MEDIA' }, 415);
  const sequence = integerHeader(request, 'x-audio-sequence');
  const startMs = integerHeader(request, 'x-audio-start-ms');
  const endMs = integerHeader(request, 'x-audio-end-ms');
  const sourceStartMs = integerHeader(request, 'x-audio-source-start-ms', startMs);
  const sourceEndMs = integerHeader(request, 'x-audio-source-end-ms', endMs);
  if (!Number.isSafeInteger(sequence) || sequence < 0 || sequence >= AUDIO_RESOURCE_CAPS.maxChunks || !Number.isSafeInteger(startMs) || !Number.isSafeInteger(endMs) || !Number.isSafeInteger(sourceStartMs) || !Number.isSafeInteger(sourceEndMs) || startMs !== sequence * AUDIO_CHUNK_BUDGET.chunkDurationMs || startMs < 0 || endMs <= startMs || endMs > AUDIO_RESOURCE_CAPS.targetDurationMs || sourceStartMs < 0 || sourceEndMs <= sourceStartMs || sourceStartMs > startMs || sourceEndMs < endMs || sourceStartMs < startMs - AUDIO_CHUNK_BUDGET.overlapMs || sourceEndMs > endMs + AUDIO_CHUNK_BUDGET.overlapMs) return json({ error: 'INVALID_METADATA' }, 400);
  let bytes: Uint8Array;
  try {
    bytes = await boundedBody(request);
    assertRequestBodySize(bytes.byteLength);
  } catch (error) {
    if (error instanceof GroqProviderError && error.kind === 'too_large') return json({ error: 'BODY_TOO_LARGE' }, 413);
    return json({ error: 'INVALID_BODY' }, 400);
  }
  const declared = integerHeader(request, 'x-audio-byte-length');
  if (declared !== bytes.byteLength) {
    bytes.fill(0);
    return json({ error: 'BODY_LENGTH_MISMATCH' }, 400);
  }
  const candidate: PreparedAudioChunk = { sequence, startMs, endMs, sourceStartMs, sourceEndMs, bytes, mediaType: AUDIO_CHUNK_BUDGET.internalMediaType };
  try {
    validatePreparedChunk(candidate);
  } catch {
    bytes.fill(0);
    return json({ error: 'INVALID_METADATA' }, 400);
  }
  if (!hasMp3Frame(bytes)) {
    bytes.fill(0);
    return json({ error: 'INVALID_AUDIO' }, 415);
  }
  const chunk = candidate;
  inFlight = true;
  try {
    const transcription = await transcribeChunk(chunk);
    return json({ sequence, startMs, endMs, text: transcription.text, spans: transcription.spans }, 200);
  } catch (error) {
    if (error instanceof GroqProviderError) {
      const status = error.kind === 'too_large' ? 413 : error.kind === 'timeout' ? 504 : error.kind === 'rejected' ? 502 : 503;
      return json({ error: error.message }, status);
    }
    return json({ error: 'PROVIDER_UNAVAILABLE' }, 503);
  } finally {
    bytes.fill(0);
    inFlight = false;
  }
}
