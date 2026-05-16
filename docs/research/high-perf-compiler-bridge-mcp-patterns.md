# HighPerfCompilerBridge (daScript) MCP Server — Reference Architecture

**Source:** Gaijin Entertainment
**Relevance:** Compiler-backed MCP + Hot-Reload Patterns for the Autoresearch Triad.

## Chronological Adoption Plan

**Phase 1 (Immediate): Reference + Pattern Extraction**
*   **Action:** Clone upstream repo into `external_repos/upstream/execution/`. Document all 29 tools in `THIRD_PARTY_TAPESTRY.json`.
*   **Extraction:** Isolate the semantic hashing hot-reload pattern. This is critical: unchanged functions must stay Ahead-Of-Time (AOT) compiled, while changed functions gracefully fall back to the interpreter to avoid full rebuilds.

**Phase 2 (Weeks 1-2): Prototype**
*   **Action:** Implement 4–6 compiler-style tools into our Media MCP (`type_of(ki_id)`, `find_references(symbol)`, `diagnostics(ki_id)`, `eval_expression(expression)`).
*   **Execution:** Apply semantic hashing to unchanged Knowledge Items (KIs) during Dream Consolidation.

**Phase 3 (Month 2): Production Deployment**
*   **Action:** Expose a live-reload REST endpoint (port 9090 pattern).
*   **Integration:** Make the `SpreadingActivationCore` (Wander) and `HighPerfCompilerBridge` (daScript-style) tools available to the 8-Agent C-Suite via the MCP layer, allowing dynamic hot-swapping of agent logic without pipeline restarts.
