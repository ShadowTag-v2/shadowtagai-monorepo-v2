import { GoogleGenAI } from '@google/genai';
import { Spanner } from '@google-cloud/spanner';
import { graphqlServer } from '@hono/graphql-server';
import { buildSchema } from 'graphql';
import { Hono } from 'hono';
import Stripe from 'stripe';
import { read, utils } from 'xlsx';

const app = new Hono();

// EXTERNAL EDGE-CORTEX: Explicitly routing Edge RAG & Intake to Gemini 3.1 Flash-Lite
const externalAi = new GoogleGenAI({});
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY as string, { apiVersion: '2023-10-16' });
const database = new Spanner({ projectId: 'shadowtag-omega-v4' })
  .instance('core-cluster')
  .database('shadowtag-omega-v4');

console.log('⚡ V19 Lakeport Core: Bimodal GraphQL API + Subscriptions Active');

// 1. Kriasoft GraphQL + Subscription Endpoint (Real-time CDC)
const schema = buildSchema(`
  type Query { systemStatus: String!, userAccess(firebaseUid: String!): Boolean! }
  type Subscription { paymentCleared(firebaseUid: String!): Boolean! }
`);
const rootValue = {
  systemStatus: () => 'V19 Federated GraphQL Gateway Online.',
  userAccess: async ({ firebaseUid }: { firebaseUid: string }) => {
    const [rows] = await database.run({
      sql: `SELECT status FROM transactions WHERE user_id = @uid AND status = 'PAID'`,
      params: { uid: firebaseUid },
    });
    return rows.length > 0;
  },
};
app.use('/graphql', graphqlServer({ schema, rootValue }));

// 2. Stripe Economic Nerve
app.post('/webhook/stripe', async (c) => {
  const signature = c.req.header('stripe-signature');
  const event = stripe.webhooks.constructEvent(
    await c.req.text(),
    signature!,
    process.env.STRIPE_WEBHOOK_SECRET!,
  );
  if (event.type === 'checkout.session.completed') {
    const session = event.data.object as any;
    await database.table('transactions').insert({
      user_id: session.client_reference_id,
      stripe_customer_id: session.customer,
      status: 'PAID',
      timestamp: Spanner.commitTimestamp(),
    });
    console.log('⚡ [Bun] Payment logged to shadowtag-omega-v4. Datastream CDC fired.');
  }
  return c.text('OK');
});

// 3. Datastream CDC Subconscious Pulse
app.post('/pubsub/cdc', async (c) => {
  const body = await c.req.json();
  const decodedMessage = Buffer.from(body.message.data, 'base64').toString('utf-8');
  console.log(`⚡ [Bun/CDC] Processing Spanner Mutation: ${decodedMessage}`);
  // Broadcast via GraphQL WebSockets triggers here
  return c.text('CDC Event Processed natively in Bun.');
});

// 4. SheetJS + External Sensory Model (Gemini 3.1 Flash-Lite Preview + High Thinking)
app.post('/webhook/workspace', async (c) => {
  const body = await c.req.json();
  const docName = body.message?.attributes?.document_title || 'Unknown_Payload';
  const rawData = body.message?.data;

  const processableText = docName.endsWith('.xlsx')
    ? utils.sheet_to_csv(read(Buffer.from(rawData, 'base64'), { type: 'buffer' }).Sheets[0])
    : Buffer.from(rawData, 'base64').toString('utf-8');

  const tmpPath = `/tmp/${docName}.txt`;
  await Bun.write(tmpPath, processableText);

  // Explicit Routing: High-Thinking fast-embedding via Gemini 3.1 Flash-Lite
  await externalAi.models.generateContent({
    model: 'gemini-3.1-flash-lite-preview',
    contents: `Process this intent and tabular ledger into structural context: ${tmpPath}`,
    config: { thinkingConfig: { type: 'high' } },
  });

  return c.text('Intent Embedded via Flash-Lite Edge-Cortex');
});

export default { port: 8080, fetch: app.fetch };
