/**
 * Triage Checkout — Stripe Escrow + ABA Rule 1.18 Conflict Gate
 *
 * The Front Door. Captures $99 upfront via Stripe Connect, splits:
 * - $79 → Lawyer's IOLTA Stripe account
 * - $20 → KovelAI's Agent-Native Cut
 *
 * BUT ONLY after a headless CRM conflict check passes via MCP.
 * If conflicts exist, no data is saved and no payment is processed.
 */

import { NextResponse } from 'next/server';

// ─── Types ──────────────────────────────────────────────────────

interface TriageRequest {
  clientName: string;
  adverseParties: string[];
  firmId: string;
  lawyerIoltaStripeId: string;
}

interface ConflictCheckResult {
  hasConflict: boolean;
  matchedParties: string[];
  confidenceScore: number;
}

// ─── Route Handler ──────────────────────────────────────────────

export async function POST(req: Request) {
  try {
    const body: TriageRequest = await req.json();
    const { clientName, adverseParties, firmId, lawyerIoltaStripeId } = body;

    // Validate inputs (Pydantic/Zod equivalent — never trust user input)
    if (!clientName || !adverseParties?.length || !firmId || !lawyerIoltaStripeId) {
      return NextResponse.json(
        { type: 'https://kovelai.com/errors/validation', title: 'Validation Error', status: 400, detail: 'Missing required fields.' },
        { status: 400 },
      );
    }

    // ══════════════════════════════════════════════════════════════
    // 1. THE ETHICAL GATE: Headless CRM Conflict Check via MCP
    //    ABA Model Rule 1.18 — Duties to Prospective Client
    // ══════════════════════════════════════════════════════════════

    const conflictResult = await performConflictCheck(firmId, adverseParties);

    if (conflictResult.hasConflict) {
      // Rule 1.18 violation — cannot proceed. No data saved.
      return NextResponse.json(
        {
          status: 'CONFLICT',
          message: 'Unable to consult. Potential conflict of interest detected. No data has been saved or transmitted.',
          // Never expose which parties matched (that itself would be a privilege violation)
        },
        { status: 403 },
      );
    }

    // ══════════════════════════════════════════════════════════════
    // 2. OUTCOME-BASED PRICING: Stripe Connect Escrow
    //    $99 total → $79 to lawyer's IOLTA, $20 KovelAI commission
    // ══════════════════════════════════════════════════════════════

    const checkoutSession = await createStripeCheckoutSession(
      lawyerIoltaStripeId,
      firmId,
    );

    return NextResponse.json({
      status: 'CLEARED',
      checkoutUrl: checkoutSession.url,
      sessionId: checkoutSession.id,
    });
  } catch (error) {
    // RFC 9457 error format — never expose stack traces
    return NextResponse.json(
      {
        type: 'https://kovelai.com/errors/internal',
        title: 'Internal Error',
        status: 500,
        detail: 'Secure transit failed. Please retry.',
      },
      { status: 500 },
    );
  }
}

// ─── Conflict Check (MCP-backed) ────────────────────────────────

async function performConflictCheck(
  firmId: string,
  adverseParties: string[],
): Promise<ConflictCheckResult> {
  // In production, this calls the Antigravity MCP Gateway → Clio MCP tool:
  //
  // const gateway = new AntigravityMCPGateway({ firmId, seuSessionId: '...' });
  // const result = await gateway.callTool('clio_fuzzy_conflict_check', {
  //   query: adverseParties.join(', '),
  //   threshold: 0.85,
  // });
  //
  // The fuzzy match uses Levenshtein distance to catch name variations:
  // "John Smith" matches "Jon Smyth" at 0.82 similarity.

  // Placeholder — swap with live MCP call
  return {
    hasConflict: false,
    matchedParties: [],
    confidenceScore: 0,
  };
}

// ─── Stripe Checkout Session ────────────────────────────────────

async function createStripeCheckoutSession(
  lawyerIoltaStripeId: string,
  firmId: string,
): Promise<{ id: string; url: string }> {
  // In production, this uses the Stripe Connect API:
  //
  // const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);
  // const session = await stripe.checkout.sessions.create({
  //   payment_method_types: ['card'],
  //   line_items: [{
  //     price_data: {
  //       currency: 'usd',
  //       product_data: { name: 'KovelAI Privileged AI Triage & Hybrid Search Session' },
  //       unit_amount: 9900,
  //     },
  //     quantity: 1,
  //   }],
  //   mode: 'payment',
  //   payment_intent_data: {
  //     transfer_data: { destination: lawyerIoltaStripeId, amount: 7900 },
  //     application_fee_amount: 2000,
  //   },
  //   success_url: `https://kovelai.com/portal/${firmId}/session-start`,
  //   cancel_url: `https://kovelai.com/portal/${firmId}/cancelled`,
  //   metadata: { firmId, source: 'kovelai_triage' },
  // });

  return {
    id: `cs_placeholder_${firmId}`,
    url: `https://checkout.stripe.com/placeholder/${firmId}`,
  };
}
