/**
 * Stripe Connect Webhook Handler
 *
 * Item #7: Stripe Connect test mode webhooks.
 *
 * Handles:
 * - checkout.session.completed → Provision client access
 * - customer.subscription.updated → Tier changes
 * - customer.subscription.deleted → Deactivate tenant
 * - account.updated → Connect onboarding status
 * - invoice.payment_failed → Notify lawyer
 *
 * Security: HMAC signature verification (Cor.30 Pillar 5)
 *
 * @see lib/billing/stripe-connect.ts
 */

import { type NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY ?? '', {
  apiVersion: '2025-03-31.basil',
});

const WEBHOOK_SECRET = process.env.STRIPE_WEBHOOK_SECRET ?? '';

// ─── Tier Mapping ───────────────────────────────────────────────────

const PRICE_TO_TIER: Record<string, string> = {
  price_1TNKSREHnWpykeMiRMDlVgLl: 'pro_monthly',
  price_1TNKSjEHnWpykeMi0S9GCVjy: 'pro_annual',
  price_1TNKSREHnWpykeMi8mrDf4rI: 'enterprise',
};

// ─── Main Handler ───────────────────────────────────────────────────

export async function POST(req: NextRequest): Promise<NextResponse> {
  const body = await req.text();
  const signature = req.headers.get('stripe-signature');

  if (!signature || !WEBHOOK_SECRET) {
    return NextResponse.json({ error: 'Missing signature' }, { status: 400 });
  }

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(body, signature, WEBHOOK_SECRET);
  } catch (err) {
    const _message = err instanceof Error ? err.message : 'Unknown';
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 });
  }

  // Idempotency: Check if event already processed
  const eventId = event.id;
  const processed = await checkIdempotency(eventId);
  if (processed) {
    return NextResponse.json({ received: true, duplicate: true });
  }

  try {
    switch (event.type) {
      case 'checkout.session.completed':
        await handleCheckoutCompleted(event.data.object as Stripe.Checkout.Session);
        break;

      case 'customer.subscription.updated':
        await handleSubscriptionUpdated(event.data.object as Stripe.Subscription);
        break;

      case 'customer.subscription.deleted':
        await handleSubscriptionDeleted(event.data.object as Stripe.Subscription);
        break;

      case 'account.updated':
        await handleAccountUpdated(event.data.object as Stripe.Account);
        break;

      case 'invoice.payment_failed':
        await handlePaymentFailed(event.data.object as Stripe.Invoice);
        break;

      default:
        console.log(`[STRIPE WEBHOOK] Unhandled event type: ${event.type}`);
    }

    await markProcessed(eventId);
    return NextResponse.json({ received: true });
  } catch (_err) {
    return NextResponse.json({ error: 'Handler failed' }, { status: 500 });
  }
}

// ─── Event Handlers ─────────────────────────────────────────────────

async function handleCheckoutCompleted(session: Stripe.Checkout.Session): Promise<void> {
  const firmId = session.metadata?.firmId;
  const clientEmail = session.customer_email;

  if (!firmId) {
    return;
  }

  console.log(`[STRIPE] Checkout completed: firm=${firmId}, client=${clientEmail}`);

  // Provision client access in the firm's tenant
  await provisionClient({
    firmId,
    clientEmail: clientEmail ?? '',
    subscriptionId: session.subscription as string,
    stripeCustomerId: session.customer as string,
  });
}

async function handleSubscriptionUpdated(subscription: Stripe.Subscription): Promise<void> {
  const firmId = subscription.metadata?.firmId;
  const priceId = subscription.items?.data?.[0]?.price?.id;
  const newTier = priceId ? (PRICE_TO_TIER[priceId] ?? 'unknown') : 'unknown';

  console.log(
    `[STRIPE] Subscription updated: firm=${firmId}, tier=${newTier}, status=${subscription.status}`,
  );

  if (firmId && subscription.status === 'active') {
    await updateTenantTier(firmId, newTier);
  }
}

async function handleSubscriptionDeleted(subscription: Stripe.Subscription): Promise<void> {
  const firmId = subscription.metadata?.firmId;

  console.log(`[STRIPE] Subscription deleted: firm=${firmId}`);

  if (firmId) {
    await deactivateTenant(firmId);
  }
}

async function handleAccountUpdated(account: Stripe.Account): Promise<void> {
  const firmId = account.metadata?.firmId;
  const chargesEnabled = account.charges_enabled;
  const payoutsEnabled = account.payouts_enabled;

  console.log(
    `[STRIPE] Account updated: firm=${firmId}, charges=${chargesEnabled}, payouts=${payoutsEnabled}`,
  );

  if (firmId) {
    await updateConnectStatus(firmId, {
      chargesEnabled: chargesEnabled ?? false,
      payoutsEnabled: payoutsEnabled ?? false,
      detailsSubmitted: account.details_submitted ?? false,
    });
  }
}

async function handlePaymentFailed(invoice: Stripe.Invoice): Promise<void> {
  const firmId = invoice.metadata?.firmId ?? '';
  const customerEmail = typeof invoice.customer_email === 'string' ? invoice.customer_email : '';
  const amountDue = invoice.amount_due;

  console.log(
    `[STRIPE] Payment failed: firm=${firmId}, email=${customerEmail}, amount=${amountDue}`,
  );

  if (firmId) {
    await notifyPaymentFailure(firmId, customerEmail, amountDue);
  }
}

// ─── Stub Implementations ──────────────────────────────────────────
// These will be wired to Firestore + Cloud Tasks

async function checkIdempotency(_eventId: string): Promise<boolean> {
  // TODO: Check Firestore for processed event IDs
  return false;
}

async function markProcessed(_eventId: string): Promise<void> {
  // TODO: Write event ID to Firestore with TTL
}

async function provisionClient(_data: {
  firmId: string;
  clientEmail: string;
  subscriptionId: string;
  stripeCustomerId: string;
}): Promise<void> {
  // TODO: Create client record in firm's tenant namespace
}

async function updateTenantTier(_firmId: string, _tier: string): Promise<void> {
  // TODO: Update firm tier in Firestore
}

async function deactivateTenant(_firmId: string): Promise<void> {
  // TODO: Mark tenant as inactive, revoke tokens
}

async function updateConnectStatus(
  _firmId: string,
  _status: { chargesEnabled: boolean; payoutsEnabled: boolean; detailsSubmitted: boolean },
): Promise<void> {
  // TODO: Update Connect onboarding status in Firestore
}

async function notifyPaymentFailure(
  _firmId: string,
  _email: string,
  _amount: number,
): Promise<void> {
  // TODO: Send payment failure notification via Cloud Tasks → Gmail API
}
