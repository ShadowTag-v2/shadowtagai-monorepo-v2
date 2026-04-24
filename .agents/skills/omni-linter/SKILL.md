---
name: Omni-Linter Singularity
description: Unifies ast-grep, ruff, biome, and gitleaks into a single deterministic AST-resolution pass.
---
# Omni-Linter Singularity

## 4-Pass Deterministic Pipeline (V22 Pruned Singularity)

1. **Step 0 — DELETION.** Run `ruff check --select F401,F841 --fix` to locate and remove dead code (unused imports + unused variables). V22: vulture pruned — ruff F401/F841 subsumes.
2. **Step 1 — AST patterns.** Run `ast-grep` for arbitrary AST pattern eradication.
3. **Step 2 — Lint + fix.** Run `ruff check --fix --unsafe-fixes` repeatedly until stabilization.
4. **Step 3 — Secrets.** Gitleaks enforces secrets zero-trust. `gitleaks detect --no-banner`.
5. **Step 4 — Semantic analysis (opt-in).** When standard AST pass finds ambiguous results (e.g., dynamically referenced code, metaprogramming), dispatch a Deep Research query to resolve the ambiguity. Cost: $1–3 per query.

## Step 4 Details (Deep Research Integration)

Step 4 is triggered ONLY when:
- Ruff F401/F841 reports dead code that may be dynamically loaded
- The dead code is in a dynamically-loaded module (plugin system, registry pattern)
- The developer passes `--deep-analysis` flag

When triggered:
1. Collect ruff F401/F841 output for ambiguous items
2. Formulate a research query: "Is {function_name} in {module_path} used transitively?"
3. Dispatch to `deep-research-preview-04-2026` via Interactions API
4. If Deep Research confirms the code is dead → delete
5. If Deep Research finds transitive usage → add `# noqa: F401` with justification comment

## Execution Command

```bash
# Standard pass (free) — V22 Pruned Singularity
ruff check --select F401,F841 --fix src/ && \
ast-grep scan --config .ast-grep.yml src/ && \
ruff check --fix --unsafe-fixes src/ && \
gitleaks detect --no-banner

# Deep analysis pass (costs $1-3)
python -m labs.uphillsnowball.src.intelligence.deep_research_client \
  --query "dead code analysis for {module}"
```
