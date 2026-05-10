---
description: Turn the regenerated plan into enforced reality and verify canonical state.
---

# /thread-canonicalize

**Purpose:** Write the surviving artifacts, retire duplicates, activate the intended control plane, verify runtime conformity, and produce a final canonical-state report.

> **CRITICAL STAGE 3 RULE:**
> Do not draft new architecture here unless verification proves the current one fails. Stage 3 is for enforcement and proof, not fresh ideation.

## Procedure

1. **Write canonical artifacts to disk**
   - Only write the surviving files from `docs/UPDATED_pnkln_PACK.md`.

2. **Activate the control plane**
   - Open `pnkln.code-workspace`.
   - Ensure `AGENTS.md` is the absolute behavior source.
   - Ensure `antigravity-mcp-config.json` is the sole MCP truth actually referenced.

3. **Retire competing surfaces**
   - Replace retired files with adapter/retired stubs.
   - Remove source-of-truth ambiguity.
   - Confirm no stale file is still loaded by editors/extensions.

4. **Verify runtime conformity**
   - Check that VS Code uses the intended workspace.
   - Verify Python interpreter resolves correctly.
   - Verify Jupyter uses the local kernel environment.
   - Ensure MCP config parses without errors.
   - Confirm `.env` provides the required secrets.
   - Ensure the LanceDB smoke test passes.
   - Ensure the Gemini API stream command template is correct.

5. **Audit live references**
   - Traverse the workspace to search for references to retired MCP paths.
   - Search for old naming conventions (`pnkln-stack`, `pnkln-stack`) where it should now strictly be `pnkln`.
   - Search for stale model names or inline secrets.
   - Search for archived/live-root contradictions.

6. **Freeze supersession**
   - Generate a definitive manifest mapping:
     - Canonical
     - Adapter-only
     - Retired
     - Forbidden to revive

7. **Produce proof**
   - Generate a concise evidence report with pass/fail gates per truth surface.

## Expected Stage 3 Output Format

A. Files written
B. Activation checks
C. Duplicate/retired surfaces neutralized
D. Runtime verification results
E. Remaining drift or blockers
F. Final canonical state
