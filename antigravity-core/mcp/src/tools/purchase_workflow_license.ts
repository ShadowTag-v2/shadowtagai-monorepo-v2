import { executeGrantLicenseMutation } from "../utils/firebase-data-connect.js";
import Stripe from "stripe";

// @ts-ignore
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2026-04-22.dahlia" as any
});

export async function purchaseWorkflowLicense(
  videoId: string,
  agentWalletToken: string,
  authToken: string
) {
  try {
    // 1. Validate agent payment token (simplified for demo)
    if (!agentWalletToken.startsWith("agnt_")) {
      return {
        content: [{ type: "text", text: "Transaction Failed: Invalid agent wallet token." }]
      };
    }

    // 2. Create Stripe micro-charge ($2.99)
    const paymentIntent = await stripe.paymentIntents.create({
      amount: 299,
      currency: "usd",
      payment_method: "pm_card_visa", // In production: use agent-linked method
      confirm: true,
      metadata: { videoId, agentWalletToken }
    });

    if (paymentIntent.status !== "succeeded") {
      return {
        content: [{ type: "text", text: "Payment Failed. Insufficient agent funds." }]
      };
    }

    // 3. Grant license in Cloud SQL via Data Connect
    await executeGrantLicenseMutation({
      buyerId: agentWalletToken,
      videoId
    });

    // 4. Return workflow data (in production: signed GCS URL)
    return {
      content: [{
        type: "text",
        text: `License Granted. Workflow data unlocked for agent ${agentWalletToken}.`
      }]
    };
  } catch (error) {
    return {
      content: [{ type: "text", text: `A2A Purchase Error: ${error instanceof Error ? error.message : "Unknown"}` }]
    };
  }
}