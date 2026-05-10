---
name: TACSOP Operational Patterns
description: Six operational patterns extracted from Cor.Antigravity TACSOP 2 (V15-V21) after full doctrinal audit on 2026-04-24. Only genuinely new, safe patterns that passed the disposition filter are included here.
---

<!-- GUARDRAIL: MODERATE-RISK skill. Contains Pattern 3 (Temporal-Reversal on Lint Failure)
     which uses git checkout -- <file>. All 6 patterns are bounded and audited.
     12 dangerous concepts were explicitly REFUSED during disposition. -->

# TACSOP Operational Patterns

**Source:** Cor.Antigravity TACSOP 2 (V15-V21), audited 2026-04-24
**Disposition:** 47 concepts already active, 12 refused (dangerous/prohibited), 5 no-op. These 6 patterns are the genuinely new additions.
**TACSOP 4 Kairos:** See `.agents/skills/kairos-zero-day-matrix/SKILL.md` for the Tri-Partite Cognitive Architecture and Patterns 7-9.

---

## Pattern 1: Asynchronous Cascade Execution

**When:** Executing a numbered list of 5+ sequential steps (e.g., deployment pipeline, multi-file refactor, CI/CD sequence).

**Rule:** Do NOT stop between steps unless blocked or failed. Continue execution through the entire list using `[STEP N/M]` markers for traceability.

**Implementation:**
```
[STEP 1/7] Creating database migration... ✅
[STEP 2/7] Running ruff check... ✅
[STEP 3/7] Deploying to staging... ✅
[STEP 4/7] Running integration tests... ❌ BLOCKED — auth token expired
→ HALT. Report blocker. Resume from STEP 4 after resolution.
```

**Anti-pattern:** Stopping after each step to ask "should I continue?" when the plan was already approved.

---

## Pattern 2: Execution Ledger Checkpoint

**When:** Multi-hour execution sessions, or any task with >10 discrete checkpoints.

**Rule:** Maintain a numbered checkpoint ledger in `task.md`. If context truncates or session resumes, fast-forward to the last `[x]` checkpoint instead of re-executing from scratch.

**Implementation:** This extends the existing `task.md` artifact pattern by adding:
- Numbered checkpoint IDs (not just bullet items)
- Timestamps on completion
- Explicit "resume from" markers

```markdown
## Execution Ledger
- [x] CP-01: Schema validated (18:12Z)
- [x] CP-02: Migration applied (18:15Z)
- [/] CP-03: Integration tests ← RESUME HERE
- [ ] CP-04: Deploy to staging
```

---

## Pattern 3: Temporal-Reversal on Lint Failure

**When:** `ruff check` or `biome lint` fails AFTER your edits, and the failure was introduced by the edit (not pre-existing).

**Rule:** Revert the specific files with `git checkout -- <files>`, fix the lint issue in isolation, then re-apply the original change with the fix included.

**CRITICAL:** Use `git checkout -- <files>` (safe, file-level) — NEVER `git reset --hard` (destructive, repo-level).

**Decision Tree:**
1. Edit files
2. Run lint → PASS? Continue normally
3. Lint FAIL?
   a. Was the error pre-existing? → Ignore (not your problem)
   b. Was the error introduced by your edit? → Revert, fix, re-apply
   c. Is the error a false positive? → Add targeted `# noqa` / `// biome-ignore`

---

## Pattern 4: Universal AST Evaluator

**When:** Running tests across multiple languages in the same session (Python + JS + Go + Rust).

**Rule:** Normalize all test outputs into a unified table before reporting to the user.

**Output Format:**
```markdown
| Language | Framework | Passed | Failed | Skipped | Duration |
|----------|-----------|--------|--------|---------|----------|
| Python   | pytest    | 480    | 0      | 3       | 12.4s    |
| TypeScript | vitest  | 67     | 2      | 0       | 3.1s     |
| Go       | go test   | 23     | 0      | 1       | 1.8s     |
| Rust     | cargo test| 15     | 0      | 0       | 4.2s     |
```

**Parsing rules:**
- pytest: Look for `X passed, Y failed, Z skipped` in final summary line
- vitest: Look for `Tests X | Failed Y | Skipped Z`
- go test: Count `--- PASS` and `--- FAIL` lines
- cargo test: Look for `test result: ok. X passed; Y failed; Z ignored`

---

## Pattern 5: Autoresearch Mutation Fitness

**When:** The autolint daemon (`gca_autolint_daemon.py`) or manual dead-code cleanup removes functions/imports.

**Rule:** Before committing the cleanup, run the test suite and compare execution time (`bench_ms`) against the pre-cleanup baseline. If execution time regresses by >5%, investigate before committing.

**Implementation:**
```bash
# Pre-cleanup baseline
/opt/homebrew/bin/python3.14 -m pytest --tb=no -q 2>&1 | tail -1  # Get timing

# Run cleanup
ruff check --select F401,F841 --fix .

# Post-cleanup measurement
/opt/homebrew/bin/python3.14 -m pytest --tb=no -q 2>&1 | tail -1  # Compare timing
```

**Threshold:** 5% regression = investigate. 10% regression = revert and analyze.

---

## Pattern 6: 8-Agent Board Synthesis

**When:** Making architecture decisions that affect >3 packages or involve security/payment/compliance changes (STATE B / Clutch triggers).

**Rule:** Before committing to the design, mentally evaluate from 8 perspectives. This extends the existing `rcr-code-reviewer` Council of Excellence with specific named roles:

| # | Role | Focus |
|---|------|-------|
| 1 | CTO / Architect | Structural integrity, tech debt, scalability |
| 2 | DX Engineer | Developer experience, API ergonomics, documentation |
| 3 | Security Engineer | Attack surface, privilege escalation, data exposure |
| 4 | Monetizer | Revenue impact, pricing implications, conversion effects |
| 5 | Platform / Infra | Cloud costs, deployment complexity, operational burden |
| 6 | QA Lead | Testability, regression risk, edge cases |
| 7 | Legal / Compliance | GDPR, PCI, Heppner privilege, regulatory exposure |
| 8 | End User Advocate | UX impact, cognitive load, accessibility |

**Output:** A single paragraph per role with APPROVE / CONCERN / BLOCK disposition. If any role BLOCKs, address before proceeding.

**When NOT to use:** Simple UI tweaks, config changes, documentation updates, or any task that stays in STATE A.
