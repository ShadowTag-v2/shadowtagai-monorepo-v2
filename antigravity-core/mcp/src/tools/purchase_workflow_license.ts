import { executeGrantLicenseMutation } from "../utils/firebase-data-connect.js";
import Stripe from "stripe";
import { Storage } from "@google-cloud/storage";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2026-04-22.dahlia"
});

const storage = new Storage();
const BUCKET_NAME = process.env.WORKFLOW_BUCKET_NAME || "shadowtag-workflows";

export async function purchaseWorkflowLicense(
  videoId: string,
  agentWalletToken: string,
  authToken: string
) {
  try {
    // 1. Validate agent payment token (simplified for demo)
    if (!agentWalletToken.startsWith("agnt_")) {
      return {
        content: [{ type: "text" as const, text: "Transaction Failed: Invalid agent wallet token." }]
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
        content: [{ type: "text" as const, text: "Payment Failed. Insufficient agent funds." }]
      };
    }

    // 3. Grant license in Cloud SQL via Data Connect
    await executeGrantLicenseMutation({
      buyerId: agentWalletToken,
      videoId
    });

    // 4. Return workflow data (in production: signed GCS URL)
    const options = {
      version: 'v4' as const,
      action: 'read' as const,
      expires: Date.now() + 15 * 60 * 1000, // 15 minutes
    };

    let url = "";
    try {
      const [signedUrl] = await storage
        .bucket(BUCKET_NAME)
        .file(`${videoId}.json`)
        .getSignedUrl(options);
      url = signedUrl;
    } catch (e) {
      console.warn("Failed to sign GCS URL (likely local dev without service account). Using mock URL.");
      url = `https://storage.googleapis.com/${BUCKET_NAME}/${videoId}.json?mock=true`;
    }

    return {
      content: [{
        type: "text" as const,
        text: `License Granted. Workflow data unlocked for agent ${agentWalletToken}. Access URL: ${url}`
      }]
    };
  } catch (error) {
    return {
      content: [{ type: "text" as const, text: `A2A Purchase Error: ${error instanceof Error ? error.message : "Unknown"}` }]
    };
  }
}