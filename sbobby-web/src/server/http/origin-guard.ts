export type OriginCheck = { ok: true } | { ok: false; status: 403; code: 'ORIGIN_REQUIRED' | 'ORIGIN_MISMATCH' | 'PROBE_REQUIRED' };

function exactSecret(actual: string | null, expected: string | undefined): boolean {
  if (!actual || !expected || actual.length !== expected.length) return false;
  let difference = 0;
  for (let index = 0; index < actual.length; index += 1) difference |= actual.charCodeAt(index) ^ expected.charCodeAt(index);
  return difference === 0;
}

export function checkPreviewOrigin(request: Request): OriginCheck {
  const origin = request.headers.get('origin');
  const host = request.headers.get('host');
  if (!origin || origin === 'null' || !host) return { ok: false, status: 403, code: 'ORIGIN_REQUIRED' };
  try {
    const parsed = new URL(origin);
    const local = host.startsWith('localhost:') || host.startsWith('127.0.0.1:');
    if (parsed.host !== host || (!local && parsed.protocol !== 'https:') || (local && !['http:', 'https:'].includes(parsed.protocol))) return { ok: false, status: 403, code: 'ORIGIN_MISMATCH' };
  } catch {
    return { ok: false, status: 403, code: 'ORIGIN_MISMATCH' };
  }
  if (!exactSecret(request.headers.get('x-audio-probe'), process.env.SPIKE_PROBE_KEY)) return { ok: false, status: 403, code: 'PROBE_REQUIRED' };
  return { ok: true };
}
