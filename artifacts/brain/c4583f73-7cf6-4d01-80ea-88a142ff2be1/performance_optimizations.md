# Performance & Token Optimizations

**Agent:** 6 — Performance Optimizer
**Target:** `shadowtag-omega-v4`

System latency and token usage must be rigorously compressed to support a 650-Agent swarm architecture.

## 1. Token Efficiency (LLMLingua / JURA Tiers)

* **Problem:** Blindly passing 300-file contexts to 120 Flash Agents will exhaust rate limits and exponentially increase financial burn.
* **Optimization:** Implement the **JURA Protocol Routing Engine**.
  * `FREE Tier`: Route minor regex and format checks to local linters or `gemini-2.0-flash-lite`.
  * `FLASH Layer (90% load)`: Utilize `gemini-3-flash` for the bulk workforce. Limit context payloads strictly to the `workspace/` dependencies mapped iteratively by the `memory` MCP.
  * `PRO Layer (10% load)`: Retain `gemini-3-pro` exclusively for "Law School" grading, deep structural pivots, and initial orchestrator prompts.

## 2. Latency & Parallel Execution

* **Problem:** Sequential execution of 7-agent sweeps takes dozens of minutes (e.g. Mole background cache deletion taking 30m+).
* **Optimization:** Deploy Async Node / Tokio Python workers.
  * Agent 1, Agent 2, and Agent 5 can operate in complete parallel.
  * Agent 3 and Agent 6 depend on Agent 2's output.
  * By enforcing a strict Directed Acyclic Graph (DAG) using the `sequential-thinking` MCP, total mission time drops from `O(N)` to the depth of the longest dependency path.

## 3. Vector Retrieval Speed

* **Problem:** Generic RAG queries create sub-optimal recall on codebase patterns.
* **Optimization:** Use `WarpGrep` / `ast-grep` wrappers natively as tools *before* falling back to dense neural embeddings. Semantic AST search is 1000x faster than vector math for raw code patterns.

## 4. Cache Usage

* **Problem:** Re-computing common proofs (e.g., "Is `auth.ts` secure?").
* **Optimization:** Implement deep integration with the **Redis Agent Memory Server** or the Google Cloud equivalent. When the "Law School" Pro Agent approves a module, save the specific commit hash + file checksum to Redis. Future sweeps instantly skip re-evaluating unmodified files.
