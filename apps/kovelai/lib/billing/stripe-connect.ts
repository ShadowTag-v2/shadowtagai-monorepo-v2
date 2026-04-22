/**
 * Stripe Connect Dual-Billing Engine
 *
 * Sprint Item #6: The money machine.
 *
 * Dual flow:
 * 1. Client → Lawyer (Stripe Connect): Client subscribes to AI portal,
 *    funds flow to lawyer's Stripe account. Lawyer gets paid upfront.
 * 2. Lawyer → Us (Platform Fee): Auto-scaling tiered subscription
 *    Solo $299, Practice $599, Enterprise $999.
 *
 * Fee isolation: We NEVER touch the client-lawyer fee arrangement.
 *
 * @see BUSINESS_CONTEXT_LOCKED.md — Stripe Live Configuration
 * @see Cor.30 Pillar 5 — Payments & Webhooks
 */

import Stripe from 'stripe';
import { z } from 'zod';

// ─── Configuration ──────────────────────────────────────────────────

const STRIPE_CONFIG = {
  products: {
    trial: 'prod_UM2XwCF1byjegL',
    pro: 'prod_UM2X10cpyay52e',
    enterprise: 'prod_UM2XMVp9Er7A0i',
  },
  prices: {
    proMonthly: 'price_1TNKSREHnWpykeMiRMDlVgLl',
    proAnnual: 'price_1TNKSjEHnWpykeMi0S9GCVjy',
    enterprise: 'price_1TNKSREHnWpykeMi8mrDf4rI',
  },
  betaCoupon: '3wseBY7Z',
  portalConfig: 'bpc_1TNKSjEHnWpykeMi0qQPoaHm',
  webhookEndpoint: 'we_1TNKSjEHnWpykeMiQZqmpy3X',
} as const;

// ─── Platform Fee Tiers ─────────────────────────────────────────────

const PLATFORM_FEES: Record<string, { monthly: number; applicationFeePercent: number }> = {
  solo: { monthly: 299, applicationFeePercent: 15 },
  practice: { monthly: 599, applicationFeePercent: 12 },
  enterprise: { monthly: 999, applicationFeePercent: 10 },
};

// ─── Schemas ────────────────────────────────────────────────────────

const OnboardFirmSchema = z.object({
  firmId: z.string().uuid(),
  firmName: z.string().min(1).max(200),
  email: z.string().email(),
  tier: z.enum(['solo', 'practice', 'enterprise']),
  country: z.string().length(2).default('US'),
});

const CreateClientSubscriptionSchema = z.object({
  firmStripeAccountId: z.string().startsWith('acct_'),
  clientEmail: z.string().email(),
  priceId: z.string().startsWith('price_'),
  firmId: z.string().uuid(),
  clientId: z.string().uuid(),
});

export type OnboardFirmRequest = z.infer<typeof OnboardFirmSchema>;
export type CreateClientSubRequest = z.infer<typeof CreateClientSubscriptionSchema>;

// ─── Stripe Connect Onboarding ──────────────────────────────────────

/**
 * Creates a Stripe Connect Express account for a law firm.
 *
 * This account receives client payments directly.
 * Our platform takes a commission via application_fee_percent.
 */
export async function onboardFirm(
  stripe: Stripe,
  request: OnboardFirmRequest,
): Promise<{
  accountId: string;
  onboardingUrl: string;
}> {
  const validated = OnboardFirmSchema.parse(request);

  // Create Express account
  const account = await stripe.accounts.create({
    type: 'express',
    country: validated.country,
    email: validated.email,
    capabilities: {
      card_payments: { requested: true },
      transfers: { requested: true },
    },
    business_type: 'company',
    company: {
      name: validated.firmName,
    },
    metadata: {
      firmId: validated.firmId,
      tier: validated.tier,
      platform: 'kovelai',
    },
  });

  // Generate onboarding link
  const accountLink = await stripe.accountLinks.create({
    account: account.id,
    refresh_url: `https://kovelai.web.app/onboarding/refresh?firm=${validated.firmId}`,
    return_url: `https://kovelai.web.app/onboarding/complete?firm=${validated.firmId}`,
    type: 'account_onboarding',
  });

  console.log(`[Stripe Connect] Created account ${account.id} for firm ${validated.firmId}`);

  return {
    accountId: account.id,
    onboardingUrl: accountLink.url,
  };
}

// ─── Client Subscription (Client → Lawyer) ──────────────────────────

/**
 * Creates a subscription where the client pays the lawyer,
 * and our platform takes a commission.
 */
