/**
 * Triple-Site GraphQL Nexus — V25 Pinnacle
 * Feature flag and site config API backed by Spanner.
 * Serves the HeadFade, CounselConduit, and KovelAI/ShadowTagAI fleet.
 *
 * Supports:
 * - HTTP POST for queries and mutations
 * - WebSocket (graphql-ws protocol) for subscriptions via AsyncIterator
 */

import { Spanner } from '@google-cloud/spanner';
import type { ServerWebSocket } from 'bun';
import { EventEmitter } from 'events';
import { buildSchema, type ExecutionResult, graphql, parse, subscribe } from 'graphql';

// ──────────────────────────────────────────────────────────────
// PubSub — in-memory AsyncIterator-backed event bus
// ──────────────────────────────────────────────────────────────
class PubSub {
  private emitter = new EventEmitter();

  publish(event: string, payload: unknown): void {
    this.emitter.emit(event, payload);
  }

  asyncIterator<T = unknown>(event: string): AsyncIterableIterator<T> {
    const emitter = this.emitter;
    const pullQueue: Array<(value: IteratorResult<T>) => void> = [];
    const pushQueue: T[] = [];
    let done = false;

    const handler = (value: T) => {
      if (pullQueue.length > 0) {
        pullQueue.shift()!({ value, done: false });
      } else {
        pushQueue.push(value);
      }
    };

    emitter.on(event, handler);

    return {
      next(): Promise<IteratorResult<T>> {
        if (done) return Promise.resolve({ value: undefined as unknown as T, done: true });
        if (pushQueue.length > 0) {
          return Promise.resolve({ value: pushQueue.shift()!, done: false });
        }
        return new Promise((resolve) => pullQueue.push(resolve));
      },
      return(): Promise<IteratorResult<T>> {
        done = true;
        emitter.removeListener(event, handler);
        for (const resolve of pullQueue) {
          resolve({ value: undefined as unknown as T, done: true });
        }
        pullQueue.length = 0;
        pushQueue.length = 0;
        return Promise.resolve({ value: undefined as unknown as T, done: true });
      },
      throw(err: Error): Promise<IteratorResult<T>> {
        done = true;
        emitter.removeListener(event, handler);
        return Promise.reject(err);
      },
      [Symbol.asyncIterator]() {
        return this;
      },
    };
  }
}

const pubsub = new PubSub();

// Subscription event channels
const EVENTS = {
  FLAG_CHANGED: 'FLAG_CHANGED',
  TRANSACTION_CREATED: 'TRANSACTION_CREATED',
} as const;

// ──────────────────────────────────────────────────────────────
// Spanner connection
// ──────────────────────────────────────────────────────────────
const PROJECT_ID = process.env.GOOGLE_CLOUD_PROJECT || 'shadowtag-omega-v4';
const INSTANCE_ID = process.env.SPANNER_INSTANCE || 'uphill-core-cluster';
const DATABASE_ID = process.env.SPANNER_DATABASE || 'uphill-ledger';

const spanner = new Spanner({ projectId: PROJECT_ID });
const database = spanner.instance(INSTANCE_ID).database(DATABASE_ID);

// ──────────────────────────────────────────────────────────────
// Schema — Queries + Mutations + Subscriptions
// ──────────────────────────────────────────────────────────────
const schema = buildSchema(`
  type FeatureFlag {
    id: ID!
    site_id: String!
    feature_name: String!
    is_active: Boolean!
  }

  type SiteConfig {
    site_id: ID!
    display_name: String!
    url: String!
    lighthouse_target: Int!
  }

  type Transaction {
    id: ID!
    revenue: Int!
    ui_variant_id: String!
    timestamp: String!
  }

  type Query {
    getFlags(site_id: String!): [FeatureFlag]
    getSiteConfig(site_id: String!): SiteConfig
    getRecentTransactions(limit: Int): [Transaction]
  }

  type Mutation {
    updateFlag(id: ID!, site_id: String!, feature_name: String!, is_active: Boolean!): FeatureFlag
    createTransaction(id: ID!, revenue: Int!, ui_variant_id: String!): Transaction
  }

  type Subscription {
    flagChanged(site_id: String!): FeatureFlag
    transactionCreated: Transaction
  }
`);

