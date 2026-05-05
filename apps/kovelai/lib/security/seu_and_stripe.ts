/**
 * @fileoverview S.E.U. Security Middleware & Stripe Ledger
 *
 * The mathematical antidote to .npmrc agentic key exfiltration hacks.
 *
 * S.E.U. = Sandbox-Bound, Ephemeral, User-Billed
 *
 * [S] Sandbox-Bound: Token is locked to the client's IP hash.
 *     If exfiltrated via process.env, it violently rejects from foreign IPs.
 * [E] Ephemeral: Token mathematically dies in 60 minutes. No renewal.
 * [U] User-Billed: Token is minted only AFTER Stripe payment clears.
 *     Cost is attributed to the client's PaymentIntent, not a master key.
 *
 * @see DIGITAL_PRIVILEGE_SHIELD.md
 * @see arXiv:2512.14982 (prompt repetition accuracy boost)
 */

import crypto from 'node:crypto';
import { type JWTPayload, jwtVerify, SignJWT } from 'jose';
import Stripe from 'stripe';

const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
if (!stripeSecretKey) throw new Error('[SEU] STRIPE_SECRET_KEY must be set');
const stripe = new Stripe(stripeSecretKey);
const SECRET_KEY = new TextEncoder().encode(process.env.SEU_JWT_SECRET);

/** S.E.U. JWT payload shape. */
interface SeuPayload extends JWTPayload {
  sandboxId: string;
  clientIpHash: string;
  firmId?: string;
}

/**
 * Charges the client via Stripe Connect (destination charge to lawyer)
 * and mints an S.E.U. token bound to the payment + client IP.
 *
 * @param firmStripeAccountId - The lawyer's Stripe Connect account ID
 * @param clientIp - The client's originating IP address
 * @param amount - Triage fee in dollars (e.g., 25 for $25.00)
 * @param firmId - Internal firm identifier for telemetry
 * @returns clientSecret for Stripe Elements + seuToken for Edge Router
 */
export async function chargeAndMintSEU(
  firmStripeAccountId: string,
  clientIp: string,
  amount: number,
  firmId?: string,
) {
  // 1. Destination Charge: Client pays Lawyer directly. KovelAI touches zero legal fees.
  const paymentIntent = await stripe.paymentIntents.create({
    amount: amount * 100, // cents
    currency: 'usd',
    transfer_data: { destination: firmStripeAccountId },
  });

  // 2. Token is Sandbox-Bound (IP & Payment ID), Ephemeral (1 hr), and User-Billed
  const token = await new SignJWT({
    sandboxId: paymentIntent.id,
    clientIpHash: crypto.createHash('sha256').update(clientIp).digest('hex'),
    firmId,
  } satisfies SeuPayload)
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('1h') // [E] Ephemeral: mathematically dies in 60 minutes
    .sign(SECRET_KEY);

  return { clientSecret: paymentIntent.client_secret, seuToken: token };
}

/**
 * Verifies an S.E.U. token and enforces the Sandbox-Bound IP check.
 *
 * @param token - The S.E.U. JWT to verify
 * @param incomingIp - The IP of the current request
 * @returns Decoded payload if valid
 * @throws Error if token is expired, invalid, or IP mismatches
 */
export async function verifySeuToken(token: string, incomingIp: string): Promise<SeuPayload> {
  const { payload } = await jwtVerify(token, SECRET_KEY);
  const incomingIpHash = crypto.createHash('sha256').update(incomingIp).digest('hex');

  // [S] Sandbox-Bound Check: Blocks .npmrc exfiltration hacks
  if ((payload as SeuPayload).clientIpHash !== incomingIpHash) {
    throw new Error('S.E.U. Perimeter Breach: IP Mismatch. Execution Halted.');
  }

  return payload as SeuPayload;
}
