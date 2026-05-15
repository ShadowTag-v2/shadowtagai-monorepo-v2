/**
 * Workspace Intake — MCP Server Stub
 * 
 * Provides workspace file indexing and context ingestion
 * capabilities to the Cline Heavy Cruiser fleet.
 * 
 * Runtime: Bun
 * Transport: stdio (MCP JSON-RPC)
 */

import { readdir, stat } from "node:fs/promises";
import { join, relative, extname } from "node:path";

const WORKSPACE_ROOT = "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball";

// File extension categories
const CODE_EXTENSIONS = new Set([
  ".ts", ".tsx", ".js", ".jsx", ".py", ".cs", ".go", ".rs",
  ".json", ".yaml", ".yml", ".toml", ".md", ".html", ".css",
]);

const IGNORED_DIRS = new Set([
  "node_modules", ".git", "__pycache__", ".venv", "venv",
  "dist", "build", ".next", "out", "external_repos", "archive",
]);

interface FileEntry {
  path: string;
  size: number;
  extension: string;
  isDirectory: boolean;
}

/**
 * Recursively scan a directory, returning file metadata.
 */
async function scanDirectory(
  dir: string,
  maxDepth: number = 4,
  currentDepth: number = 0
): Promise<FileEntry[]> {
  if (currentDepth >= maxDepth) return [];

  const entries: FileEntry[] = [];
  
  try {
    const items = await readdir(dir, { withFileTypes: true });

    for (const item of items) {
      if (IGNORED_DIRS.has(item.name)) continue;
      if (item.name.startsWith(".") && item.name !== ".agents") continue;

      const fullPath = join(dir, item.name);
      const relativePath = relative(WORKSPACE_ROOT, fullPath);

      if (item.isDirectory()) {
        entries.push({
          path: relativePath,
          size: 0,
          extension: "",
          isDirectory: true,
        });
        const children = await scanDirectory(fullPath, maxDepth, currentDepth + 1);
        entries.push(...children);
      } else {
        const ext = extname(item.name);
        if (CODE_EXTENSIONS.has(ext)) {
          const stats = await stat(fullPath);
          entries.push({
            path: relativePath,
            size: stats.size,
            extension: ext,
            isDirectory: false,
          });
        }
      }
    }
  } catch {
    // Permission errors, etc.
  }

  return entries;
}

/**
 * MCP JSON-RPC handler — responds to tool calls via stdin/stdout.
 */
async function handleRequest(request: { method: string; params?: Record<string, unknown> }) {
  switch (request.method) {
    case "tools/list":
      return {
        tools: [
          {
            name: "scan_workspace",
            description: "Scan the monorepo workspace and return file tree metadata",
            inputSchema: {
              type: "object",
              properties: {
                path: { type: "string", description: "Subdirectory to scan (relative to workspace root)" },
                maxDepth: { type: "number", description: "Maximum directory depth (default: 4)" },
              },
            },
          },
          {
            name: "get_workspace_stats",
            description: "Get aggregate statistics about the workspace",
            inputSchema: { type: "object", properties: {} },
          },
        ],
      };

    case "tools/call": {
      const toolName = (request.params as { name: string })?.name;
      const args = (request.params as { arguments?: Record<string, unknown> })?.arguments ?? {};

      if (toolName === "scan_workspace") {
        const subPath = (args.path as string) ?? "";
        const maxDepth = (args.maxDepth as number) ?? 4;
        const scanRoot = subPath ? join(WORKSPACE_ROOT, subPath) : WORKSPACE_ROOT;
        const files = await scanDirectory(scanRoot, maxDepth);
        return {
          content: [{ type: "text", text: JSON.stringify(files, null, 2) }],
        };
      }

      if (toolName === "get_workspace_stats") {
        const files = await scanDirectory(WORKSPACE_ROOT, 3);
        const byExt = new Map<string, number>();
        let totalSize = 0;
        let fileCount = 0;

        for (const f of files) {
          if (!f.isDirectory) {
            fileCount++;
            totalSize += f.size;
            byExt.set(f.extension, (byExt.get(f.extension) ?? 0) + 1);
          }
        }

        return {
          content: [{
            type: "text",
            text: JSON.stringify({
              totalFiles: fileCount,
              totalSizeBytes: totalSize,
              extensionBreakdown: Object.fromEntries(byExt),
              workspaceRoot: WORKSPACE_ROOT,
            }, null, 2),
          }],
        };
      }

      return { content: [{ type: "text", text: `Unknown tool: ${toolName}` }] };
    }

    default:
      return {};
  }
}

// MCP stdio transport — read JSON-RPC from stdin, write to stdout
const decoder = new TextDecoder();
let buffer = "";

process.stdin.on("data", async (chunk: Buffer) => {
  buffer += decoder.decode(chunk, { stream: true });

  // Parse newline-delimited JSON-RPC
  const lines = buffer.split("\n");
  buffer = lines.pop() ?? "";

  for (const line of lines) {
    if (!line.trim()) continue;
    try {
      const request = JSON.parse(line);
      const result = await handleRequest(request);
      const response = { jsonrpc: "2.0", id: request.id, result };
      process.stdout.write(JSON.stringify(response) + "\n");
    } catch {
      // Ignore malformed input
    }
  }
});

console.error("🔧 workspace-intake MCP server started (stdio)");
