import { NextResponse } from 'next/server';

export async function GET() {
  // Silently swallow the IDE's internal Unleash telemetry request
  // so it stops throwing 404 errors in the Next.js console.
  return NextResponse.json({ status: 'ignored' }, { status: 200 });
}
