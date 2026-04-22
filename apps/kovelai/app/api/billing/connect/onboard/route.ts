/**
 * Stripe Connect Onboarding Flow
 *
 * Dual-billing Stripe Connect setup:
 * 1. Client → Lawyer: Client subscribes via law firm's Stripe Connect account
 * 2. Lawyer → Us: Auto-scaling tiered subscription
 *
 * Nag Protocol #18: Set up Stripe Connect onboarding flow
 */
import { NextResponse, type NextRequest } from 'next/server';
import { z } from 'zod';

const OnboardingSchema = z.object({
  firmId: z.string().uuid(),
  firmName: z.string().min(1).max(200),
  contactEmail: z.string().email(),
  country: z.string().length(2).default('US'),
  businessType: z.enum(['individual', 'company', 'non_profit']).default('company'),
  returnUrl: z.string().url().optional(),
  refreshUrl: z.string().url().optional(),
});

export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    const body = await req.json();
    const parsed = OnboardingSchema.parse(body);

    const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
    if (!stripeSecretKey) {
      return NextResponse.json(
        { error: 'Stripe not configured' },
        { status: 503 },
      );
    }

    // Step 1: Create Connected Account for the law firm
    const accountRes = await fetch('https://api.stripe.com/v1/accounts', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${stripeSecretKey}`,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        type: 'standard',
        country: parsed.country,
        email: parsed.contactEmail,
        'business_profile[name]': parsed.firmName,
        'business_profile[product_description]': 'Legal services via KovelAI platform',
        'metadata[firm_id]': parsed.firmId,
        'metadata[platform]': 'kovelai',
      }),
    });

    if (!accountRes.ok) {
      const error = await accountRes.json();
      return NextResponse.json(
        { error: 'Stripe account creation failed', details: error },
        { status: 502 },
      );
    }

    const account = await accountRes.json();

    // Step 2: Create Account Link for onboarding
    const baseUrl = process.env.KOVELAI_BASE_URL ?? 'https://kovelai.web.app';
    const linkRes = await fetch('https://api.stripe.com/v1/account_links', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${stripeSecretKey}`,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        account: account.id,
        refresh_url: parsed.refreshUrl ?? `${baseUrl}/settings/billing?refresh=true`,
        return_url: parsed.returnUrl ?? `${baseUrl}/settings/billing?onboarded=true`,
        type: 'account_onboarding',
      }),
    });

    if (!linkRes.ok) {
      const error = await linkRes.json();
      return NextResponse.json(
        { error: 'Stripe onboarding link failed', details: error },
        { status: 502 },
      );
    }

    const link = await linkRes.json();

    return NextResponse.json({
      status: 'ONBOARDING_INITIATED',
      stripeAccountId: account.id,
      onboardingUrl: link.url,
      expiresAt: new Date(link.expires_at * 1000).toISOString(),
      firmId: parsed.firmId,
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request', details: error.errors },
        { status: 400 },
      );
    }
    return NextResponse.json(
      { error: 'Onboarding failed' },
      { status: 500 },
    );
  }
}
