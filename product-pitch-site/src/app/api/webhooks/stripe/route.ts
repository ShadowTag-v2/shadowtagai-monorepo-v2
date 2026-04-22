import { NextRequest, NextResponse } from "next/server";
import { getStripe } from "@/lib/stripe";
import type Stripe from "stripe";

/**
 * POST /api/webhooks/stripe
 *
 * Handles Stripe webhook events for subscription lifecycle management.
 * Verifies HMAC signature per Cor.30 R21-22.
 *
 * Required env: STRIPE_WEBHOOK_SECRET
 * Stripe Dashboard → Webhooks → Add endpoint → https://kovelai.web.app/api/webhooks/stripe
 *
 * Events handled:
 *   - checkout.session.completed → New subscription created
 *   - customer.subscription.updated → Plan change, renewal
 *   - customer.subscription.deleted → Cancellation
 *   - invoice.payment_succeeded → Successful charge
 *   - invoice.payment_failed → Failed charge (trigger retry email)
 */
export async function POST(request: NextRequest) {
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!webhookSecret) {
    console.error("[stripe-webhook] STRIPE_WEBHOOK_SECRET not configured");
    return NextResponse.json(
      { error: "Webhook not configured" },
      { status: 503 }
    );
  }

  // Read raw body for HMAC verification
  const rawBody = await request.text();
  const signature = request.headers.get("stripe-signature");

  if (!signature) {
    return NextResponse.json(
      { error: "Missing stripe-signature header" },
      { status: 400 }
    );
  }

  let event: Stripe.Event;

  try {
    const stripe = getStripe();
    event = stripe.webhooks.constructEvent(rawBody, signature, webhookSecret);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    console.error("[stripe-webhook] Signature verification failed:", message);
    return NextResponse.json(
      { error: "Invalid signature" },
      { status: 400 }
    );
  }

  // Idempotency: log event ID for dedup (per Cor.30 R22)
  console.info(
    JSON.stringify({
      severity: "INFO",
      message: "stripe_webhook_received",
      event_id: event.id,
      event_type: event.type,
      timestamp: new Date().toISOString(),
    })
  );

  try {
    switch (event.type) {
      case "checkout.session.completed": {
        const session = event.data.object as Stripe.Checkout.Session;
        await handleCheckoutComplete(session);
        break;
      }

      case "customer.subscription.updated": {
        const subscription = event.data.object as Stripe.Subscription;
        await handleSubscriptionUpdated(subscription);
        break;
      }

      case "customer.subscription.deleted": {
        const subscription = event.data.object as Stripe.Subscription;
        await handleSubscriptionDeleted(subscription);
        break;
      }

      case "invoice.payment_succeeded": {
        const invoice = event.data.object as Stripe.Invoice;
        await handlePaymentSucceeded(invoice);
        break;
      }

      case "invoice.payment_failed": {
        const invoice = event.data.object as Stripe.Invoice;
        await handlePaymentFailed(invoice);
        break;
      }

      default:
        console.info(
          JSON.stringify({
            severity: "INFO",
            message: "stripe_webhook_unhandled",
            event_type: event.type,
          })
        );
    }

    return NextResponse.json({ received: true }, { status: 200 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    console.error(
      JSON.stringify({
        severity: "ERROR",
        message: "stripe_webhook_handler_error",
        event_id: event.id,
        event_type: event.type,
        error: message,
      })
    );
    // Return 200 to prevent Stripe retries on app-level errors
    // The error is logged for investigation
    return NextResponse.json({ received: true }, { status: 200 });
  }
}

// ───────────────────────────────────────────────
// Handler implementations
// ───────────────────────────────────────────────

async function handleCheckoutComplete(session: Stripe.Checkout.Session) {
  const tier = session.metadata?.tier || "unknown";
  const customerEmail = session.customer_details?.email || "unknown";
  const customerId = session.customer as string;
  const subscriptionId = session.subscription as string;

  console.info(
    JSON.stringify({
      severity: "INFO",
      message: "new_subscription_created",
      tier,
      customer_email: customerEmail,
      customer_id: customerId,
      subscription_id: subscriptionId,
    })
  );

  // TODO: Create tenant record in Firestore
  // TODO: Send welcome email via Google Workspace API
  // TODO: Provision Cloud Run namespace for firm
}

async function handleSubscriptionUpdated(subscription: Stripe.Subscription) {
  const status = subscription.status;
  const tier = subscription.metadata?.tier || "unknown";

  console.info(
    JSON.stringify({
      severity: "INFO",
      message: "subscription_updated",
      subscription_id: subscription.id,
      status,
      tier,
      cancel_at_period_end: subscription.cancel_at_period_end,
    })
  );

  // TODO: Update Firestore tenant record with new plan/status
  // TODO: If upgraded, provision additional resources
  // TODO: If downgraded, schedule resource cleanup via Cloud Tasks
}

async function handleSubscriptionDeleted(subscription: Stripe.Subscription) {
  const tier = subscription.metadata?.tier || "unknown";

  console.info(
    JSON.stringify({
      severity: "WARNING",
      message: "subscription_cancelled",
      subscription_id: subscription.id,
      tier,
    })
  );

  // TODO: Mark tenant as cancelled in Firestore
  // TODO: Schedule GDPR 30-day deletion via Cloud Tasks queue
  // TODO: Send retention email
}

async function handlePaymentSucceeded(invoice: Stripe.Invoice) {
  console.info(
    JSON.stringify({
      severity: "INFO",
      message: "payment_succeeded",
      invoice_id: invoice.id,
      customer_id: invoice.customer as string,
      amount_paid: invoice.amount_paid,
      currency: invoice.currency,
    })
  );

  // TODO: Update billing record in Firestore
  // TODO: Send receipt via Google Workspace API
}

async function handlePaymentFailed(invoice: Stripe.Invoice) {
  console.error(
    JSON.stringify({
      severity: "ERROR",
      message: "payment_failed",
      invoice_id: invoice.id,
      customer_id: invoice.customer as string,
      amount_due: invoice.amount_due,
      attempt_count: invoice.attempt_count,
      next_payment_attempt: invoice.next_payment_attempt,
    })
  );

  // TODO: Send payment failure notification via Google Workspace
  // TODO: If attempt_count >= 3, flag for manual review
  // TODO: Create alert in Google Workspace Chat
}
