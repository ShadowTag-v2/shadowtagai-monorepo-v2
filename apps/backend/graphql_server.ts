/**
 * Triple-Site GraphQL Nexus — V25 Pinnacle
 * Feature flag and site config API backed by Spanner.
 * Serves the HeadFade, CounselConduit, and KovelAI/ShadowTagAI fleet.
 */
import { buildSchema, graphql } from 'graphql';
import { Spanner } from '@google-cloud/spanner';

const PROJECT_ID = process.env.GOOGLE_CLOUD_PROJECT || 'shadowtag-omega-v4';
const INSTANCE_ID = process.env.SPANNER_INSTANCE || 'uphill-core-cluster';
const DATABASE_ID = process.env.SPANNER_DATABASE || 'uphill-ledger';

const spanner = new Spanner({ projectId: PROJECT_ID });
const database = spanner.instance(INSTANCE_ID).database(DATABASE_ID);

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
`);

const rootValue = {
  getFlags: async ({ site_id }: { site_id: string }) => {
    try {
      const [rows] = await database.run({
        sql: 'SELECT id, site_id, feature_name, is_active FROM feature_flags WHERE site_id = @siteId',
        params: { siteId: site_id },
      });
      return rows.map(row => row.toJSON());
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
      return rows.map(row => row.toJSON());
    } catch (err) {
      console.error('[GraphQL] getRecentTransactions error:', err);
      return [];
    }
  },
};

if (import.meta.main) {
  const PORT = parseInt(process.env.GRAPHQL_PORT || '4000', 10);

  Bun.serve({
    port: PORT,
    async fetch(req) {
      // CORS preflight
      if (req.method === 'OPTIONS') {
        return new Response(null, {
          headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
          },
        });
      }

      if (req.method === 'POST') {
        const { query, variables } = await req.json();
        const result = await graphql({ schema, source: query, rootValue, variableValues: variables });
        return Response.json(result, {
          headers: { 'Access-Control-Allow-Origin': '*' },
        });
      }

      return new Response('V25 GraphQL Nexus — POST /graphql', { status: 404 });
    },
  });

  console.log(`🔮 V25 GraphQL Nexus active on port ${PORT}`);
}
