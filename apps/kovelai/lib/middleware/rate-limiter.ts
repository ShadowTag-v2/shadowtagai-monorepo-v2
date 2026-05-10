/**
 * Rate Limiter Middleware for KovelAI API Routes
 *
 * Sprint Item #14: Per-user, per-endpoint rate limiting.
 *
 * Uses in-memory sliding window for MVP, upgradeable to
 * Cloud Armor or Redis for production scale.
 *
 * @see docs/cor30-security-audit.md — Finding: "Missing rate limiting"
 */

import { type NextRequest, NextResponse } from 'next/server';

// ─── Configuration ──────────────────────────────────────────────────

interface RateLimitConfig {
  windowMs: number;
  maxRequests: number;
  keyGenerator: (req: NextRequest) => string;
}

const DEFAULT_CONFIG: RateLimitConfig = {
  windowMs: 60_000, // 1 minute
  maxRequests: 30,
  keyGenerator: (req) => {
    const forwarded = req.headers.get('x-forwarded-for');
    const ip = forwarded?.split(',')[0]?.trim() ?? 'unknown';
    return `${ip}:${req.nextUrl.pathname}`;
  },
};

const ROUTE_LIMITS: Record<string, Partial<RateLimitConfig>> = {
  '/api/privileged-search': { maxRequests: 10, windowMs: 60_000 },
  '/api/war-room/murder-board': { maxRequests: 5, windowMs: 60_000 },
  '/api/war-room/stream': { maxRequests: 5, windowMs: 60_000 },
  '/api/tokens/byok': { maxRequests: 20, windowMs: 60_000 },
};

// ─── Sliding Window Store ───────────────────────────────────────────

interface WindowEntry {
  timestamps: number[];
  blocked: boolean;
}

const store = new Map<string, WindowEntry>();

// Cleanup stale entries every 5 minutes
setInterval(() => {
  const now = Date.now();
  for (const [key, entry] of store.entries()) {
    entry.timestamps = entry.timestamps.filter((t) => now - t < 300_000);
    if (entry.timestamps.length === 0) {
      store.delete(key);
    }
  }
}, 300_000);

// ─── Middleware ──────────────────────────────────────────────────────

export function createRateLimiter(customConfig?: Partial<RateLimitConfig>) {
  const config = { ...DEFAULT_CONFIG, ...customConfig };

  return function rateLimitMiddleware(handler: (req: NextRequest) => Promise<NextResponse>) {
    return async function rateLimitedHandler(req: NextRequest): Promise<NextResponse> {
      const routeConfig = ROUTE_LIMITS[req.nextUrl.pathname];
      const effectiveConfig = { ...config, ...routeConfig };
      const key = effectiveConfig.keyGenerator(req);
      const now = Date.now();

      let entry = store.get(key);
      if (!entry) {
        entry = { timestamps: [], blocked: false };
        store.set(key, entry);
      }

      // Slide the window
      entry.timestamps = entry.timestamps.filter((t) => now - t < effectiveConfig.windowMs);

      if (entry.timestamps.length >= effectiveConfig.maxRequests) {
        const retryAfter = Math.ceil((entry.timestamps[0] + effectiveConfig.windowMs - now) / 1000);

        return NextResponse.json(
          {
            error: 'Too many requests',
            retryAfter,
            limit: effectiveConfig.maxRequests,
            window: `${effectiveConfig.windowMs / 1000}s`,
          },
          {
            status: 429,
            headers: {
              'Retry-After': String(retryAfter),
              'X-RateLimit-Limit': String(effectiveConfig.maxRequests),
              'X-RateLimit-Remaining': '0',
              'X-RateLimit-Reset': String(
                Math.ceil((entry.timestamps[0] + effectiveConfig.windowMs) / 1000),
              ),
            },
          },
        );
      }

      // Record this request
      entry.timestamps.push(now);
      const remaining = effectiveConfig.maxRequests - entry.timestamps.length;

      // Execute handler
      const response = await handler(req);

      // Attach rate limit headers
      response.headers.set('X-RateLimit-Limit', String(effectiveConfig.maxRequests));
      response.headers.set('X-RateLimit-Remaining', String(remaining));

      return response;
    };
  };
}

// ─── Utility: Apply to route handler ────────────────────────────────

export function withRateLimit(
  handler: (req: NextRequest) => Promise<NextResponse>,
  config?: Partial<RateLimitConfig>,
): (req: NextRequest) => Promise<NextResponse> {
  return createRateLimiter(config)(handler);
}
