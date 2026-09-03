import { startWorkerJob } from '@/src/server/runpod';
import { del } from '@vercel/blob';

export const runtime = 'nodejs';

function isBlobUrl(value: string) {
  try {
    return new URL(value).hostname.endsWith('.blob.vercel-storage.com');
  } catch {
    return false;
  }
}

export async function POST(request: Request): Promise<Response> {
  try {
    const body = await request.json() as { audioUrl?: unknown; title?: unknown };
    if (typeof body.audioUrl !== 'string' || !isBlobUrl(body.audioUrl) || typeof body.title !== 'string') {
      return Response.json({ error: 'INVALID_JOB' }, { status: 400 });
    }
    try {
      const result = await startWorkerJob(body.audioUrl, body.title.slice(0, 120));
      return Response.json(result, { headers: { 'Cache-Control': 'no-store' } });
    } catch (error) {
      await del(body.audioUrl).catch(() => undefined);
      throw error;
    }
  } catch (error) {
    const code = error instanceof Error ? error.message : 'WORKER_UNAVAILABLE';
    return Response.json({ error: code }, { status: code === 'WORKER_NOT_CONFIGURED' ? 503 : 502 });
  }
}
