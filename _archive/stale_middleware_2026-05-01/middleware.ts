import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';
import { type NextRequest, NextResponse } from 'next/server';

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});
const ratelimit = new Ratelimit({ redis, limiter: Ratelimit.slidingWindow(10, '10 s') });
export async function middleware(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith('/api/')) {
    const { success } = await ratelimit.limit(request.ip ?? '127.0.0.1');
    if (!success) return NextResponse.json({ error: 'Rate limit exceeded' }, { status: 429 });
  }
  return NextResponse.next();
}
export const config = { matcher: '/api/:path*' };
