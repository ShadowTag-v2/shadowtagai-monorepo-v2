import { NextResponse } from "next/server";
import Stripe from "stripe";
import { createClient } from "@supabase/supabase-js";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || "sk_test_placeholder", {
  apiVersion: "2025-02-24.acacia",
});

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL || "https://placeholder.supabase.co",
  process.env.SUPABASE_SERVICE_ROLE_KEY || "placeholder",
);

export async function POST(req: Request) {
  const body = await req.text();
  const signature = req.headers.get("stripe-signature");

  if (!signature) {
    return NextResponse.json({ error: "Missing Stripe signature" }, { status: 400 });
  }

  try {
    const event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET || "whsec_placeholder",
    );

    if (event.type === "checkout.session.completed") {
      const session = event.data.object as Stripe.Checkout.Session;
      const userId = session.client_reference_id;
      const amountPaid = session.amount_total;

      if (!userId) {
        throw new Error("No client_reference_id found. Cannot credit user.");
      }

      // Convert cents to credits multiplier. Example: $10 = 100 credits.
      const creditsToAdd = (amountPaid || 0) / 10;

      // Deterministic Ledger update (RPC call to avoid race conditions)
      const { error } = await supabase.rpc("increment_credits", {
        user_id: userId,
        amount: creditsToAdd,
      });

      if (error) {
        console.error("Core DB Ledger Failure:", error);
        return NextResponse.json({ error: "Database transaction failed." }, { status: 500 });
      }
    }

    return NextResponse.json({ received: true }, { status: 200 });
  } catch (error: unknown) {
    console.error("Webhook Error:", error.message);
    return NextResponse.json({ error: `Webhook Handler Error: ${error.message}` }, { status: 400 });
  }
}
