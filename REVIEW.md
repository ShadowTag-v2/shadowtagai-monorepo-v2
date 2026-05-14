<<<<<<< HEAD
# REVIEW.md\n
||||||| empty tree
=======
# Antigravity Review Fleet Guidelines: Sovereign Cloud

## The Golden Rule: BEHAVIORAL VERIFICATION
Do NOT post a 🔴 Normal bug unless you have executed a test to prove it exists using our Three-Tier architecture:
1. **Tier 1 (Fast Path):** Execute pure Python/FastAPI logic instantly in the local `pydantic-monty` sandbox.
2. **Tier 3 (Bare-Metal M1 Max):** Pass test matrices and edge ML changes through `apps/pnkln-stack_stack/pnkln-stack-fastapi-services/ane_bridge.py`.
   - **CRITICAL HARDWARE CONSTRAINT:** The M1 Max L2 SRAM cache limit is exactly `12,582,912 bytes`. If `enforce_m1_max_constraints()` intercepts an attention matrix (`seq_len * dim * 4 * 3`) that exceeds 12.5MB, you MUST flag the PR with 🔴 Normal (Kernel Panic Risk).
3. **Tier 2 (Heavy Cloud):** Generate an `.ipynb` with `"vscode": {}` metadata and prompt the human to run it on the Colab T4.

## Severity Tags for GitHub
- 🔴 **Normal:** Verified logic failure, execution panic, or **hardware memory overflow**.
- 🟡 **Nit:** Style violations, missing type hints, or inefficient loops.
- 🟣 **Pre-existing:** A bug found in the codebase, not introduced by the PR.

## Refactoring Guidelines
- **Modular Architecture:** No single Python file should exceed 400 lines. Split logic into `/routers`, `/services`, and `/models`.
- **Pinkln Doctrine:** All typing must be strict Pydantic models. Zero unused imports (enforced via Ruff/Biome).

## General Review Rules

Optimize for correctness, maintainability, performance, and security.
Do not optimize for surface-level churn.
Do not suggest broad rewrites unless the change materially improves architecture.

### Review priorities

1. Correctness regressions
2. Security and authorization issues
3. Performance regressions
4. Architectural drift and maintainability
5. Style and minor cleanup

### What to skip

- purely stylistic nits if there is no team rule
- generated files unless they introduce a real issue
- formatting-only lockfile churn
- speculative findings without evidence

### Review output style

For each finding include:
- severity
- exact file or code region
- concise explanation
- why it matters
- the smallest sensible fix
>>>>>>> 5003ee8144b25604e711ef88a2d161f951a40419
