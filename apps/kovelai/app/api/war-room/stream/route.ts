/**
 * Oracle Studio SSE Streaming API
 *
 * Real-time streaming endpoint for the 7-stage Murder Board pipeline.
 * Uses Server-Sent Events (SSE) for low-latency progress updates
 * to the War Room dashboard.
 *
 * Nag Protocol #16: Oracle Studio 7-stage pipeline SSE streaming
 */
import { type NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import {
  createMurderBoardSSEStream,
  type MurderBoardInput,
} from '@/lib/orchestrator/murder-board-v2';
import { verifySEUToken } from '@/lib/security/seu-token-manager';

// ─── Request Schema ───────────────────────────────────────────────────
const StreamRequestSchema = z.object({
  caseDescription: z.string().min(10).max(50000),
  firmId: z.string().uuid(),
  clientId: z.string().uuid(),
  jurisdiction: z.string().min(2).max(50),
  practiceArea: z.string().min(2).max(100),
  matterId: z.string().optional(),
  documents: z.array(z.string()).optional(),
  modelTier: z.enum(['reasoning', 'flash', 'lite']).optional(),
  ephemeralToken: z.string().min(1),
  sandboxId: z.string().min(1),
});

// ─── SSE Endpoint ─────────────────────────────────────────────────────
export async function POST(req: NextRequest): Promise<Response> {
  try {
    const body = await req.json();
    const parsed = StreamRequestSchema.parse(body);

    // Validate S.E.U. token
    const clientIp = req.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ?? '0.0.0.0';
    await verifySEUToken(parsed.ephemeralToken, clientIp, parsed.sandboxId);

    // Build pipeline input
    const input: MurderBoardInput = {
      caseDescription: parsed.caseDescription,
      firmId: parsed.firmId,
      clientId: parsed.clientId,
      jurisdiction: parsed.jurisdiction,
      practiceArea: parsed.practiceArea,
      matterId: parsed.matterId,
      documents: parsed.documents,
      modelTier: parsed.modelTier,
    };

    // Create SSE stream
    const stream = createMurderBoardSSEStream(input);

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        Connection: 'keep-alive',
        'X-Privilege-Shield': 'kovel-doctrine-active',
      },
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request', details: error.errors },
        { status: 400 },
      );
    }
    return NextResponse.json({ error: 'Pipeline initialization failed' }, { status: 500 });
  }
}
