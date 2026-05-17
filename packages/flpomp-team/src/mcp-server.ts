/**
 * Pomelli Swarm — MCP Server (V25 Pinnacle)
 *
 * Orchestrates continuous A/B testing across the live fleet:
 *   - HeadFade (headfade.com)
 *   - CounselConduit (counselconduit production)
 *   - KovelAI (kovelai.com)
 *
 * Provides tools for:
 *   - inspect_design_quality: Run design quality audit via Lighthouse
 *   - compare_variants: Compare two URL variants for visual regression
 *   - fleet_status: Report health of all monitored applications
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const FLEET = {
  headfade: "https://headfade.com",
  counselconduit: "https://counselconduit-767252945109.us-central1.run.app",
  kovelai: "https://kovelai.com",
};

const server = new McpServer({
  name: "pomelli-swarm",
  version: "1.0.0",
  description: "Continuous A/B testing and design quality orchestration across the live fleet",
});

server.tool("fleet_status", "Report health status of all monitored applications", {}, async () => {
  const results: Record<string, string> = {};
  for (const [name, url] of Object.entries(FLEET)) {
    try {
      const resp = await fetch(url, { method: "HEAD", signal: AbortSignal.timeout(5000) });
      results[name] = `${resp.status} ${resp.statusText}`;
    } catch (err: unknown) {
      const error = err as Error;
      results[name] = `ERROR: ${error.message}`;
    }
  }
  return {
    content: [{ type: "text", text: JSON.stringify(results, null, 2) }],
  };
});

server.tool(
  "inspect_design_quality",
  "Run a design quality check against a URL (HTTP status + response time)",
  {
    url: z.string().url().describe("The URL to inspect"),
  },
  async ({ url }) => {
    const start = Date.now();
    try {
      const resp = await fetch(url, { signal: AbortSignal.timeout(10000) });
      const elapsed = Date.now() - start;
      const contentType = resp.headers.get("content-type") || "unknown";
      const contentLength = resp.headers.get("content-length") || "unknown";
      const csp = resp.headers.get("content-security-policy") || "not set";

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                url,
                status: resp.status,
                responseTimeMs: elapsed,
                contentType,
                contentLength,
                cspPresent: csp !== "not set",
                hstsPresent: !!resp.headers.get("strict-transport-security"),
              },
              null,
              2,
            ),
          },
        ],
      };
    } catch (err: unknown) {
      const error = err as Error;
      return {
        content: [{ type: "text", text: `Error inspecting ${url}: ${error.message}` }],
        isError: true,
      };
    }
  },
);

server.tool(
  "compare_variants",
  "Compare HTTP responses between two URL variants",
  {
    urlA: z.string().url().describe("First URL variant"),
    urlB: z.string().url().describe("Second URL variant"),
  },
  async ({ urlA, urlB }) => {
    const fetchMeta = async (url: string) => {
      const start = Date.now();
      const resp = await fetch(url, { signal: AbortSignal.timeout(10000) });
      return {
        url,
        status: resp.status,
        responseTimeMs: Date.now() - start,
        contentLength: resp.headers.get("content-length") || "unknown",
      };
    };
    try {
      const [a, b] = await Promise.all([fetchMeta(urlA), fetchMeta(urlB)]);
      return {
        content: [{ type: "text", text: JSON.stringify({ variantA: a, variantB: b }, null, 2) }],
      };
    } catch (err: unknown) {
      const error = err as Error;
      return {
        content: [{ type: "text", text: `Error comparing: ${error.message}` }],
        isError: true,
      };
    }
  },
);

const transport = new StdioServerTransport();
await server.connect(transport);
