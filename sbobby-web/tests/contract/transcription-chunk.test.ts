import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest';
import { AUDIO_CHUNK_BUDGET } from '@/src/client/audio/chunk-budget';
import { POST } from '@/app/api/internal/spikes/transcription-chunk/route';

const savedEnv = { enabled: process.env.PROVIDER_CALLS_ENABLED, key: process.env.GROQ_API_KEY, probe: process.env.SPIKE_PROBE_KEY };
const endpoint = 'https://api.groq.com/openai/v1/audio/transcriptions';
function validMp3(size: number): Uint8Array {
  const bytes = new Uint8Array(size);
  bytes.set([0x49, 0x44, 0x33, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x22]);
  bytes.set([0xff, 0xfb, 0x90, 0x64], 44);
  return bytes;
}

function request(bytes: Uint8Array, extra: Record<string, string> = {}) {
  return new Request('https://preview.example/api/internal/spikes/transcription-chunk', {
    method: 'POST',
    headers: {
      origin: 'https://preview.example',
      host: 'preview.example',
      'content-type': AUDIO_CHUNK_BUDGET.internalMediaType,
      'x-audio-probe': 'test-probe',
      'x-audio-sequence': '0',
      'x-audio-start-ms': '0',
      'x-audio-end-ms': '1000',
      'x-audio-source-start-ms': '0',
      'x-audio-source-end-ms': '1000',
      'x-audio-byte-length': String(bytes.byteLength),
      ...extra
    },
    body: bytes.buffer as ArrayBuffer
  });
}

describe('transcription probe contract', () => {
  beforeEach(() => {
    process.env.PROVIDER_CALLS_ENABLED = 'true';
    process.env.GROQ_API_KEY = 'test-key';
    process.env.SPIKE_PROBE_KEY = 'test-probe';
  });
  afterEach(() => {
    vi.restoreAllMocks();
    if (savedEnv.enabled === undefined) delete process.env.PROVIDER_CALLS_ENABLED; else process.env.PROVIDER_CALLS_ENABLED = savedEnv.enabled;
    if (savedEnv.key === undefined) delete process.env.GROQ_API_KEY; else process.env.GROQ_API_KEY = savedEnv.key;
    if (savedEnv.probe === undefined) delete process.env.SPIKE_PROBE_KEY; else process.env.SPIKE_PROBE_KEY = savedEnv.probe;
  });

  it('forwards one raw bounded MP3 body and returns normalized timestamps', async () => {
    const bytes = validMp3(128);
    const provider = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ text: 'ciao', segments: [{ start: 0, end: 0.9, text: 'ciao' }], words: [{ start: 0, end: 0.5, word: 'ciao' }] }), { status: 200, headers: { 'content-type': 'application/json' } }));
    const response = await POST(request(bytes));
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ sequence: 0, startMs: 0, endMs: 1000, text: 'ciao', spans: [{ startMs: 0, endMs: 900, text: 'ciao' }] });
    expect(provider).toHaveBeenCalledTimes(1);
    expect(provider.mock.calls[0][0]).toBe(endpoint);
    const init = provider.mock.calls[0][1] as RequestInit;
    expect(init.body).toBeInstanceOf(FormData);
  });

  it('enforces just-below, exact, and above body caps before provider use', async () => {
    const provider = vi.spyOn(globalThis, 'fetch').mockImplementation(async () => new Response(JSON.stringify({ text: '', segments: [] }), { status: 200 }));
    for (const size of [AUDIO_CHUNK_BUDGET.maxRequestBodyBytes - 1, AUDIO_CHUNK_BUDGET.maxRequestBodyBytes]) {
      const bytes = validMp3(size);
      const response = await POST(request(bytes));
      expect(response.status).toBe(200);
    }
    const above = validMp3(AUDIO_CHUNK_BUDGET.maxRequestBodyBytes + 1);
    expect((await POST(request(above))).status).toBe(413);
    expect(provider).toHaveBeenCalledTimes(2);
  }, 20_000);

  it('keeps normalized response JSON within the one-megabyte cap', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async () => new Response(JSON.stringify({ text: 'x'.repeat(999_950), segments: [] }), { status: 200 }));
    const response = await POST(request(validMp3(128)));
    expect(response.status).toBe(502);
    expect(new TextEncoder().encode(await response.text()).byteLength).toBeLessThanOrEqual(AUDIO_CHUNK_BUDGET.maxResponseBytes);
  });

  it('rejects non-canonical timeline metadata before the provider call', async () => {
    const provider = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ text: '', segments: [] }), { status: 200 }));
    const response = await POST(request(validMp3(128), { 'x-audio-sequence': '1' }));
    expect(response.status).toBe(400);
    expect(await response.json()).toEqual({ error: 'INVALID_METADATA' });
    expect(provider).not.toHaveBeenCalled();
  });
});
