/**
 * @fileoverview War Room Murder Board — API Route
 *
 * Triggers the 7-step Murder Board cognitive pipeline.
 * Accepts a Vent Mode transcript and S.E.U. token, creates a
 * pipeline session, and enqueues Stage 1 via Cloud Tasks.
 *
 * @see murder-board.ts — Pipeline orchestrator
 * @see WAR_ROOM_ARCHITECTURE.md — Technical design
 */

import { NextResponse } from 'next/server';
import crypto from 'crypto';
import { verifySeuToken } from '@/lib/security/seu_and_stripe';
import {
  createSession,
  getSession,
  runFullPipeline,
} from '@/lib/orchestrator/murder-board';

export const runtime = 'edge';

interface MurderBoardRequest {
  transcript: string;
  seuToken: string;
  clioOAuthToken?: string;
  contextCacheId?: string;
}

/**
 * POST — Trigger a new Murder Board pipeline.
 */
export async function POST(req: Request) {
  try {
    const {
      transcript,
      seuToken,
      clioOAuthToken,
      contextCacheId,
    }: MurderBoardRequest = await req.json();

    // 1. Validate S.E.U. token
    const clientIp = req.headers.get('x-forwarded-for') || 'unknown';
    const payload = await verifySeuToken(seuToken, clientIp);

    // 2. Generate session ID
    const sessionId = crypto.randomUUID();
    const firmId = payload.firmId ?? 'unknown';

    // 3. Create pipeline session in Firestore
    await createSession(
      sessionId,
      firmId,
      transcript,
      seuToken,
      clioOAuthToken,
      contextCacheId,
    );

    // 4. In production, enqueue Stage 1 via Cloud Tasks.
    //    For development, run the full pipeline directly.
    if (process.env.NODE_ENV === 'production') {
      // TODO: Enqueue via Cloud Tasks
      // await enqueueCloudTask('kovelai-murder-board', {
      //   sessionId,
      //   stage: 1,
      // });
    } else {
      // Development: run full pipeline (background)
      // @ts-expect-error: waitUntil available in Edge Runtime
      req.waitUntil(runFullPipeline(sessionId));
    }

    return NextResponse.json(
      {
        sessionId,
        status: 'intake',
        message: 'Murder Board pipeline initiated',
        statusUrl: `/api/war-room/status/${sessionId}`,
      },
      {
        status: 202,
        headers: {
          'Cache-Control': 'no-store',
          'X-Kovel-Attestation': 'active',
          'X-War-Room-Session': sessionId,
        },
      },
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      {
        error: 'Murder Board initiation failed',
        detail: message,
      },
      { status: 403 },
    );
  }
}

/**
 * GET — Check pipeline status for a session.
 */
export async function GET(req: Request) {
  const url = new URL(req.url);
  const sessionId = url.searchParams.get('sessionId');

  if (!sessionId) {
    return NextResponse.json(
      { error: 'sessionId parameter required' },
      { status: 400 },
    );
  }

  const session = await getSession(sessionId);

  if (!session) {
    return NextResponse.json(
      { error: 'Session not found' },
      { status: 404 },
    );
  }

  return NextResponse.json({
    sessionId: session.sessionId,
    status: session.status,
    hasIntakeData: !!session.intakeData,
    hasVerbAudit: !!session.verbAudit,
    verbCount: session.verbAudit?.length || 0,
    hasOracleMemo: !!session.oracleMemo,
    citationCount: session.citations?.length || 0,
    hasBrief: !!session.briefContent,
    error: session.error,
  });
}
