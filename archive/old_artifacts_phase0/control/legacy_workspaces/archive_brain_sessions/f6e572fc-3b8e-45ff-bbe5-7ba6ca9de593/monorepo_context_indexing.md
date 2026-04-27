# Monorepo Context Cache Indexing Strategy

To achieve true global agent inference with near-zero prefill latency and massive cost savings (the Aegaeon Protocol), we must index the *entire* Monorepo codebase into a single Gemini Context Cache slab.

Here is the strategic outline for achieving this scale.

## 1. The AST Compilation Sweep

You cannot simply concatenate files together. The LLM loses structural context. We must compile the codebase into an Abstract Syntax Tree (AST) representation or a highly structured markdown digest.

**Implementation:**
*   **The Sweeper Daemon:** A python script (e.g., `scripts/compile_monorepo_ast.py`) runs periodically or via a Git hook.
*   **Exclusions:** It rigorously ignores `/external_sdks`, `/tools/legacy`, `.beads`, `.venv`, `node_modules`, and binary heavy assets.
*   **Formatting:** Each file is appended to a massive `MONOREPO_STATE.md` artifact using the following format:
    ```markdown
    # File: apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services/ane_bridge.py
    ## Path: /Users/pikeymickey/...
    ## Type: python
    ```python
    [Full Source Code]
    ```
    ```
*   **Metadata:** Essential metadata (latest commit hashes, active JIRA tags) are prepended to the top of the file.

## 2. Pumping the Cache Slab

Once `MONOREPO_STATE.md` is compiled, it will represent hundreds of thousands of tokens.

**Implementation:**
*   **The Cache Manager:** A dedicated service uploads `MONOREPO_STATE.md` to the Google GenAI API using `client.caches.create`.
*   **The Pointer:** Google returns a Cache ID (e.g., `cached_monorepo_v8`).
*   **The Registry:** The Cache Manager writes this ID to a local lockfile (e.g., `.agent_state/active_cache_id.json`) or environment variable.

## 3. Global Inference Routing

Every single tool in the Antigravity stack that requires LLM reasoning now routes through the central registry.

**Implementation:**
*   **Swarm Webhooks:** When `webhook_pr_review.py` triggers, it reads `active_cache_id.json` and points all 7 parallel agents exactly at that `cached_content`.
*   **CLI Tools:** When the user asks a deep architectural question via the terminal, the CLI tool retrieves the active Cache ID. The LLM instantly has perfect recall of the entire Monorepo without needing to grep or search.
*   **The Delta Push:** The only context sent in the actual API call is the *User Prompt* and any *Uncommitted Diffs* (since the cache represents the static codebase at the time it was compiled).

## 4. Cache Invalidation and Refresh

Caching isn't free. The TTL (Time-To-Live) and refresh cycles must be managed carefully.

**Implementation:**
*   **Nightly Build:** Compile the AST and pump the Cache automatically at 3:00 AM.
*   **Trigger Warning:** If the Swarm Router detects that `HEAD` has drifted too far from the Cache's compiled state (e.g., significant refactors), it triggers a blocking rebuild of the Cache Slab before executing PR reviews.
*   **Garbage Collection:** Ensure older caches are explicitly deleted via `client.caches.delete(name=cache.name)` to prevent ghost billing on Google Cloud.
