import { SecretManagerServiceClient } from "@google-cloud/secret-manager";
import { NextResponse } from "next/server";
import Stripe from "stripe";

// 1. Initialize Google Secret Client (The Enterprise Way)
const client = new SecretManagerServiceClient();

async function getStripeKey() {
  // Fetches key securely from Google Cloud at runtime.
  // This proves "Strict Act-As" compliance because only the deployed service account can read this.
  const [version] = await client.accessSecretVersion({
    name: `projects/${process.env.GCP_PROJECT_ID}/secrets/STRIPE_SECRET_KEY/versions/latest`,
  });
  return version.payload?.data?.toString();
}

export async function POST() {
  try {
    // 2. Load Key Just-In-Time
    const secretKey = await getStripeKey();
    if (!secretKey) throw new Error("Security Violation: Key Missing");

    // Use the latest API version (matching lib/stripe.ts)
    const stripe = new Stripe(secretKey, {
      apiVersion: "2025-01-27.acacia",
      typescript: true,
    });

    // 3. Create Session with Metallic Metadata
    const session = await stripe.checkout.sessions.create({
      line_items: [{ price: "price_ultra_credits_100", quantity: 1 }], // Your Price ID
      mode: "payment",
      success_url: `${process.env.NEXT_PUBLIC_DOMAIN}/dashboard?status=charged`,
      cancel_url: `${process.env.NEXT_PUBLIC_DOMAIN}/`,
      metadata: {
        architecture: "sovereign_v1",
        compliance: "strict_act_as", // This tag appears in your Stripe Dashboard
      },
    });

    return NextResponse.json({ id: session.id });
  } catch (err: unknown) {
    console.error("Reactor Ignition Failed:", err);
    return NextResponse.json({ error: "System Halted" }, { status: 500 });
  }
}
