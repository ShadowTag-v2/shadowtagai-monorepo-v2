/**
 * AST-Grep Semantic Scalpel — MCP Server (V25 Pinnacle)
 *
 * Exposes ast-grep search, rewrite, and scan operations over MCP stdio protocol.
 * Replaces regex/sed mutations with deterministic AST-level surgery.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { execSync } from "node:child_process";

const server = new McpServer({
  name: "semantic-scalpel",
  version: "1.0.0",
  description: "AST-Grep search, rewrite, and scan over MCP stdio",
});

function runAstGrep(args: string[]): string {
  try {
    const result = execSync(`sg ${args.join(" ")}`, {
      encoding: "utf-8",
      timeout: 30_000,
      maxBuffer: 10 * 1024 * 1024,
      cwd: process.cwd(),
    });
    return result;
  } catch (err: unknown) {
    const error = err as { stdout?: string; stderr?: string; message?: string };
    if (error.stdout) return error.stdout;
    throw new Error(error.stderr || error.message || "ast-grep failed");
  }
}

server.tool(
  "ast_search",
  "Search for AST patterns in source code using ast-grep",
  {
    pattern: z.string().describe("The ast-grep pattern to search for"),
    lang: z.string().optional().describe("Language (ts, js, py, go, rust, etc.)"),
    path: z.string().optional().describe("Path to search in (default: .)"),
  },
  async ({ pattern, lang, path }) => {
    const args = ["run", "--pattern", `'${pattern}'`];
    if (lang) args.push("--lang", lang);
    if (path) args.push(path);
    args.push("--json");
    try {
      const output = runAstGrep(args);
      return { content: [{ type: "text", text: output || "No matches found" }] };
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
  "ast_rewrite",
  "Rewrite AST patterns in source code (dry-run by default)",
  {
    pattern: z.string().describe("The pattern to match"),
    rewrite: z.string().describe("The replacement pattern"),
    lang: z.string().optional().describe("Language"),
    path: z.string().optional().describe("Path to rewrite in"),
    apply: z.boolean().optional().describe("Apply changes (default: dry-run)"),
  },
  async ({ pattern, rewrite, lang, path, apply }) => {
    const args = ["run", "--pattern", `'${pattern}'`, "--rewrite", `'${rewrite}'`];
    if (lang) args.push("--lang", lang);
    if (path) args.push(path);
    if (!apply) args.push("--json");
    try {
      const output = runAstGrep(args);
      return {
        content: [
          {
            type: "text",
            text: apply
              ? `Applied rewrite: ${pattern} → ${rewrite}\n${output}`
              : `Dry-run results:\n${output}`,
          },
        ],
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
  "ast_scan",
  "Run ast-grep scan with a rules file",
  {
    rulesFile: z.string().optional().describe("Path to rules YAML file"),
    path: z.string().optional().describe("Path to scan"),
  },
  async ({ rulesFile, path }) => {
    const args = ["scan"];
    if (rulesFile) args.push("--rule", rulesFile);
    if (path) args.push(path);
    args.push("--json");
    try {
      const output = runAstGrep(args);
      return { content: [{ type: "text", text: output || "No issues found" }] };
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
