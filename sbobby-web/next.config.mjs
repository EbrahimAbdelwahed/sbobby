/** @type {import('next').NextConfig} */
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "base-uri 'self'",
      "connect-src 'self' https://*.blob.vercel-storage.com https://*.public.blob.vercel-storage.com",
      "font-src 'self'",
      "form-action 'self'",
      "frame-ancestors 'none'",
      "img-src 'self' data:",
      "object-src 'none'",
      "script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval'",
      "style-src 'self' 'unsafe-inline'",
      "worker-src 'self' blob:",
      "child-src 'self' blob:",
    ].join('; ')
  },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'no-referrer' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' }
];

const nextConfig = {
  poweredByHeader: false,
  reactStrictMode: true,
  async headers() {
    return [{ source: '/(.*)', headers: securityHeaders }];
  }
};

export default nextConfig;
