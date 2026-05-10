# Magic Docs Engine

## Overview
Harvested from the `MagicDocs/` service, this skill defines the fallback behavior for when the Google Developer Knowledge MCP does not cover a specific framework or internal library.

## Protocol
1. If documentation is missing, the agent MUST fetch the remote documentation (e.g., via `curl` or browser automation).
2. The fetched documentation MUST be cached locally in `knowledge/magic_docs/`.
3. Only the most relevant snippets (extracted via `grep_search` or semantic search) should be injected into the context window to preserve the context budget.
