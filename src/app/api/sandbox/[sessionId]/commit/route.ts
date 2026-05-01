// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * POST /api/sandbox/[sessionId]/commit
 *
 * Executes the attorney's accept/reject/partial decision
 * by forwarding to the Python firestore_bridge.py commit endpoint.
 *
 * Body:
 *   { action: CommitAction, selectedFiles?: string[], matterId: string }
 *
 * Security:
 *   - Attorney auth verified by middleware
 *   - Idempotency key from X-Idempotency-Key header
 *   - Trust Level 0 enforced by bridge
 */

import { type NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.COUNSELCONDUIT_API_URL
  ?? 'https://counselconduit-767252945109.us-central1.run.app';

interface CommitRequestBody {
  action: 'accept' | 'reject' | 'partial_accept';
  selectedFiles?: string[];
  matterId: string;
  rejectionReason?: string;
}

export async function POST(
  request: NextRequest,
  { params }: { params: { sessionId: string } },
) {
  const sessionId = params.sessionId;

  let body: CommitRequestBody;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      { error: 'Invalid JSON body' },
      { status: 400 },
    );
  }

  const { action, selectedFiles, matterId, rejectionReason } = body;

  if (!action || !matterId) {
    return NextResponse.json(
      { error: 'Missing required fields: action, matterId' },
      { status: 400 },
    );
  }

  // Validate action enum
  const validActions = ['accept', 'reject', 'partial_accept'];
  if (!validActions.includes(action)) {
    return NextResponse.json(
      { error: `Invalid action: ${action}. Must be one of: ${validActions.join(', ')}` },
      { status: 400 },
    );
  }

  try {
    const backendRes = await fetch(
      `${BACKEND_URL}/api/sandbox/${sessionId}/commit`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Forward auth + idempotency
          ...(request.headers.get('authorization')
            ? { Authorization: request.headers.get('authorization')! }
            : {}),
          ...(request.headers.get('x-idempotency-key')
            ? { 'X-Idempotency-Key': request.headers.get('x-idempotency-key')! }
            : {}),
        },
        body: JSON.stringify({
          action,
          selected_files: selectedFiles,
          matter_id: matterId,
          rejection_reason: rejectionReason ?? '',
        }),
        signal: AbortSignal.timeout(30_000),
      },
    );

    if (!backendRes.ok) {
      const errorBody = await backendRes.text();
      return NextResponse.json(
        { error: `Backend error: ${backendRes.status}`, details: errorBody },
        { status: backendRes.status },
      );
    }

    const result = await backendRes.json();
    return NextResponse.json(result);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Internal error';
    console.error('[sandbox/commit] Failed:', message);
    return NextResponse.json(
      { error: message },
      { status: 502 },
    );
  }
}
