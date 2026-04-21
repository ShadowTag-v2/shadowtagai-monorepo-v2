---
name: notebooklm-oracle
description: Enforces mandatory architectural context retrieval. Use before drafting flight plans, touching undocumented APIs, or starting any complex logic in the monorepo.
---

# NotebookLM Oracle Mandate

This skill ensures that you never guess domain logic, system constraints, or monorepo context in isolation. Context must be computed, never guessed.

## When to use this skill

- Before dropping into "Planning Mode" (STATE B / High Entropy execution).
- Before rolling out new architectures or mapping complex microservices.
- When encountering undocumented APIs or legacy backend services.
- Before creating or locking a `-plan.md` Amnesia shield.

## How to use it

### 1. The Canonical Source of Truth
Treat NotebookLM as the absolute canonical source of truth for the `ShadowTag-Omega-v4` monorepo. Do not guess system invariants.

### 2. Execute Mandatory Context-Sync
Before beginning code execution on a high-entropy task, you must explicitly use NotebookLM to extract the necessary architectural RAG payload. Do not architect or synthesize context in isolation.

Available context retrieval methods (in priority order):
1. **Knowledge Items (KIs)** — Check KI summaries at conversation start
2. **Conversation Logs** — Raw logs from past conversations in `<appDataDir>/brain/`
3. **NotebookLM MCP** — `uv tool install notebooklm-mcp-cli` (50 queries/day)
4. **Google Developer Knowledge MCP** — For Google API/SDK documentation
5. **LanceDB Local RAG** — `retriever_lancedb.py` for workspace-local search

### 3. Verify and Merge
- Synthesize the retrieved context.
- Validate your proposed flight plan strictly against this extracted research.
- Ensure the retrieved context is successfully merged into your internal logic map.
- Cross-reference KI artifacts against current codebase (KIs can become stale).

### 4. Execution Gate
You will not transition back to autonomous execution (STATE A) or write any code until the context validation is logically verified. DO NOT DEVIATE.

### 5. Integration with Existing Doctrine
- This skill supplements the `sequential-thinking` MCP for multi-step architectural decisions.
- The Hammock Protocol from `SIMPLICITY_DOCTRINE.md` applies: think BEFORE coding.
- The Rich Hickey doctrine applies: Simple (one-fold, unentangled) over Easy (familiar, at-hand).
