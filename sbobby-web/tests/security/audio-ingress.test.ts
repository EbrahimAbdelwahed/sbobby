import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AUDIO_CHUNK_BUDGET } from '@/src/client/audio/chunk-budget';
import { POST } from '@/app/api/internal/spikes/transcription-chunk/route';

const saved = { enabled: process.env.PROVIDER_CALLS_ENABLED, key: process.env.GROQ_API_KEY, probe: process.env.SPIKE_PROBE_KEY };
function makeRequest(origin: string | null, host = 'preview.example', bytes = new Uint8Array([0x49, 0x44, 0x33, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x22, ...new Array(34).fill(0), 0xff, 0xfb, 0x90, 0x64])) {
  return new Request(`https://${host}/api/internal/spikes/transcription-chunk`, { method: 'POST', headers: { ...(origin === null ? {} : { origin }), host, 'content-type': AUDIO_CHUNK_BUDGET.internalMediaType, 'x-audio-probe': 'test-probe', 'x-audio-sequence': '0', 'x-audio-start-ms': '0', 'x-audio-end-ms': '1000', 'x-audio-byte-length': String(bytes.byteLength) }, body: bytes.buffer as ArrayBuffer });
}

describe('audio ingress security boundary', () => {
  beforeEach(() => { process.env.PROVIDER_CALLS_ENABLED = 'true'; process.env.GROQ_API_KEY = 'test-key'; process.env.SPIKE_PROBE_KEY = 'test-probe'; });
  afterEach(() => { vi.restoreAllMocks(); for (const [name, value] of Object.entries({ PROVIDER_CALLS_ENABLED: saved.enabled, GROQ_API_KEY: saved.key, SPIKE_PROBE_KEY: saved.probe })) { if (value === undefined) delete process.env[name]; else process.env[name] = value; } });

  it.each([
    ['missing origin', null, 'preview.example'],
    ['null origin', 'null', 'preview.example'],
    ['cross-site origin', 'https://evil.example', 'preview.example'],
    ['spoofed host', 'https://preview.example', 'evil.example']
  ])('%s never reaches Groq', async (_name, origin, host) => {
    const provider = vi.spyOn(globalThis, 'fetch');
    const response = await POST(makeRequest(origin, host));
    expect(response.status).toBe(403);
    expect(provider).not.toHaveBeenCalled();
  });

  it('rejects forged probe, permissive media, malformed bytes, and disabled calls before Groq', async () => {
    const provider = vi.spyOn(globalThis, 'fetch');
    const forged = makeRequest('https://preview.example'); forged.headers.set('x-audio-probe', 'forged');
    expect((await POST(forged)).status).toBe(403);
    const malformed = makeRequest('https://preview.example', 'preview.example', new Uint8Array([1, 2, 3, 4]));
    expect((await POST(malformed)).status).toBe(415);
    const permissive = makeRequest('https://preview.example'); permissive.headers.set('content-type', 'multipart/form-data');
    expect((await POST(permissive)).status).toBe(415);
    process.env.PROVIDER_CALLS_ENABLED = 'false';
    expect((await POST(makeRequest('https://preview.example'))).status).toBe(503);
    expect(provider).not.toHaveBeenCalled();
  });

  it('does not treat a truncated ID3 header as a valid MP3 frame', async () => {
    const provider = vi.spyOn(globalThis, 'fetch');
    const truncated = new Uint8Array(128);
    truncated.set([0x49, 0x44, 0x33, 0x04, 0x00, 0x00, 0x00, 0x00, 0x7f, 0x7f]);
    expect((await POST(makeRequest('https://preview.example', 'preview.example', truncated))).status).toBe(415);
    expect(provider).not.toHaveBeenCalled();
  });

  it('redacts provider body from public errors', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('secret-provider-body-and-filename', { status: 500 }));
    const response = await POST(makeRequest('https://preview.example'));
    const body = await response.text();
    expect(response.status).toBe(502);
    expect(body).not.toContain('secret-provider-body-and-filename');
    expect(body).not.toContain('filename');
  });
});