// ──────────────────────────────────────────────────────────────
// Resolvers
// ──────────────────────────────────────────────────────────────
const rootValue = {
  // ── Queries ──
  getFlags: async ({ site_id }: { site_id: string }) => {
    try {
      const [rows] = await database.run({
        sql: 'SELECT id, site_id, feature_name, is_active FROM feature_flags WHERE site_id = @siteId',
        params: { siteId: site_id },
      });
      return rows.map((row) => row.toJSON());
    } catch (err) {
      console.error('[GraphQL] getFlags error:', err);
      return [];
    }
  },

  getSiteConfig: async ({ site_id }: { site_id: string }) => {
    try {
      const [rows] = await database.run({
        sql: 'SELECT site_id, display_name, url, lighthouse_target FROM site_configs WHERE site_id = @siteId LIMIT 1',
        params: { siteId: site_id },
      });
      return rows.length > 0 ? rows[0].toJSON() : null;
    } catch (err) {
      console.error('[GraphQL] getSiteConfig error:', err);
      return null;
    }
  },

  getRecentTransactions: async ({ limit }: { limit?: number }) => {
    const pageSize = limit ?? 10;
    try {
      const [rows] = await database.run({
        sql: `SELECT id, revenue, ui_variant_id, CAST(timestamp AS STRING) as timestamp 
              FROM transactions ORDER BY timestamp DESC LIMIT @pageSize`,
        params: { pageSize },
      });
      return rows.map((row) => row.toJSON());
    } catch (err) {
      console.error('[GraphQL] getRecentTransactions error:', err);
      return [];
    }
  },

  // ── Mutations (publish events to subscribers) ──
  updateFlag: async ({
    id,
    site_id,
    feature_name,
    is_active,
  }: {
    id: string;
    site_id: string;
    feature_name: string;
    is_active: boolean;
  }) => {
    try {
      await database.runTransactionAsync(async (transaction) => {
        transaction.upsert('feature_flags', { id, site_id, feature_name, is_active });
        await transaction.commit();
      });
      const flag = { id, site_id, feature_name, is_active };
      pubsub.publish(EVENTS.FLAG_CHANGED, { flagChanged: flag, site_id });
      return flag;
    } catch (err) {
      console.error('[GraphQL] updateFlag error:', err);
      return null;
    }
  },

  createTransaction: async ({
    id,
    revenue,
    ui_variant_id,
  }: {
    id: string;
    revenue: number;
    ui_variant_id: string;
  }) => {
    const timestamp = new Date().toISOString();
    try {
      await database.runTransactionAsync(async (transaction) => {
        transaction.insert('transactions', { id, revenue, ui_variant_id, timestamp });
        await transaction.commit();
      });
      const txn = { id, revenue, ui_variant_id, timestamp };
      pubsub.publish(EVENTS.TRANSACTION_CREATED, { transactionCreated: txn });
      return txn;
    } catch (err) {
      console.error('[GraphQL] createTransaction error:', err);
      return null;
    }
  },

  // ── Subscriptions (AsyncIterator pattern) ──
  flagChanged: ({ site_id }: { site_id: string }) => {
    const baseIterator = pubsub.asyncIterator(EVENTS.FLAG_CHANGED);
    // Filter: only yield events matching the requested site_id
    return {
      async next(): Promise<IteratorResult<unknown>> {
        while (true) {
          const result = await baseIterator.next();
          if (result.done) return result;
          // biome-ignore lint/suspicious/noExplicitAny: PubSub payload shape
          const payload = result.value as any;
          if (payload.site_id === site_id) {
            return { value: payload, done: false };
          }
        }
      },
      return: () => baseIterator.return!(),
      throw: (err: Error) => baseIterator.throw!(err),
      [Symbol.asyncIterator]() {
        return this;
      },
    };
  },

  transactionCreated: () => pubsub.asyncIterator(EVENTS.TRANSACTION_CREATED),
};

// ──────────────────────────────────────────────────────────────
// WebSocket session state for graphql-ws protocol
// ──────────────────────────────────────────────────────────────
interface WsSession {
  subscriptions: Map<string, AsyncIterableIterator<unknown>>;
  initialized: boolean;
}

