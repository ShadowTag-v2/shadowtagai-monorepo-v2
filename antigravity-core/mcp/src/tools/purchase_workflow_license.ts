import { executeGrantLicenseMutation } from "../utils/firebase-data-connect.js";
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2025-02-24.acacia"
});

export async function purchaseWorkflowLicense(
  videoId: string,
  agentWalletToken: string,
  authToken: string
) {
  try {
    if (!agentWalletToken.startsWith("agnt_")) {
      return {
        content: [{ type: "text", text: "Transaction Failed: Invalid agent wallet token." }]
      };
    }

    const paymentIntent = await stripe.paymentIntents.create({
      amount: 299,
      currency: "usd",
      payment_method: "pm_card_visa",
      confirm: true,
      metadata: { videoId, agentWalletToken }
    });

    if (paymentIntent.status !== "succeeded") {
      return {
        content: [{ type: "text", text: "Payment Failed. Insufficient agent funds." }]
      };
    }

    await executeGrantLicenseMutation({
      buyerId: agentWalletToken,
      videoId
    });

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
