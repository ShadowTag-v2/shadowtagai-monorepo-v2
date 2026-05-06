import { NextApiRequest, NextApiResponse } from 'next';
import Stripe from 'stripe';
import { executeGrantLicenseMutation } from '../utils/firebase-data-connect.js';

// @ts-ignore
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2026-04-22.dahlia' as any
});

const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET!;

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).end();
  }

  const sig = req.headers['stripe-signature'] as string;
  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(req.body, sig, endpointSecret);
  } catch (err) {
    console.error('Webhook signature verification failed:', err);
    return res.status(400).send('Webhook Error');
  }

  if (event.type === 'payment_intent.succeeded') {
    const paymentIntent = event.data.object as Stripe.PaymentIntent;
    const { videoId, agentWalletToken } = paymentIntent.metadata;

    if (videoId && agentWalletToken) {
      try {
        await executeGrantLicenseMutation({
          buyerId: agentWalletToken,
          videoId
        });

        console.log(`✅ A2A License granted via webhook: ${agentWalletToken} → ${videoId}`);
      } catch (error) {
        console.error('Failed to grant license after payment:', error);
      }
    }
  }

  res.status(200).json({ received: true });
}