// ──────────────────────────────────────────────────────────────
// Server — HTTP + WebSocket
// ──────────────────────────────────────────────────────────────
if (import.meta.main) {
  const PORT = parseInt(process.env.GRAPHQL_PORT || '4000', 10);

  Bun.serve<WsSession>({
    port: PORT,

    async fetch(req, server) {
      // ── WebSocket upgrade (graphql-ws protocol) ──
      const upgrade = req.headers.get('upgrade')?.toLowerCase();
      if (upgrade === 'websocket') {
        const protocols = req.headers.get('sec-websocket-protocol') ?? '';
        const supported = protocols.split(',').map((p) => p.trim());
        if (supported.includes('graphql-transport-ws')) {
          const ok = server.upgrade(req, {
            headers: { 'Sec-WebSocket-Protocol': 'graphql-transport-ws' },
            data: { subscriptions: new Map(), initialized: false } satisfies WsSession,
          });
          return ok ? undefined : new Response('WebSocket upgrade failed', { status: 500 });
        }
        return new Response('Unsupported WebSocket subprotocol', { status: 400 });
      }

      // ── CORS preflight ──
      if (req.method === 'OPTIONS') {
        return new Response(null, {
          headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
          },
        });
      }

      // ── HTTP POST for queries & mutations ──
      if (req.method === 'POST') {
        const { query, variables } = await req.json();
        const result = await graphql({
          schema,
          source: query,
          rootValue,
          variableValues: variables,
        });
        return Response.json(result, {
          headers: { 'Access-Control-Allow-Origin': '*' },
        });
      }

      return new Response('V25 GraphQL Nexus — POST /graphql | WS /graphql', { status: 404 });
    },

    websocket: {
      open(ws: ServerWebSocket<WsSession>) {
        // Connection opened — wait for connection_init per graphql-ws protocol
        console.log('[WS] Client connected');
      },

      async message(ws: ServerWebSocket<WsSession>, rawMsg: string | Buffer) {
        try {
          const msg = JSON.parse(typeof rawMsg === 'string' ? rawMsg : rawMsg.toString());

          switch (msg.type) {
            case 'connection_init': {
              ws.data.initialized = true;
              ws.send(JSON.stringify({ type: 'connection_ack' }));
              break;
            }

            case 'subscribe': {
              if (!ws.data.initialized) {
                ws.send(
                  JSON.stringify({
                    id: msg.id,
                    type: 'error',
                    payload: [{ message: 'Not initialized' }],
                  }),
                );
                break;
              }

              const { query: source, variables } = msg.payload;
              const document = parse(source);

              // Start subscription via graphql-js subscribe()
              const result = await subscribe({
                schema,
                document,
                rootValue,
                variableValues: variables,
              });

              // If it's an error (not an async iterator), send error + complete
              if (!('next' in (result as object))) {
                const errorResult = result as ExecutionResult;
                ws.send(JSON.stringify({ id: msg.id, type: 'error', payload: errorResult.errors }));
                ws.send(JSON.stringify({ id: msg.id, type: 'complete' }));
                break;
              }

              // It's an AsyncIterator — consume and forward
              const iterator = result as AsyncIterableIterator<ExecutionResult>;
              ws.data.subscriptions.set(msg.id, iterator);

              // Fire-and-forget: stream results to client
              (async () => {
                try {
                  for await (const value of iterator) {
                    ws.send(JSON.stringify({ id: msg.id, type: 'next', payload: value }));
                  }
                  ws.send(JSON.stringify({ id: msg.id, type: 'complete' }));
                } catch {
                  // Client disconnected or iterator threw
                }
              })();

              break;
            }

            case 'complete': {
              // Client unsubscribing
              const iter = ws.data.subscriptions.get(msg.id);
              if (iter?.return) await iter.return();
              ws.data.subscriptions.delete(msg.id);
              break;
            }

            case 'ping': {
              ws.send(JSON.stringify({ type: 'pong' }));
              break;
            }
          }
        } catch (err) {
          console.error('[WS] Message error:', err);
        }
      },

      close(ws: ServerWebSocket<WsSession>) {
        // Cleanup all active subscriptions on disconnect
        for (const [, iter] of ws.data.subscriptions) {
          if (iter.return) void iter.return();
        }
        ws.data.subscriptions.clear();
        console.log('[WS] Client disconnected');
      },
    },
  });

  console.log(`🔮 V25 GraphQL Nexus active on port ${PORT} (HTTP + WS)`);
}
