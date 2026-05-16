#!/usr/bin/env node
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const execFileAsync = promisify(execFile);
const projectId = process.env.BIGQUERY_PROJECT_ID || process.env.GOOGLE_CLOUD_PROJECT || "shadowtag-omega-v4";

const server = new McpServer({
  name: "bigquery",
  version: "1.0.0",
});

server.tool("bigquery_list_datasets", "List BigQuery datasets for the configured project.", {}, async () => {
  const { stdout, stderr } = await execFileAsync("bq", ["ls", "--project_id", projectId], {
    timeout: 30000,
    maxBuffer: 1024 * 1024,
  });
  return { content: [{ type: "text", text: stdout || stderr || "No datasets returned." }] };
});

server.tool(
  "bigquery_query",
  "Run a read-only BigQuery SQL query.",
  {
    sql: z.string(),
    location: z.string().optional(),
  },
  async ({ sql, location }) => {
    const trimmed = sql.trim();
    if (!/^select\b|^with\b/i.test(trimmed)) {
      throw new Error("Only read-only SELECT/WITH queries are allowed.");
    }

    const args = ["query", "--nouse_legacy_sql", "--format=json", "--project_id", projectId];
    if (location) args.push("--location", location);
    args.push(trimmed);

    const { stdout, stderr } = await execFileAsync("bq", args, {
      timeout: 60000,
      maxBuffer: 4 * 1024 * 1024,
    });
    return { content: [{ type: "text", text: stdout || stderr || "No rows returned." }] };
  },
);

await server.connect(new StdioServerTransport());
