# Feature Implementation

Structured workflow for implementing features with review checkpoints and evidence logging.

## Prerequisites
- Bootstrap alignment complete (run `/bootstrap-alignment` first)
- Feature spec exists in `docs/specs/` or user provides requirements

## Steps

1. **Spec Lock** — Write the feature specification to `docs/specs/<feature-name>.spec.md` if one does not exist. Include acceptance criteria, affected packages, and risk assessment.

// turbo
2. **Repo Oracle Check** — Run `scripts/repo-oracle "<feature-name>"` to verify no existing implementation.

3. **Plan** — Create an implementation plan. For changes >100 LOC, outline the approach before coding. Consider 2+ approaches.

4. **Implement** — Build the feature following dev standards:
   - Python: Google style, ruff at 90%
   - TypeScript: Google style, biome linting
   - Step 0 is deletion — remove dead code first

// turbo
5. **Lint** — Run `ruff check --fix . && ruff format .` for Python. Run `npx @biomejs/biome check --write .` for TypeScript.

// turbo
6. **Test** — Run `/opt/homebrew/bin/python3.14 -m pytest --tb=short -q` for Python tests.

7. **Evidence** — Log the implementation to `.agent/evidence/index.ndjson`:
   ```json
   {"timestamp":"<ISO>","action":"feature_implemented","feature":"<name>","files_changed":N,"tests_passing":N}
   ```

8. **Review Checkpoint** — Present the diff summary to the user. If STATE B criteria triggered (auth/payment/architecture >3 packages), pause for explicit approval.

## Completion Criteria
- All tests pass (no regressions from baseline 504 collected)
- Lint clean (ruff + biome)
- Evidence logged
- User review complete (STATE A auto-approve or STATE B explicit)
