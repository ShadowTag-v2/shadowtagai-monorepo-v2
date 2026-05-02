// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * GET /api/sandbox/[sessionId]/diffs
 *
 * Retrieves computed diffs for a sandbox session.
 * Calls the Python firestore_bridge.py compute_diffs endpoint
 * on the Cloud Run backend.
 *
 * Security:
 *   - Attorney auth verified by middleware
 *   - Session ID validated server-side
 *   - Trust Level 0 enforced by bridge
 */

import { type NextRequest, NextResponse } from 'next/server';

const BACKEND_URL =
  process.env.COUNSELCONDUIT_API_URL ?? 'https://counselconduit-767252945109.us-central1.run.app';

export async function GET(request: NextRequest, { params }: { params: { sessionId: string } }) {
  const sessionId = params.sessionId;
  const matterId = request.nextUrl.searchParams.get('matter') ?? '';

  if (!sessionId || !matterId) {
    return NextResponse.json({ error: 'Missing sessionId or matter parameter' }, { status: 400 });
  }

  try {
    // Forward to Python backend
    const backendRes = await fetch(
      `${BACKEND_URL}/api/sandbox/${sessionId}/diffs?matter=${encodeURIComponent(matterId)}`,
      {
        headers: {
          'Content-Type': 'application/json',
          // Forward auth token from client
          ...(request.headers.get('authorization')
            ? { Authorization: request.headers.get('authorization')! }
            : {}),
        },
        // 30s timeout for diff computation
        signal: AbortSignal.timeout(30_000),
      },
    );

    if (!backendRes.ok) {
      const body = await backendRes.text();
      return NextResponse.json(
        { error: `Backend error: ${backendRes.status}`, details: body },
        { status: backendRes.status },
      );
    }

    const data = await backendRes.json();
    return NextResponse.json(data);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Internal error';
    console.error('[sandbox/diffs] Failed:', message);
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
