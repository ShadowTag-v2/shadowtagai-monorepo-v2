#!/usr/bin/env node
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const execFileAsync = promisify(execFile);

const server = new McpServer({
  name: "genkit",
  version: "1.0.0",
});

server.tool("genkit_help", "Show Genkit CLI help.", {}, async () => {
  const { stdout, stderr } = await execFileAsync("npx", ["-y", "genkit-cli", "--help"], {
    timeout: 15000,
    maxBuffer: 1024 * 1024,
  });
  return { content: [{ type: "text", text: stdout || stderr || "No output." }] };
});

server.tool(
  "genkit_cli",
  "Run a bounded Genkit CLI command.",
  {
    args: z.array(z.string()).describe("Arguments passed after genkit."),
  },
  async ({ args }) => {
    const safeArgs = args.filter((arg) => !/[;&|`$<>]/.test(arg));
    const { stdout, stderr } = await execFileAsync("npx", ["-y", "genkit-cli", ...safeArgs], {
      timeout: 30000,
      maxBuffer: 1024 * 1024,
    });
    return { content: [{ type: "text", text: stdout || stderr || "No output." }] };
  },
);

await server.connect(new StdioServerTransport());
