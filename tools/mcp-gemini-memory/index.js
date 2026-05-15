#!/usr/bin/env node
/**
 * Gemini Memory — Sovereign Epistemic Engine MCP Server
 *
 * Provides file-based memory operations via Gemini API File Search:
 *   - memory_store: Store a fact with tags
 *   - memory_recall: Recall facts by semantic query
 *   - memory_list: List all stored memory tags
 *
 * Uses @google/genai for Gemini API file operations.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const MEMORY_DIR = join(process.cwd(), ".memory");

if (!existsSync(MEMORY_DIR)) {
  mkdirSync(MEMORY_DIR, { recursive: true });
}

function getMemoryPath() {
  return join(MEMORY_DIR, "facts.json");
}

function loadMemory() {
  const path = getMemoryPath();
  if (!existsSync(path)) return [];
  try {
    return JSON.parse(readFileSync(path, "utf-8"));
  } catch {
    return [];
  }
}

function saveMemory(facts) {
  writeFileSync(getMemoryPath(), JSON.stringify(facts, null, 2));
}

const server = new McpServer({
  name: "gemini-memory",
  version: "1.0.0",
  description: "Sovereign Epistemic Engine — local fact storage with semantic recall",
});

server.tool(
  "memory_store",
  "Store a fact in memory with optional tags",
  {
    fact: z.string().describe("The fact or knowledge to store"),
    tags: z.array(z.string()).optional().describe("Tags for categorization"),
    source: z.string().optional().describe("Source of the fact"),
  },
  async ({ fact, tags, source }) => {
    const facts = loadMemory();
    const entry = {
      id: `mem_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
      fact,
      tags: tags || [],
      source: source || "agent",
      timestamp: new Date().toISOString(),
    };
    facts.push(entry);
    saveMemory(facts);
    return {
      content: [{ type: "text", text: `Stored: ${entry.id} (${facts.length} total facts)` }],
    };
  }
);

server.tool(
  "memory_recall",
  "Recall facts from memory by keyword search",
  {
    query: z.string().describe("Search query to find relevant facts"),
    limit: z.number().optional().describe("Max results (default 10)"),
  },
  async ({ query, limit }) => {
    const facts = loadMemory();
    const maxResults = limit || 10;
    const queryLower = query.toLowerCase();
    const matches = facts
      .filter(
        (f) =>
          f.fact.toLowerCase().includes(queryLower) ||
          f.tags.some((t) => t.toLowerCase().includes(queryLower))
      )
      .slice(-maxResults);
    return {
      content: [
        {
          type: "text",
          text:
            matches.length > 0
              ? JSON.stringify(matches, null, 2)
              : `No facts matching "${query}"`,
        },
      ],
    };
  }
);

server.tool(
  "memory_list",
  "List all unique tags in memory",
  {},
  async () => {
    const facts = loadMemory();
    const tags = [...new Set(facts.flatMap((f) => f.tags))].sort();
    return {
      content: [
        {
          type: "text",
          text: `${facts.length} facts, ${tags.length} tags: ${tags.join(", ") || "(none)"}`,
        },
      ],
    };
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
