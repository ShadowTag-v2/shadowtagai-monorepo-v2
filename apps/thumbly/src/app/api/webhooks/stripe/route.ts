import { createClient } from '@supabase/supabase-js';
import { NextResponse } from 'next/server';
import Stripe from 'stripe';

if (!process.env.STRIPE_SECRET_KEY) {
  throw new Error('STRIPE_SECRET_KEY environment variable is required');
}

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
  apiVersion: '2025-02-24.acacia',
});

if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.SUPABASE_SERVICE_ROLE_KEY) {
  throw new Error('Supabase environment variables are required');
}

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY,
);

export async function POST(req: Request) {
  const body = await req.text();
  const signature = req.headers.get('stripe-signature');

  if (!signature) {
    return NextResponse.json({ error: 'Missing Stripe signature' }, { status: 400 });
  }

  try {
    if (!process.env.STRIPE_WEBHOOK_SECRET) {
      return NextResponse.json({ error: 'Missing webhook secret configuration' }, { status: 500 });
    }

    const event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET,
    );

    if (event.type === 'checkout.session.completed') {
      const session = event.data.object as Stripe.Checkout.Session;
      const userId = session.client_reference_id;
      const amountPaid = session.amount_total;

      if (!userId) {
        throw new Error('No client_reference_id found. Cannot credit user.');
      }

      // Convert cents to credits multiplier. Example: $10 = 100 credits.
      const creditsToAdd = (amountPaid || 0) / 10;

      // Deterministic Ledger update (RPC call to avoid race conditions)
      const { error } = await supabase.rpc('increment_credits', {
        user_id: userId,
        amount: creditsToAdd,
      });

      if (error) {
        return NextResponse.json({ error: 'Database transaction failed.' }, { status: 500 });
      }
    }

    return NextResponse.json({ received: true }, { status: 200 });
  } catch (error: unknown) {
    return NextResponse.json({ error: `Webhook Handler Error: ${error.message}` }, { status: 400 });
  }
}
