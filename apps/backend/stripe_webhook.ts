#!/usr/bin/env bun
import { Spanner } from '@google-cloud/spanner';
/**
 * apps/backend/stripe_webhook.ts — V25 Financial Governor
 *
 * Closes the capital circuit: Stripe → Spanner → Datastream → BigQuery ROI.
 * Listens for checkout.session.completed events and writes transactions
 * to the Spanner ledger for CDC propagation.
 *
 * Env required:
 *   STRIPE_SECRET_KEY (from GCP Secret Manager via scripts/load_mcp_secrets.sh)
 *   STRIPE_WEBHOOK_SECRET (from GCP Secret Manager)
 */
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
});

const spanner = new Spanner({ projectId: 'shadowtag-omega-v4' });
const database = spanner.instance('core-cluster').database('primary-db');

console.log('💰 V25 Financial Governor Active on port 8081');

Bun.serve({
  port: 8081,
  async fetch(req) {
    if (req.method === 'POST' && new URL(req.url).pathname === '/stripe-webhook') {
      const sig = req.headers.get('stripe-signature');
      if (!sig) {
        return new Response('Missing signature', { status: 400 });
      }

      try {
        const body = await req.text();
        const event = stripe.webhooks.constructEvent(body, sig, process.env.STRIPE_WEBHOOK_SECRET!);

        if (event.type === 'checkout.session.completed') {
          const session = event.data.object as Stripe.Checkout.Session;
          const siteId = session.metadata?.site_id || 'unknown';
          const userId = session.client_reference_id || 'anonymous';

          console.log(
            `[CAPITAL INGESTION] Revenue: ${session.amount_total} | Site: ${siteId} | User: ${userId}`,
          );

          await database.table('transactions').insert([
            {
              id: session.id,
              user_id: userId,
              revenue: session.amount_total,
              target_site: siteId,
              stripe_customer_id: session.customer as string,
              status: 'PAID',
              timestamp: Spanner.commitTimestamp(),
            },
          ]);

          console.log('✅ Transaction committed to Spanner. Datastream CDC will fire.');
        }

        return new Response('Ledger Updated', { status: 200 });
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : 'Unknown error';
        console.error(`❌ Webhook Error: ${message}`);
        return new Response(`Webhook Error: ${message}`, { status: 400 });
      }
    }

    // Health check
    if (req.method === 'GET' && new URL(req.url).pathname === '/health') {
      return Response.json({ status: 'V25 Financial Governor Online', port: 8081 });
    }

    return new Response('Not Found', { status: 404 });
  },
});
