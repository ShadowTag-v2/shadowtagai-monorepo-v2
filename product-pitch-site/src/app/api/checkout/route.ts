import { NextRequest, NextResponse } from "next/server";
import { getStripe, STRIPE_PRICES, BETA_COUPON } from "@/lib/stripe";

type PlanTier = keyof typeof STRIPE_PRICES;

interface CheckoutRequestBody {
  tier: PlanTier;
  coupon?: string;
}

/**
 * POST /api/checkout
 *
 * Creates a Stripe Checkout Session for the selected pricing tier.
 * Redirects the customer to Stripe's hosted checkout page.
 *
 * Body: { tier: "solo" | "practice" | "enterprise", coupon?: string }
 */
export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as CheckoutRequestBody;
    const { tier, coupon } = body;

    // Validate tier
    if (!tier || !STRIPE_PRICES[tier]) {
      return NextResponse.json(
        { error: "Invalid pricing tier. Must be: solo, practice, or enterprise" },
        { status: 400 }
      );
    }

    const stripe = getStripe();
    const priceId = STRIPE_PRICES[tier].monthly;
    const origin = request.headers.get("origin") || "https://kovelai.web.app";

    // Build checkout session params
    // Item 9: Also accept coupon from URL query params
    const urlCoupon = request.nextUrl.searchParams.get("coupon");
    const effectiveCoupon = coupon || urlCoupon;

    const sessionParams: Parameters<typeof stripe.checkout.sessions.create>[0] = {
      mode: "subscription",
      payment_method_types: ["card"],
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      success_url: `${origin}/?checkout=success&session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${origin}/#pricing`,
      // Item 8: Billing portal return URL
      customer_creation: "always",
      metadata: {
        tier,
        source: "kovelai-pitch-site",
      },
      subscription_data: {
        metadata: {
          tier,
          source: "kovelai-pitch-site",
        },
      },
      // Item 8: After payment, allow access to billing portal
      after_expiration: {
        recovery: {
          enabled: true,
          allow_promotion_codes: true,
        },
      },
    };

    // Item 9: Apply beta coupon (3wseBY7Z) if provided via body or URL param
    if (effectiveCoupon === BETA_COUPON) {
      sessionParams.discounts = [{ coupon: BETA_COUPON }];
    }

    const session = await stripe.checkout.sessions.create(sessionParams);

    return NextResponse.json({ url: session.url }, { status: 200 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    console.error("[checkout] Error creating session:", message);

    // Return actionable error in dev, generic in prod
    if (message.includes("STRIPE_SECRET_KEY")) {
      return NextResponse.json(
        { error: "Stripe is not configured. Set STRIPE_SECRET_KEY in .env.local" },
        { status: 503 }
      );
    }

    return NextResponse.json(
      { error: "Failed to create checkout session" },
      { status: 500 }
    );
  }
}
