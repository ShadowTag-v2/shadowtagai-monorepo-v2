/**
 * V18 Zenith — Unified Kriasoft Bun Backend
 * Isomorphic GraphQL Gateway running on Hono v4 + Bun.serve()
 *
 * Routes:
 *   /graphql       — Unified GraphQL API (Kriasoft graphql-starter-kit pattern)
 *   /webhook/stripe — Stripe webhook with raw body signature verification
 *   /intake/tabular — SheetJS spreadsheet ingestion + Gemini RAG embedding
 *   /health        — Cloud Run health probe
 *
 * Runtime: Bun 1.3.11 (Zig-backed)
 * Pattern: Kriasoft Isomorphic Monorepo (graphql-starter-kit + react-firebase-starter)
 */

import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { logger } from 'hono/logger';

const app = new Hono();

// Middleware
app.use('*', logger());
app.use('*', cors({
  origin: [
    'https://counselconduit-767252945109.us-central1.run.app',
    'https://headfade.com',
    'http://localhost:3000',
  ],
  allowMethods: ['GET', 'POST', 'OPTIONS'],
  allowHeaders: ['Content-Type', 'Authorization', 'stripe-signature'],
}));

// ─── Health Probe (Cloud Run) ─────────────────────────────────────
app.get('/health', (c) => c.json({
  status: 'OK',
  version: 'V18-Zenith',
  runtime: 'Bun ' + Bun.version,
  timestamp: new Date().toISOString(),
}));

// ─── GraphQL Endpoint (Kriasoft Pattern) ──────────────────────────
// Dynamic import to avoid blocking server start if graphql isn't installed yet
app.post('/graphql', async (c) => {
  try {
    const { buildSchema, graphql } = await import('graphql');

    const schema = buildSchema(`
      type Query {
        systemStatus: String!
        userAccess(firebaseUid: String!): Boolean!
        serviceHealth: ServiceHealth!
      }

      type ServiceHealth {
        api: Boolean!
        graphql: Boolean!
        stripe: Boolean!
        spanner: Boolean!
      }
    `);

    const rootValue = {
      systemStatus: () => 'V18 Federated GraphQL Gateway Online — Bun ' + Bun.version,
      userAccess: async ({ firebaseUid }: { firebaseUid: string }) => {
        // TODO: Wire to Spanner when core-cluster is provisioned
        // const { Spanner } = await import('@google-cloud/spanner');
        // const db = new Spanner().instance('core-cluster').database('shadowtag-omega-v4');
        // const [rows] = await db.run({ sql: `SELECT status FROM transactions WHERE user_id = @uid AND status = 'PAID'`, params: { uid: firebaseUid } });
        // return rows.length > 0;
        console.log(`[GraphQL] Access check for UID: ${firebaseUid}`);
        return true; // Default allow until Spanner is live
      },
      serviceHealth: () => ({
        api: true,
        graphql: true,
        stripe: !!process.env.STRIPE_SECRET_KEY,
        spanner: false, // Will be true when core-cluster is provisioned
      }),
    };

    const body = await c.req.json();
    const result = await graphql({ schema, source: body.query, rootValue, variableValues: body.variables });
    return c.json(result);
  } catch (err) {
    console.error('[GraphQL] Schema error:', err);
    return c.json({ errors: [{ message: 'GraphQL engine not available' }] }, 500);
  }
});

// ─── Stripe Webhook (Raw Body Signature Verification) ─────────────
app.post('/webhook/stripe', async (c) => {
  const signature = c.req.header('stripe-signature');
  if (!signature) {
    return c.json({ error: 'Missing stripe-signature header' }, 400);
  }

  const payload = await c.req.text();

  try {
    const Stripe = (await import('stripe')).default;
    const stripe = new Stripe(process.env.STRIPE_SECRET_KEY as string, {
      apiVersion: '2024-12-18.acacia',
    });

    const event = stripe.webhooks.constructEvent(
      payload,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!,
    );

    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object as Record<string, unknown>;
        console.log(`⚡ [Stripe] Payment completed: ${session.client_reference_id} → ${session.customer}`);
        // TODO: Insert into Spanner when provisioned
        // await database.table('transactions').insert({
        //   user_id: session.client_reference_id,
        //   stripe_customer_id: session.customer,
        //   status: 'PAID',
        //   timestamp: Spanner.commitTimestamp()
        // });
        break;
      }
      case 'customer.subscription.updated':
      case 'customer.subscription.deleted': {
        console.log(`⚡ [Stripe] Subscription event: ${event.type}`);
        break;
      }
      default:
        console.log(`[Stripe] Unhandled event type: ${event.type}`);
    }

    return c.text('OK');
  } catch (err) {
    console.error('[Stripe] Webhook verification failed:', err);
    return c.json({ error: 'Webhook verification failed' }, 400);
  }
});

// ─── SheetJS Tabular Intake + Epistemic RAG ───────────────────────
app.post('/intake/tabular', async (c) => {
  try {
    const body = await c.req.json();
    const docName = body.document_title || body.message?.attributes?.document_title || 'Unknown_Payload';
    const rawData = body.data || body.message?.data;

    if (!rawData) {
      return c.json({ error: 'Missing data field' }, 400);
    }

    const { read, utils } = await import('xlsx');

    let processableText: string;

    if (docName.endsWith('.xlsx') || docName.endsWith('.xls')) {
      const workbook = read(Buffer.from(rawData, 'base64'), { type: 'buffer' });
      const firstSheetName = workbook.SheetNames[0];
      processableText = utils.sheet_to_csv(workbook.Sheets[firstSheetName]);
    } else {
      processableText = Buffer.from(rawData, 'base64').toString('utf-8');
    }

    const tmpPath = `/tmp/${docName}.txt`;
    await Bun.write(tmpPath, processableText);

    // Gemini File API for RAG embedding
    try {
      const { GoogleGenAI } = await import('@google/genai');
      const ai = new GoogleGenAI({});
      await ai.files.upload({
        file: tmpPath,
        config: { displayName: docName, customMetadata: { type: 'epistemic_rag' } },
      });
      console.log(`⚡ [SheetJS] Embedded ${docName} via Gemini File API`);
    } catch (aiErr) {
      console.warn(`[SheetJS] Gemini upload skipped (not configured):`, aiErr);
    }

    return c.json({
      status: 'ingested',
      document: docName,
      rows: processableText.split('\n').length,
      runtime: 'Bun ' + Bun.version,
    });
  } catch (err) {
    console.error('[SheetJS] Intake error:', err);
    return c.json({ error: 'Tabular intake failed' }, 500);
  }
});

// ─── Catch-all 404 ────────────────────────────────────────────────
app.notFound((c) => c.json({
  error: 'Not Found',
  availableRoutes: ['/health', '/graphql', '/webhook/stripe', '/intake/tabular'],
}, 404));

// ─── Error Handler ────────────────────────────────────────────────
app.onError((err, c) => {
  console.error('[Server] Unhandled error:', err);
  return c.json({ error: 'Internal Server Error' }, 500);
});

// ─── Bun.serve() ─────────────────────────────────────────────────
const port = parseInt(process.env.PORT || '8080', 10);

console.log(`⚡ V18 Zenith — Kriasoft Bun API + GraphQL Gateway`);
console.log(`⚡ Runtime: Bun ${Bun.version} | Port: ${port}`);
console.log(`⚡ Routes: /health /graphql /webhook/stripe /intake/tabular`);

export default {
  port,
  fetch: app.fetch,
};
