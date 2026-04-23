---
name: Omni-Linter Singularity
description: Unifies ast-grep, ruff, biome, and gitleaks into a single deterministic AST-resolution pass.
---
# Omni-Linter Singularity

## 5-Pass Deterministic Pipeline

1. **Step 0 — DELETION.** Run `vulture` to locate dead code. Remove it.
2. **Step 1 — AST patterns.** Run `ast-grep` for arbitrary AST pattern eradication.
3. **Step 2 — Lint + fix.** Run `ruff check --fix --unsafe-fixes` repeatedly until stabilization.
4. **Step 3 — Secrets.** Gitleaks enforces secrets zero-trust. `gitleaks detect --no-banner`.
5. **Step 4 — Semantic analysis (opt-in).** When standard AST pass finds ambiguous results (e.g., dynamically referenced code, metaprogramming), dispatch a Deep Research query to resolve the ambiguity. Cost: $1–3 per query.

## Step 4 Details (Deep Research Integration)

Step 4 is triggered ONLY when:
- `vulture` reports dead code with confidence < 90%
- The dead code is in a dynamically-loaded module (plugin system, registry pattern)
- The developer passes `--deep-analysis` flag

When triggered:
1. Collect vulture output for confidence < 90% items
2. Formulate a research query: "Is {function_name} in {module_path} used transitively?"
3. Dispatch to `deep-research-preview-04-2026` via Interactions API
4. If Deep Research confirms the code is dead → delete
5. If Deep Research finds transitive usage → whitelist in `.vulture_whitelist.py`

## Execution Command

```bash
# Standard pass (free)
vulture src/ --min-confidence 90 && \
ast-grep scan --config .ast-grep.yml src/ && \
ruff check --fix --unsafe-fixes src/ && \
gitleaks detect --no-banner

# Deep analysis pass (costs $1-3)
python -m labs.uphillsnowball.src.intelligence.deep_research_client \
  --query "dead code analysis for {module}"
```
