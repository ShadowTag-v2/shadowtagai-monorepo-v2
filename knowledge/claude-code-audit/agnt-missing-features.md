# Missing AGNT Features Implementation Specs

Based on the alignment table, the following 9 features present capability gaps in the AGNT framework that must be implemented:

1. **GrowthBook Dynamic Overrides:**
   - *Spec:* Implement \`tengu_*\` style feature flagging mapped through environment variables or a remote config fetched at session start. Needs caching with TTL to match \`getFeatureValue_CACHED_MAY_BE_STALE\`.

2. **Native AST Security Parsing (Tree-sitter):**
   - *Spec:* Replace basic regex parsing with a WASM-based AST parser to evaluate node semantics for bash commands, similar to \`parseForSecurityFromAst\`. Provide graceful degradation to "too-complex" state.

3. **Compound Command Sandboxing:**
   - *Spec:* Expand operator permission verification so pipeline commands (\`|\`, \`&&\`, \`||\`, \`>\`, \`>>\`) are split into subcommands, stripped of redirections, and independently checked against AST rules before execution.

4. **Multi-layer Context Compaction Pipeline:**
   - *Spec:* See \`DESIGN_agnt_context_compaction.md\` for the 4-layer architecture (Micro-compaction, Temporal, Consolidation, Pruning).

5. **Shadow Mode / Dark Launching:**
   - *Spec:* Implement \`killswitch\` execution models where untested parsers evaluate silently in the background and output metrics to telemetry without affecting the live execution state.

6. **Epistemic Airgapping via Safe Env Vars:**
   - *Spec:* Implement an \`ANT_ONLY_SAFE_ENV_VARS\` equivalent. Ensure environment variables passed into subcommands are safely stripped prior to matching exact or wildcard execution rules, preventing trivial bypasses.

7. **Session Branch Deduplication:**
   - *Spec:* Track conversation nodes as a graph instead of a flat log. Collapse redundant branches dynamically by keeping the branch with the most user messages/highest duration.

8. **VCR / Record-Replay Mode:**
   - *Spec:* Introduce deterministic replayability. Capture API requests to LLMs and tool execution outputs, allowing engineers to "playback" the exact environment context for debugging without burning token costs.

9. **TungstenTool (Virtual Terminal Abstraction):**
   - *Spec:* Implement a unified pseudo-terminal wrapper that prevents state collisions across agents using \`tmux\` socket isolation.