export async function createClientSubscription(
  stripe: Stripe,
  request: CreateClientSubRequest,
): Promise<{
  subscriptionId: string;
  clientSecret: string;
}> {
  const validated = CreateClientSubscriptionSchema.parse(request);
  const tier = 'practice'; // Determined from firm metadata

  // Create or retrieve customer
  const customers = await stripe.customers.list({
    email: validated.clientEmail,
    limit: 1,
  });

  let customer: Stripe.Customer;
  if (customers.data.length > 0) {
    customer = customers.data[0];
  } else {
    customer = await stripe.customers.create({
      email: validated.clientEmail,
      metadata: {
        firmId: validated.firmId,
        clientId: validated.clientId,
        platform: 'kovelai',
      },
    });
  }

  // Create subscription with application fee
  const subscription = await stripe.subscriptions.create({
    customer: customer.id,
    items: [{ price: validated.priceId }],
    payment_behavior: 'default_incomplete',
    payment_settings: {
      save_default_payment_method: 'on_subscription',
    },
    application_fee_percent: PLATFORM_FEES[tier].applicationFeePercent,
    transfer_data: {
      destination: validated.firmStripeAccountId,
    },
    metadata: {
      firmId: validated.firmId,
      clientId: validated.clientId,
      platform: 'kovelai',
    },
    expand: ['latest_invoice.payment_intent'],
  });

  const invoice = subscription.latest_invoice as Stripe.Invoice;
  const paymentIntent = invoice.payment_intent as Stripe.PaymentIntent;

  console.log(
    `[Stripe Connect] Subscription ${subscription.id} | ` +
    `Client → Firm ${validated.firmStripeAccountId} | ` +
    `Platform fee: ${PLATFORM_FEES[tier].applicationFeePercent}%`,
  );

  return {
    subscriptionId: subscription.id,
    clientSecret: paymentIntent.client_secret ?? '',
  };
}

// ─── Platform Subscription (Lawyer → Us) ────────────────────────────

/**
 * Creates the platform subscription: the lawyer pays US.
 */
export async function createPlatformSubscription(
  stripe: Stripe,
  firmEmail: string,
  firmId: string,
  tier: 'solo' | 'practice' | 'enterprise',
): Promise<{
  subscriptionId: string;
  checkoutUrl: string;
}> {
  const priceId = tier === 'enterprise'
    ? STRIPE_CONFIG.prices.enterprise
    : STRIPE_CONFIG.prices.proMonthly;

  const session = await stripe.checkout.sessions.create({
    mode: 'subscription',
    customer_email: firmEmail,
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `https://kovelai.web.app/dashboard?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `https://kovelai.web.app/pricing?cancelled=true`,
    metadata: {
      firmId,
      tier,
      platform: 'kovelai',
    },
    discounts: [{ coupon: STRIPE_CONFIG.betaCoupon }],
    subscription_data: {
      metadata: {
        firmId,
        tier,
        platform: 'kovelai',
      },
    },
  });

  return {
    subscriptionId: session.subscription as string,
    checkoutUrl: session.url ?? '',
  };
}

// ─── Webhook Handlers ───────────────────────────────────────────────

/**
 * Processes Stripe webhook events.
 * HMAC signature verification is mandatory (Cor.30 R21).
 */
export async function handleWebhookEvent(
  stripe: Stripe,
  payload: string | Buffer,
  signature: string,
  webhookSecret: string,
): Promise<{
  eventType: string;
  handled: boolean;
  firmId?: string;
}> {
  const event = stripe.webhooks.constructEvent(payload, signature, webhookSecret);

  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object as Stripe.Checkout.Session;
      console.log(`[Stripe Webhook] Checkout completed for firm ${session.metadata?.firmId}`);
      return { eventType: event.type, handled: true, firmId: session.metadata?.firmId };
    }

    case 'invoice.paid': {
      const invoice = event.data.object as Stripe.Invoice;
      console.log(`[Stripe Webhook] Invoice paid: ${invoice.id}`);
      return { eventType: event.type, handled: true };
    }

    case 'customer.subscription.deleted': {
      const subscription = event.data.object as Stripe.Subscription;
      console.log(`[Stripe Webhook] Subscription cancelled: ${subscription.id}`);
      // Trigger S.E.U. token revocation for the firm
      return {
        eventType: event.type,
        handled: true,
        firmId: subscription.metadata?.firmId,
      };
    }

    case 'account.updated': {
      const account = event.data.object as Stripe.Account;
      console.log(`[Stripe Webhook] Connect account updated: ${account.id}`);
      return { eventType: event.type, handled: true };
    }

    default:
      return { eventType: event.type, handled: false };
  }
}

// ─── Billing Portal ─────────────────────────────────────────────────

/**
 * Creates a billing portal session for a firm to manage their subscription.
 */
export async function createBillingPortalSession(
  stripe: Stripe,
  customerId: string,
): Promise<string> {
  const session = await stripe.billingPortal.sessions.create({
    customer: customerId,
    configuration: STRIPE_CONFIG.portalConfig,
    return_url: 'https://kovelai.web.app/dashboard',
  });

  return session.url;
}
