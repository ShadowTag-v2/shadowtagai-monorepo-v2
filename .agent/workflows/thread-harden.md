---
description: Add automation and enforcement around the canonicalized workspace to prevent architectural drift.
---

# /thread-harden

**Purpose:** Secure the canonicalized workspace by executing structural preflight checks, CI verifications, root guards, and explicitly instructing subsequent agents on what not to touch.

> **STAGE 4 TRIGGER:**
> This protocol should be executed rapidly post-Canonicalization (Stage 3).

## Procedure

1. **CI and Linting Gates**
   - Rapid execution of code quality baselines (e.g. `npm run lint`, `npm run format`, `biome`, `ruff`).
   - Validate strict OWASP isolation standards where relevant.

2. **Root Guard Activation**
   - Run `scripts/pnkln_root_guard.sh` to prevent path execution failures and enforce execution bindings precisely within the canonical root paths.

3. **Pack and Verification Scripts**
   - Launch `scripts/verify_mcp.sh` to smoke test YAML/JSON syntax and external integrations.
   - Launch `scripts/audit_monorepo_state.sh` to calculate and certify that zero `<unresolved>` roots exist.
   - Validate completion of the manifest's definition of `canonicalization_complete_when`.

4. **Documentation and Immutable Zones**
   - Review or append strict doctrine limits to `AGENTS.md` and `.cursor/rules/cor-vibe-coding.mdc`.
   - Instruct future executions what exact files they are not permitted to modify unless specifically directed to change the control plane.
   - Enforce the "no second source of truth" absolute mandate.
