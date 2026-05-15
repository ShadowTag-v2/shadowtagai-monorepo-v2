/**
 * KovelAI CSP Nonce Middleware
 *
 * Generates a per-request cryptographic nonce and injects it into the
 * Content-Security-Policy header. This replaces the static CSP in
 * next.config.mjs to enable strict nonce-based script execution.
 *
 * @see https://web.dev/articles/strict-csp
 * @see Cor.30 Pillar 3 — API Hardening / XSS Mitigation
 */
import { type NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  // Generate a cryptographic nonce (128-bit, base64-encoded)
  const nonce = Buffer.from(crypto.randomUUID()).toString('base64');

  // Build strict nonce-based CSP
  // - 'strict-dynamic' auto-trusts scripts loaded by nonced scripts (CSP3)
  // - 'unsafe-inline' is a fallback ignored when nonce is present (CSP3 spec)
  // - style-src keeps 'unsafe-inline' because next/font/google injects inline styles
  const cspDirectives = [
    `default-src 'self'`,
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic' https: 'unsafe-inline'`,
    `style-src 'self' 'unsafe-inline' https://fonts.googleapis.com`,
    `font-src 'self' https://fonts.gstatic.com`,
    `img-src 'self' data: https: blob:`,
    `connect-src 'self' https://*.googleapis.com https://*.firebaseio.com https://*.stripe.com https://api.perplexity.ai https://www.google-analytics.com wss://*.firebaseio.com`,
    `frame-src https://js.stripe.com https://hooks.stripe.com`,
    `object-src 'none'`,
    `base-uri 'self'`,
    `form-action 'self'`,
    `frame-ancestors 'none'`,
  ];

  const cspHeader = cspDirectives.join('; ');

  // Pass nonce to server components via request header
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set('x-nonce', nonce);

  const response = NextResponse.next({
    request: { headers: requestHeaders },
  });

  // Set CSP on the response
  response.headers.set('Content-Security-Policy', cspHeader);

  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - api routes (handled separately)
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon/manifest/icons (static assets)
     */
    {
      source: '/((?!api|_next/static|_next/image|favicon.*|manifest.json|apple-touch-icon.png).*)',
      missing: [
        { type: 'header', key: 'next-router-prefetch' },
        { type: 'header', key: 'purpose', value: 'prefetch' },
      ],
    },
  ],
};
