import { startWorkerJob } from '@/src/server/runpod';
import { del, issueSignedToken, presignUrl } from '@vercel/blob';

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
      const pathname = decodeURIComponent(new URL(body.audioUrl).pathname.slice(1));
      const validUntil = Date.now() + 2 * 60 * 60 * 1000;
      const signedToken = await issueSignedToken({ pathname, operations: ['get'], validUntil });
      const { presignedUrl } = await presignUrl(signedToken, {
        access: 'private',
        operation: 'get',
        pathname,
        validUntil,
        useCache: false,
      });
      const result = await startWorkerJob(presignedUrl, body.title.slice(0, 120));
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
