import { NextResponse } from 'next/server';
import { SecretManagerServiceClient } from '@google-cloud/secret-manager';
import Stripe from 'stripe';

// 1. INITIALIZE THE VAULT CLIENT
// We instantiate this outside the handler to leverage "Cold Start" caching in Cloud Run.
const secretsClient = new SecretManagerServiceClient();

/**
 * ACCESS_VAULT: Retrieves the Stripe Secret Key securely.
 * This function only works if the Cloud Run Service Account has 
 * 'Secret Manager Secret Accessor' permission.
 */
async function getStripeKey() {
  // The Resource Name: projects/{id}/secrets/{name}/versions/{version}
  const name = `projects/${process.env.GCP_PROJECT_ID}/secrets/STRIPE_SECRET_KEY/versions/latest`;

  try {
    const [version] = await secretsClient.accessSecretVersion({ name });
    
    // Decode the payload (it comes as a Buffer)
    const payload = version.payload?.data?.toString();
    
    if (!payload) throw new Error("VAULT_EMPTY: Secret payload is null.");
    return payload;
    
  } catch (error) {
    console.error("🚨 SECURITY ALERT: Failed to access Vault.", error);
    // In "Deep Think" mode, we fail closed. 
    // We do not fallback to env vars.
    throw error; 
  }
}

export async function POST(req: Request) {
  try {
    console.log("> ORCHESTRATOR: INITIATING COMMERCIAL HANDSHAKE...");

    // 2. JUST-IN-TIME KEY FETCH
    // The key exists in memory ONLY for the duration of this request.
    const secretKey = await getStripeKey();
    
    // Initialize Stripe with the secure key
    const stripe = new Stripe(secretKey, {
      apiVersion: '2023-10-16', // Pin the API version for stability
    });

    // 3. DEFINE THE COMMERCIAL TERMS
    // In a real scenario, you might pass a 'priceId' from the frontend,
    // but hardcoding the "Sovereign Tier" here prevents price tampering.
    const PRICE_ID = 'price_ultra_credits_100'; // Hardcoded for Demo

    // 4. CREATE THE SESSION
    const session = await stripe.checkout.sessions.create({
      line_items: [
        {
          price: PRICE_ID,
          quantity: 1,
        },
      ],
      mode: 'payment',
      // The "Gucci" Return URLs
      success_url: `${process.env.NEXT_PUBLIC_DOMAIN}/dashboard?status=reactor_online`,
      cancel_url: `${process.env.NEXT_PUBLIC_DOMAIN}/`,
      
      // 5. METADATA FORENSICS
      // This data appears in your Stripe Dashboard. It proves provenance.
      metadata: {
        architecture: 'sovereign_v1',
        origin: 'cloud_run_reactor',
        compliance: 'strict_act_as',
        environment: process.env.NODE_ENV
      },
      
      // Customize the Stripe hosted page to match the "Void" aesthetic
      allow_promotion_codes: true,
    });

    console.log(`> HANDSHAKE_COMPLETE: Session ${session.id} created.`);
    
    return NextResponse.json({ id: session.id });

  } catch (err: any) {
    console.error("REACTOR_IGNITION_FAILED:", err);
    
    // Obscure the actual error from the client to prevent info leakage
    return NextResponse.json(
      { error: "SYSTEM_HALTED: Ignition Sequence Aborted." }, 
      { status: 500 }
    );
  }
}
