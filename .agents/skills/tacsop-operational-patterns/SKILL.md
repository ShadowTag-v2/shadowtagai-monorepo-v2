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

---

## Pattern 7: Jules Cloud Delegation Governance (TACSOP 8)

**When:** Pushing code to GitHub that will trigger Jules (the async Cloud COO), OR when reviewing infrastructure changes that Jules deployed.

**Rule:** Jules is NOT a local MCP tool. It is an asynchronous GitHub-triggered cloud agent that:
1. Authenticates via GCP Workload Identity Federation (WIF) — never static API keys
2. Spins up ephemeral Cloud VMs to review Spanner DDL and deploy Cloud Run/Firebase
3. Unleashes the Pomelli Swarm as its final action after successful deployment

**Governance Boundaries:**

| Boundary | Enforcement |
|----------|-------------|
| **Trigger Gate** | Jules is triggered ONLY by GitHub push events. Never invoke Jules directly. |
| **Auth Model** | WIF + `jules-action` in GitHub Actions. PEM/PAT auth is BANNED for Jules. |
| **Deployment Scope** | Jules deploys to Cloud Run + Firebase Hosting ONLY. No direct Spanner DDL execution without Judge 6 pre-approval. |
| **Rollback Authority** | If Jules deployment fails, Antigravity (local architect) must manually triage via Cloud Run revision rollback — Jules does NOT self-heal. |
| **Audit Trail** | All Jules-triggered deployments must be traceable in GitHub Actions logs. No shadow deployments. |

**Interaction Protocol:**
```
Antigravity (local) → git push → GitHub Actions → Jules (cloud) →
  → Deploy Cloud Run/Firebase → Unleash Pomelli Swarm →
  → Pomelli generates AST-Grep patches → Antigravity applies patches
```

**Anti-pattern:** Assuming Jules deployed correctly without verifying the live health endpoint. Always `curl /enclave/v1/health` after Jules completes.

---

## Pattern 8: Pomelli Swarm Oversight (TACSOP 9)

**When:** Pomelli Swarm is crawling live websites, OR when reviewing AST-Grep patches generated by Pomelli.

**Rule:** The Pomelli Swarm (`flpomp-team.git`) is a multi-agent A/B testing workforce powered by `gemini-3.1-flash-lite-preview`. It is NOT Google's public Pomelo product (brand DNA extractor). The two share a similar name but are architecturally distinct.

**Pomelli Identity Resolution:**

| Name | What It Is | Relationship |
|------|-----------|--------------|
| **Pomelli Swarm** | Custom `flpomp-team.git` multi-agent A/B testing fleet. Uses arXiv:2512.14982 test-time compute scaling. | Our product. Crawls 3 live sites. |
| **Google Pomelo** | Google Labs brand DNA extractor for small businesses. Generates social graphics from website URL. | External Google product. NOT our swarm. |

**Governance Boundaries:**

| Boundary | Enforcement |
|----------|-------------|
| **Model Restriction** | Pomelli agents run ONLY on `gemini-3.1-flash-lite-preview`. Never Opus, never thinking models. |
| **Physics Invariant** | arXiv:2512.14982 — prompt repetition + majority-voting for accuracy at flash-lite costs. |
| **Scope** | Crawls HeadFade, CounselConduit, ShadowTagAI live DOMs ONLY. No external sites. |
| **Patch Authority** | Pomelli GENERATES AST-Grep patches. It does NOT apply them. Antigravity (local architect) must review and apply. |
| **Brand Truth** | Pomelli reads Material 3 guidelines from NotebookLM MCP. No ad-hoc design decisions. |
| **FinOps Gate** | If BigQuery FinOps Governor reports unit economics inversion, Pomelli is automatically paused. |

**Failure Modes:**
1. Pomelli generates a patch that breaks tests → TACSOP 3 (Temporal-Reversal) applies
2. Pomelli crawls a site that's down → Log to `.beads/issues.jsonl`, skip site, continue
3. Pomelli's Lighthouse audit drops below P100 → Flag in nag protocol, escalate to STATE B

**Anti-pattern:** Treating Pomelli patches as pre-approved. Every Pomelli-generated patch MUST pass through the Omni-Linter Singularity (TACSOP 5) before commit.

---

## HeadFade Pivot Governance Addendum

**Effective:** 2026-05-18. The monorepo's active product focus has pivoted from pure Uphillsnowball infrastructure to **HeadFade** as the consumer revenue engine, with CounselConduit as the B2B complement.

**TACSOP Applicability:**
- All existing TACSops (0-7) apply to HeadFade development unchanged
- TACSOP 8 (Jules) and TACSOP 9 (Pomelli) apply exclusively to HeadFade's multi-tenant fleet
- Judge 6 acts as the shared compliance bridge between HeadFade and CounselConduit
- The 3-website multi-tenant fleet (HeadFade, CounselConduit, ShadowTagAI) shares the Spanner ledger and Hono/GraphQL backend
