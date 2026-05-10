#!/usr/bin/env node
/**
 * MCP Spanner Bridge — V25 Pinnacle
 *
 * Provides read-only Spanner operations over MCP stdio:
 *   - spanner_query: Run read-only SQL queries
 *   - spanner_list_tables: List all tables in the database
 *   - spanner_get_schema: Get DDL for a specific table
 *
 * Requires ADC or GOOGLE_APPLICATION_CREDENTIALS.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const PROJECT_ID = process.env.SPANNER_PROJECT || "shadowtag-omega-v4";
const INSTANCE_ID = process.env.SPANNER_INSTANCE || "core-cluster";
const DATABASE_ID = process.env.SPANNER_DATABASE || "shadowtag-db";

let spannerClient = null;

async function getSpannerDatabase() {
  if (!spannerClient) {
    const { Spanner } = await import("@google-cloud/spanner");
    const spanner = new Spanner({ projectId: PROJECT_ID });
    const instance = spanner.instance(INSTANCE_ID);
    spannerClient = instance.database(DATABASE_ID);
  }
  return spannerClient;
}

const server = new McpServer({
  name: "google-cloud-spanner",
  version: "1.0.0",
  description: `Spanner bridge for ${PROJECT_ID}/${INSTANCE_ID}/${DATABASE_ID}`,
});

server.tool(
  "spanner_query",
  "Run a read-only SQL query against Spanner",
  { sql: z.string().describe("The SQL query to execute (read-only)") },
  async ({ sql }) => {
    try {
      const db = await getSpannerDatabase();
      const [rows] = await db.run({ sql, json: true });
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(rows.slice(0, 100), null, 2),
          },
        ],
      };
    } catch (err) {
      return {
        content: [{ type: "text", text: `Error: ${err.message}` }],
        isError: true,
      };
    }
  }
);

server.tool(
  "spanner_list_tables",
  "List all tables in the Spanner database",
  {},
  async () => {
    try {
      const db = await getSpannerDatabase();
      const [rows] = await db.run({
        sql: `SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = ''`,
        json: true,
      });
      const tables = rows.map((r) => r.TABLE_NAME || r.table_name);
      return {
        content: [{ type: "text", text: JSON.stringify(tables, null, 2) }],
      };
    } catch (err) {
      return {
        content: [{ type: "text", text: `Error: ${err.message}` }],
        isError: true,
      };
    }
  }
);

server.tool(
  "spanner_get_schema",
  "Get DDL schema for a specific table",
  { table: z.string().describe("Table name") },
  async ({ table }) => {
    try {
      const db = await getSpannerDatabase();
      const [rows] = await db.run({
        sql: `SELECT COLUMN_NAME, SPANNER_TYPE, IS_NULLABLE
              FROM INFORMATION_SCHEMA.COLUMNS
              WHERE TABLE_NAME = @table AND TABLE_SCHEMA = ''
              ORDER BY ORDINAL_POSITION`,
        params: { table },
        json: true,
      });
      return {
        content: [{ type: "text", text: JSON.stringify(rows, null, 2) }],
      };
    } catch (err) {
      return {
        content: [{ type: "text", text: `Error: ${err.message}` }],
        isError: true,
      };
    }
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
