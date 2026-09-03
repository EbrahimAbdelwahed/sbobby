import { handleUpload, type HandleUploadBody } from '@vercel/blob/client';

export const runtime = 'nodejs';

export async function POST(request: Request): Promise<Response> {
  const body = await request.json() as HandleUploadBody;
  try {
    const response = await handleUpload({
      request,
      body,
      onBeforeGenerateToken: async (pathname) => {
        if (!pathname.startsWith('audio/') || !/\.(mp3|m4a)$/i.test(pathname)) throw new Error('Unsupported upload');
        return {
          allowedContentTypes: ['audio/mpeg', 'audio/mp4', 'audio/x-m4a'],
          maximumSizeInBytes: 250 * 1024 * 1024,
          addRandomSuffix: true,
          cacheControlMaxAge: 60
        };
      }
    });
    return Response.json(response);
  } catch {
    return Response.json({ error: 'UPLOAD_UNAVAILABLE' }, { status: 400 });
  }
}
