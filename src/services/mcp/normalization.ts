/**
 * Pure utility functions for MCP name normalization.
 * This file has no dependencies to avoid circular imports.
 */

// Claude.ai server names are prefixed with this string
const CLAUDEAI_SERVER_PREFIX = "claude.ai ";

/**
 * Known MCP server alias map.
 * Maps variant server name formats → canonical server name.
 * The canonical name is the one used in MCP config (e.g., antigravity-mcp-config.json).
 */
const MCP_SERVER_ALIASES: ReadonlyMap<string, string> = new Map([
  // google-developer-knowledge variants
  ["google_developer_knowledge", "google-developer-knowledge"],
  ["googleDeveloperKnowledge", "google-developer-knowledge"],
  ["google_developer-knowledge", "google-developer-knowledge"],
  // firebase-mcp-server variants
  ["firebase_mcp_server", "firebase-mcp-server"],
  ["firebaseMcpServer", "firebase-mcp-server"],
  // chrome-devtools-mcp variants
  ["chrome_devtools_mcp", "chrome-devtools-mcp"],
  ["chromeDevtoolsMcp", "chrome-devtools-mcp"],
  // sequential-thinking variants
  ["sequential_thinking", "sequential-thinking"],
  ["sequentialThinking", "sequential-thinking"],
]);

/**
 * Resolve a potentially aliased MCP tool name to its canonical form.
 *
 * Handles three known variant patterns that cause "unknown_tool" after IDE restart:
 *   1. `mcp__google-developer-knowledge__search_documents` (canonical ✓)
 *   2. `mcp_google-developer-knowledge_search_documents`  (single underscore separator)
 *   3. `mcp_google_developer_knowledge_search_documents`  (hyphens→underscores)
 *
 * Returns the input unchanged if it's already canonical or not an MCP tool name.
 */
export function resolveMcpToolAlias(toolName: string): string {
  // Already canonical format
  if (toolName.startsWith("mcp__")) {
    // Check if the server portion is an alias
    const parts = toolName.split("__");
    if (parts.length >= 3) {
      const serverPart = parts[1]!;
      const canonical = MCP_SERVER_ALIASES.get(serverPart);
      if (canonical) {
        parts[1] = canonical;
        return parts.join("__");
      }
    }
    return toolName;
  }

  // Single-underscore format: mcp_serverName_toolName
  // We need to try matching known server aliases from the prefix
  if (toolName.startsWith("mcp_")) {
    const withoutPrefix = toolName.slice(4); // strip 'mcp_'

    // Try each known alias (sorted longest first to avoid partial matches)
    const sortedAliases = [...MCP_SERVER_ALIASES.entries()].sort(
      (a, b) => b[0].length - a[0].length,
    );

    for (const [alias, canonical] of sortedAliases) {
      if (withoutPrefix.startsWith(alias + "_")) {
        const toolPart = withoutPrefix.slice(alias.length + 1);
        return `mcp__${canonical}__${toolPart}`;
      }
    }

    // Also try matching the canonical name with hyphens replaced by underscores
    // e.g., mcp_google-developer-knowledge_search_documents
    for (const [, canonical] of MCP_SERVER_ALIASES) {
      const canonicalAsUnderscore = canonical.replace(/-/g, "_");
      if (withoutPrefix.startsWith(canonical + "_")) {
        const toolPart = withoutPrefix.slice(canonical.length + 1);
        return `mcp__${canonical}__${toolPart}`;
      }
      if (withoutPrefix.startsWith(canonicalAsUnderscore + "_")) {
        const toolPart = withoutPrefix.slice(canonicalAsUnderscore.length + 1);
        return `mcp__${canonical}__${toolPart}`;
      }
    }
  }

  return toolName;
}

/**
 * Normalize server names to be compatible with the API pattern ^[a-zA-Z0-9_-]{1,64}$
 * Replaces any invalid characters (including dots and spaces) with underscores.
 *
 * For claude.ai servers (names starting with "claude.ai "), also collapses
 * consecutive underscores and strips leading/trailing underscores to prevent
 * interference with the __ delimiter used in MCP tool names.
 */
export function normalizeNameForMCP(name: string): string {
  let normalized = name.replace(/[^a-zA-Z0-9_-]/g, "_");
  if (name.startsWith(CLAUDEAI_SERVER_PREFIX)) {
    normalized = normalized.replace(/_+/g, "_").replace(/^_|_$/g, "");
  }
  return normalized;
}
