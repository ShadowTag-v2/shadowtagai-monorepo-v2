#!/usr/bin/env node
/**
 * @uphill/mcp-gemini-memory — Sovereign Epistemic Engine
 *
 * Gemini API File Search MCP Server for UphillSnowball.
 * Replaces NotebookLM with an API-native, zero-infrastructure RAG engine.
 *
 * Tools exposed:
 *   - create_memory_store       — Create a FileSearchStore with multimodal embeddings
 *   - upload_to_memory          — Upload a file with enforced metadata taxonomy
 *   - search_memory             — Query the store with metadata filters, returns citations
 *   - list_memory_stores        — List all FileSearchStores
 *   - list_memory_documents     — List documents in a store
 *   - delete_memory_document    — Delete a specific document
 *   - delete_memory_store       — Delete an entire store
 *
 * Resources exposed:
 *   - memory://taxonomy         — The immutable metadata taxonomy schema
 *   - memory://geminiignore     — The .geminiignore rules
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { GoogleGenAI } from "@google/genai";

// ─── Immutable Metadata Taxonomy ──────────────────────────────────────────────
// This is the ONLY set of allowed metadata keys. The upload tool will reject
// any metadata that doesn't conform. This prevents namespace pollution.
const METADATA_TAXONOMY = {
  domain: {
    type: "string",
    allowed: [
      "architecture",
      "cloud_run",
      "firebase",
      "firestore",
      "auth",
      "stripe",
      "security",
      "genkit",
      "spanner",
      "bigquery",
      "headfade",
      "counselconduit",
      "deployment",
      "testing",
      "design",
      "general",
    ],
    description: "The functional domain this document belongs to",
  },
  source: {
    type: "string",
    allowed: [
      "adr",
      "codewiki",
      "readme",
      "design_doc",
      "api_doc",
      "diagram",
      "runbook",
      "manifest",
      "schema",
      "config",
      "whitepaper",
    ],
    description: "The type of source document",
  },
  status: {
    type: "string",
    allowed: ["active", "deprecated", "draft", "archived"],
    description: "Current lifecycle status",
  },
  last_modified: {
    type: "string",
    description: "ISO 8601 date of last modification (YYYY-MM-DD)",
  },
  component: {
    type: "string",
    allowed: [
      "frontend",
      "backend",
      "infra",
      "mcp",
      "agent",
      "kernel",
      "pwa",
      "api",
      "daemon",
      "ci_cd",
    ],
    description: "The architectural component this document relates to",
  },
};

// ─── .geminiignore Protocol ───────────────────────────────────────────────────
// Files matching these patterns are NEVER ingested into the Epistemic Engine.
const GEMINI_IGNORE_PATTERNS = [
  "node_modules/",
  ".dart_tool/",
  ".next/",
  "dist/",
  "build/",
  ".git/",
  "*.lock",
  "*.log",
  "*.min.js",
  "*.min.css",
  "*.map",
  "*.wasm",
  "*.o",
  "*.pyc",
  "__pycache__/",
  ".env",
  ".env.*",
  "keys/",
  "*.pem",
  "*.p12",
  "coverage/",
  ".beads/",
  "_audit_claude_code/",
  "external_repos/",
  ".tempmediaStorage/",
];

// Allowed target directories for ingestion
const ALLOWED_INGEST_PATHS = [
  "docs/",
  "adrs/",
  "design/",
  ".agents/",
  "AGENTS.md",
  "GEMINI.md",
  "CLAUDE.md",
  "BUSINESS_CONTEXT_LOCKED.md",
  "RISK_REGISTER.md",
  "monorepo_manifest.yaml",
  "walkthrough.md",
];

// ─── Validation Helpers ───────────────────────────────────────────────────────

function validateMetadata(metadata) {
  const errors = [];
  for (const item of metadata) {
    const { key } = item;
    const schema = METADATA_TAXONOMY[key];

    if (!schema) {
      errors.push(
        `Rejected metadata key "${key}". Allowed keys: ${Object.keys(METADATA_TAXONOMY).join(", ")}`
      );
      continue;
    }

    const value = item.stringValue || item.numericValue;
    if (schema.allowed && !schema.allowed.includes(value)) {
      errors.push(
        `Invalid value "${value}" for key "${key}". Allowed: ${schema.allowed.join(", ")}`
      );
    }
  }
  return errors;
}

function isIgnored(filePath) {
  return GEMINI_IGNORE_PATTERNS.some((pattern) => {
    if (pattern.endsWith("/")) {
      return filePath.includes(pattern);
    }
    if (pattern.startsWith("*.")) {
      return filePath.endsWith(pattern.slice(1));
    }
    return filePath.includes(pattern);
  });
}

// ─── MCP Server ───────────────────────────────────────────────────────────────

const apiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
if (!apiKey) {
  console.error(
    "FATAL: GEMINI_API_KEY or GOOGLE_API_KEY environment variable required"
  );
  process.exit(1);
}

const ai = new GoogleGenAI({ apiKey });

const server = new Server(
  { name: "mcp-gemini-memory", version: "1.0.0" },
  {
    capabilities: {
      tools: {},
      resources: {},
    },
  }
);

// ─── Resources ────────────────────────────────────────────────────────────────

server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: [
    {
      uri: "memory://taxonomy",
      name: "Metadata Taxonomy",
      description:
        "The immutable metadata taxonomy schema for the Epistemic Engine",
      mimeType: "application/json",
    },
    {
      uri: "memory://geminiignore",
      name: ".geminiignore Rules",
      description:
        "Ignore patterns preventing ingestion of noise into the vector space",
      mimeType: "application/json",
    },
  ],
}));

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  if (uri === "memory://taxonomy") {
    return {
      contents: [
        {
          uri,
          mimeType: "application/json",
          text: JSON.stringify(METADATA_TAXONOMY, null, 2),
        },
      ],
    };
  }

  if (uri === "memory://geminiignore") {
    return {
      contents: [
        {
          uri,
          mimeType: "application/json",
          text: JSON.stringify(
            {
              ignore_patterns: GEMINI_IGNORE_PATTERNS,
              allowed_ingest_paths: ALLOWED_INGEST_PATHS,
            },
            null,
            2
          ),
        },
      ],
    };
  }

  throw new Error(`Unknown resource: ${uri}`);
});

// ─── Tools ────────────────────────────────────────────────────────────────────

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "create_memory_store",
      description:
        "Create a new FileSearchStore with multimodal embeddings (gemini-embedding-2). " +
        "Each store is a semantic index for a specific knowledge domain.",
      inputSchema: {
        type: "object",
        properties: {
          display_name: {
            type: "string",
            description:
              "Human-readable name for the store (e.g. 'uphillsnowball-architecture')",
          },
        },
        required: ["display_name"],
      },
    },
    {
      name: "upload_to_memory",
      description:
        "Upload a file to the Epistemic Engine with enforced metadata taxonomy. " +
        "Supports text, PDF, PNG, JPEG. Files matching .geminiignore are rejected. " +
        "Metadata MUST conform to the taxonomy (read memory://taxonomy first).",
      inputSchema: {
        type: "object",
        properties: {
          store_name: {
            type: "string",
            description:
              "The FileSearchStore name (e.g. 'fileSearchStores/abc123')",
          },
          file_path: {
            type: "string",
            description: "Absolute path to the file to upload",
          },
          display_name: {
            type: "string",
            description: "Display name visible in citations",
          },
          metadata: {
            type: "array",
            description:
              "Custom metadata array. Each item: {key, stringValue} or {key, numericValue}",
            items: {
              type: "object",
              properties: {
                key: { type: "string" },
                stringValue: { type: "string" },
                numericValue: { type: "number" },
              },
              required: ["key"],
            },
          },
        },
        required: ["store_name", "file_path", "display_name", "metadata"],
      },
    },
    {
      name: "search_memory",
      description:
        "Query the Epistemic Engine. Returns grounded answers with inline citations, " +
        "page numbers, and custom metadata from source documents. " +
        "Use metadata_filter for targeted retrieval (AIP-160 syntax: domain='auth').",
      inputSchema: {
        type: "object",
        properties: {
          store_names: {
            type: "array",
            items: { type: "string" },
            description: "FileSearchStore names to search across",
          },
          query: {
            type: "string",
            description: "The natural language query",
          },
          metadata_filter: {
            type: "string",
            description:
              "AIP-160 filter (e.g. 'domain=\"auth\" AND status=\"active\"'). Optional.",
          },
          model: {
            type: "string",
            description:
              "Model to use for generation. Default: gemini-3-flash-preview",
          },
        },
        required: ["store_names", "query"],
      },
    },
    {
      name: "list_memory_stores",
      description: "List all FileSearchStores in the Epistemic Engine.",
      inputSchema: { type: "object", properties: {} },
    },
    {
      name: "list_memory_documents",
      description: "List all documents in a specific FileSearchStore.",
      inputSchema: {
        type: "object",
        properties: {
          store_name: {
            type: "string",
            description: "The FileSearchStore name",
          },
        },
        required: ["store_name"],
      },
    },
    {
      name: "delete_memory_document",
      description: "Delete a specific document from a FileSearchStore.",
      inputSchema: {
        type: "object",
        properties: {
          document_name: {
            type: "string",
            description:
              "Full document name (e.g. 'fileSearchStores/abc/documents/xyz')",
          },
        },
        required: ["document_name"],
      },
    },
    {
      name: "delete_memory_store",
      description:
        "Delete an entire FileSearchStore and all its documents. DESTRUCTIVE.",
      inputSchema: {
        type: "object",
        properties: {
          store_name: {
            type: "string",
            description: "The FileSearchStore name to delete",
          },
        },
        required: ["store_name"],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    // ── Create Store ────────────────────────────────────────────────────────
    case "create_memory_store": {
      const store = await ai.fileSearchStores.create({
        config: {
          displayName: args.display_name,
          embeddingModel: "models/gemini-embedding-2",
        },
      });
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                success: true,
                store_name: store.name,
                display_name: store.displayName,
                embedding_model: "models/gemini-embedding-2",
                message:
                  "Multimodal FileSearchStore created. Supports text, PDF, PNG, JPEG.",
              },
              null,
              2
            ),
          },
        ],
      };
    }

    // ── Upload File ─────────────────────────────────────────────────────────
    case "upload_to_memory": {
      // Enforce .geminiignore
      if (isIgnored(args.file_path)) {
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify({
                success: false,
                error: `File rejected by .geminiignore protocol: ${args.file_path}`,
                hint: "Only docs/, adrs/, design/, and curated source files are allowed.",
              }),
            },
          ],
          isError: true,
        };
      }

      // Enforce metadata taxonomy
      const metadataErrors = validateMetadata(args.metadata || []);
      if (metadataErrors.length > 0) {
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify({
                success: false,
                error: "Metadata taxonomy violation",
                violations: metadataErrors,
                hint: "Read memory://taxonomy to see allowed keys and values.",
              }),
            },
          ],
          isError: true,
        };
      }

      // Upload with metadata
      let operation = await ai.fileSearchStores.uploadToFileSearchStore({
        file: args.file_path,
        fileSearchStoreName: args.store_name,
        config: {
          displayName: args.display_name,
          customMetadata: args.metadata,
        },
      });

      // Poll for completion
      let attempts = 0;
      while (!operation.done && attempts < 60) {
        await new Promise((r) => setTimeout(r, 2000));
        operation = await ai.operations.get({ operation });
        attempts++;
      }

      if (!operation.done) {
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify({
                success: false,
                error: "Upload operation timed out after 120s",
                operation_name: operation.name,
              }),
            },
          ],
          isError: true,
        };
      }

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                success: true,
                message: `File "${args.display_name}" uploaded and indexed`,
                store: args.store_name,
                metadata: args.metadata,
              },
              null,
              2
            ),
          },
        ],
      };
    }

    // ── Search Memory ───────────────────────────────────────────────────────
    case "search_memory": {
      const model = args.model || "gemini-3-flash-preview";
      const toolConfig = {
        fileSearch: {
          fileSearchStoreNames: args.store_names,
        },
      };

      if (args.metadata_filter) {
        toolConfig.fileSearch.metadataFilter = args.metadata_filter;
      }

      const response = await ai.models.generateContent({
        model,
        contents: args.query,
        config: {
          tools: [toolConfig],
        },
      });

      // Extract citations from grounding metadata
      const groundingMetadata =
        response.candidates?.[0]?.groundingMetadata || {};
      const citations = (groundingMetadata.groundingChunks || []).map(
        (chunk) => {
          const ctx = chunk.retrievedContext || {};
          return {
            title: ctx.title,
            text: ctx.text?.substring(0, 500), // Truncate to save tokens
            page_number: ctx.pageNumber,
            media_id: ctx.mediaId,
            file_search_store: ctx.fileSearchStore,
            custom_metadata: ctx.customMetadata,
          };
        }
      );

      // Extract grounding supports (maps text segments to citations)
      const supports = (groundingMetadata.groundingSupports || []).map((s) => ({
        text: s.segment?.text,
        citation_indices: s.groundingChunkIndices,
        confidence: s.confidenceScores,
      }));

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                answer: response.text,
                citations,
                supports,
                model_used: model,
                stores_searched: args.store_names,
                metadata_filter: args.metadata_filter || null,
              },
              null,
              2
            ),
          },
        ],
      };
    }

    // ── List Stores ─────────────────────────────────────────────────────────
    case "list_memory_stores": {
      const stores = [];
      const storeList = await ai.fileSearchStores.list();
      for await (const store of storeList) {
        stores.push({
          name: store.name,
          display_name: store.displayName,
          create_time: store.createTime,
        });
      }
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              { stores, total: stores.length },
              null,
              2
            ),
          },
        ],
      };
    }

    // ── List Documents ──────────────────────────────────────────────────────
    case "list_memory_documents": {
      const docs = [];
      const docList = await ai.fileSearchStores.documents.list({
        parent: args.store_name,
      });
      for await (const doc of docList) {
        docs.push({
          name: doc.name,
          display_name: doc.displayName,
          create_time: doc.createTime,
        });
      }
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                documents: docs,
                total: docs.length,
                store: args.store_name,
              },
              null,
              2
            ),
          },
        ],
      };
    }

    // ── Delete Document ─────────────────────────────────────────────────────
    case "delete_memory_document": {
      await ai.fileSearchStores.documents.delete({
        name: args.document_name,
      });
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              success: true,
              deleted: args.document_name,
            }),
          },
        ],
      };
    }

    // ── Delete Store ────────────────────────────────────────────────────────
    case "delete_memory_store": {
      await ai.fileSearchStores.delete({
        name: args.store_name,
        config: { force: true },
      });
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              success: true,
              deleted: args.store_name,
              warning: "All documents and embeddings have been destroyed.",
            }),
          },
        ],
      };
    }

    default:
      throw new Error(`Unknown tool: ${name}`);
  }
});

// ─── Start Server ─────────────────────────────────────────────────────────────

const transport = new StdioServerTransport();
await server.connect(transport);
