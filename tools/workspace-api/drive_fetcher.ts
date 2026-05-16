/**
 * Active Google Drive API Polling — V25 Pinnacle
 * Allows Opus 4.6 to proactively fetch PRDs and workspace documents on demand.
 * MCP Server: google-drive-api
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "google-drive-api",
  version: "1.0.0",
  description: "Google Drive document fetcher — proactive PRD and workspace doc retrieval",
});

server.tool(
  "drive_search",
  "Search Google Drive for documents by name or content",
  {
    query: z.string().describe("Search query for Drive files"),
    mimeType: z
      .string()
      .optional()
      .describe("Filter by MIME type (e.g., application/vnd.google-apps.document)"),
    maxResults: z.number().optional().describe("Max results (default 10)"),
  },
  async ({ query, mimeType, maxResults }) => {
    // Uses ADC for authentication
    const { google } = await import("googleapis");
    const auth = new google.auth.GoogleAuth({
      scopes: ["https://www.googleapis.com/auth/drive.readonly"],
    });
    const drive = google.drive({ version: "v3", auth });

    let q = `fullText contains '${query.replace(/'/g, "\\'")}'`;
    if (mimeType) q += ` and mimeType='${mimeType}'`;

    try {
      const res = await drive.files.list({
        q,
        pageSize: maxResults || 10,
        fields: "files(id, name, mimeType, modifiedTime, webViewLink)",
      });
      return {
        content: [{ type: "text", text: JSON.stringify(res.data.files || [], null, 2) }],
      };
    } catch (err: unknown) {
      const error = err as Error;
      return {
        content: [{ type: "text", text: `Error: ${error.message}` }],
        isError: true,
      };
    }
  }
);

server.tool(
  "drive_get_content",
  "Get the text content of a Google Drive document by ID",
  {
    fileId: z.string().describe("The Google Drive file ID"),
  },
  async ({ fileId }) => {
    const { google } = await import("googleapis");
    const auth = new google.auth.GoogleAuth({
      scopes: ["https://www.googleapis.com/auth/drive.readonly"],
    });
    const drive = google.drive({ version: "v3", auth });

    try {
      const res = await drive.files.export({
        fileId,
        mimeType: "text/plain",
      });
      return {
        content: [{ type: "text", text: String(res.data).slice(0, 50000) }],
      };
    } catch (err: unknown) {
      const error = err as Error;
      return {
        content: [{ type: "text", text: `Error: ${error.message}` }],
        isError: true,
      };
    }
  }
);

server.tool(
  "drive_list_recent",
  "List recently modified documents in Google Drive",
  {
    maxResults: z.number().optional().describe("Max results (default 10)"),
  },
  async ({ maxResults }) => {
    const { google } = await import("googleapis");
    const auth = new google.auth.GoogleAuth({
      scopes: ["https://www.googleapis.com/auth/drive.readonly"],
    });
    const drive = google.drive({ version: "v3", auth });

    try {
      const res = await drive.files.list({
        pageSize: maxResults || 10,
        orderBy: "modifiedTime desc",
        fields: "files(id, name, mimeType, modifiedTime, webViewLink)",
      });
      return {
        content: [{ type: "text", text: JSON.stringify(res.data.files || [], null, 2) }],
      };
    } catch (err: unknown) {
      const error = err as Error;
      return {
        content: [{ type: "text", text: `Error: ${error.message}` }],
        isError: true,
      };
    }
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
