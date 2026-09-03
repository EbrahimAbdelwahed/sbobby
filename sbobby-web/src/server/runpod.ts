const apiBase = 'https://api.runpod.ai/v2';

function config() {
  const endpoint = process.env.RUNPOD_ENDPOINT_ID;
  const key = process.env.RUNPOD_API_KEY;
  if (!endpoint || !key) throw new Error('WORKER_NOT_CONFIGURED');
  return { endpoint, key };
}

async function call(path: string, init?: RequestInit) {
  const { endpoint, key } = config();
  const response = await fetch(`${apiBase}/${endpoint}${path}`, {
    ...init,
    cache: 'no-store',
    headers: { Authorization: `Bearer ${key}`, 'content-type': 'application/json', ...init?.headers }
  });
  if (!response.ok) throw new Error('WORKER_UNAVAILABLE');
  return response.json() as Promise<Record<string, unknown>>;
}

export async function startWorkerJob(audioUrl: string, title: string) {
  return call('/run', { method: 'POST', body: JSON.stringify({ input: { audio_url: audioUrl, title } }) });
}

export async function getWorkerJob(jobId: string) {
  return call(`/status/${encodeURIComponent(jobId)}`);
}
