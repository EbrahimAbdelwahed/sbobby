import { del } from '@vercel/blob';
import { getWorkerJob } from '@/src/server/runpod';

export const runtime = 'nodejs';

function isBlobUrl(value: string) {
  try {
    return new URL(value).hostname.endsWith('.blob.vercel-storage.com');
  } catch {
    return false;
  }
}

export async function POST(request: Request, { params }: { params: Promise<{ jobId: string }> }): Promise<Response> {
  const { jobId } = await params;
  try {
    const { audioUrl } = await request.json() as { audioUrl?: unknown };
    const result = await getWorkerJob(jobId);
    const workerOutput = result.output as { status?: unknown; error?: unknown } | undefined;
    if (result.status === 'COMPLETED' && workerOutput?.status === 'failed') {
      result.status = 'FAILED';
      result.error = workerOutput.error ?? 'PIPELINE_FAILED';
    }
    if ((result.status === 'COMPLETED' || result.status === 'FAILED') && typeof audioUrl === 'string' && isBlobUrl(audioUrl)) {
      await del(audioUrl).catch(() => undefined);
    }
    return Response.json(result, { headers: { 'Cache-Control': 'no-store' } });
  } catch (error) {
    const code = error instanceof Error ? error.message : 'WORKER_UNAVAILABLE';
    return Response.json({ error: code }, { status: code === 'WORKER_NOT_CONFIGURED' ? 503 : 502 });
  }
}
