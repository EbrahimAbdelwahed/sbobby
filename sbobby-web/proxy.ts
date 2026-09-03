import { NextResponse, type NextRequest } from 'next/server';

export function proxy(request: NextRequest) {
  const expected = process.env.APP_SESSION_TOKEN;
  const actual = request.cookies.get('sbobby_session')?.value;
  if (!expected || actual !== expected) {
    const url = request.nextUrl.clone();
    url.pathname = '/sign-in';
    url.searchParams.set('next', request.nextUrl.pathname);
    return NextResponse.redirect(url);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/app/:path*', '/api/upload/:path*', '/api/jobs/:path*']
};
