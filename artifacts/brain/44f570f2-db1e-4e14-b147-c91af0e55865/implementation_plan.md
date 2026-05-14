# Implementation Plan - Chrome DevTools MCP Multi-Session Upgrade

## Goal Description
Refactor the `chrome-devtools-mcp` server to support multiple concurrent sessions. Currently, `src/main.ts` uses a singleton `McpContext`, which limits the server to a single browser instance shared across all clients. The goal is to isolate sessions (likely by MCP session ID or client identifier) to prevent state conflicts and enable true multi-user/multi-agent support.

## User Review Required
> [!IMPORTANT]
> This change modifies the core entry point (`src/main.ts`) and context management (`src/McpContext.ts`) of the MCP server. It assumes that "Multi-Session" means supporting multiple isolated browser contexts dynamically.

## Proposed Changes

### Chrome DevTools MCP
#### [MODIFY] [src/main.ts](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/tools/chrome-devtools-mcp/src/main.ts)
- Remove the global `let context: McpContext;` singleton.
- Implement a `SessionManager` class or a `Map<string, McpContext>` to store contexts keyed by Session ID.
- Update `registerTool` to extract a Session ID (from request params or context) and retrieve/create the appropriate `McpContext`.
    - **Note:** Standard MCP tools don't pass Session ID by default. We might need to introspect `params._meta` or rely on the `McpServer` connection context if exposed.
    - *Fallback:* If Session ID is unavailable, default to a "default" session but structure the code to support multiple.

#### [MODIFY] [src/McpContext.ts](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/tools/chrome-devtools-mcp/src/McpContext.ts)
- Ensure `McpContext` can be instantiated multiple times safely (no global listeners or side effects).
- Verify `NetworkCollector` and `ConsoleCollector` are scoped to the `McpContext` instance.

## Verification Plan

### Automated Tests
- Run `npm test` in `tools/chrome-devtools-mcp` to ensure no regression.
- Create a new test case simulating multiple `McpContext` initializations.

### Manual Verification
- Connect two different MCP clients (or simulated clients) and verify they get distinct browser contexts (or at least valid distinct connections).
