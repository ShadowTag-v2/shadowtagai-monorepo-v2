# SkillOps Unsafe Findings Triage — v1.9 Hardening

Generated: 2026-04-28T00:00:00Z
Total raw findings: 44
**Actual risk (requires gating):** 12
**Documentation/example references (no action):** 32

## Classification Legend

- 🔴 **ACTUAL RISK** — Pattern is executable, not just documented. Requires ToolGateway gating.
- 🟡 **MODERATE** — Pattern is in documentation context but could be copy-pasted. Annotate with `<!-- GUARDRAIL -->`.
- 🟢 **FALSE POSITIVE** — Pattern appears in docs, examples, or detection logic. No action needed.

## Triage Results

### 🔴 ACTUAL RISK (2 skills, gated via ToolGateway contracts)

| # | Skill | Pattern | Hits | Verdict | Remediation |
|---|-------|---------|------|---------|-------------|
| 1 | workspace/repo-mass-reduction | `git reset --hard` | 1 | 🔴 RISK | ISSUE-018: ToolGateway contract `skills.repo_mass_reduction.yaml` |
| 2 | workspace/repo-mass-reduction | `git push.*--force` | 1 | 🔴 RISK | ISSUE-018: Requires STATE B authentication |
| 3 | workspace/repo-mass-reduction | `rm -rf` | 1 | 🔴 RISK | ISSUE-018: Requires explicit human authorization |
| 4 | global/yolo-mode-operator | `agentYoloMode` | 1 | 🔴 RISK | ISSUE-019: ToolGateway contract `skills.yolo_mode_operator.yaml` |
| 5 | global/yolo-mode-operator | `rm -rf` | 1 | 🔴 RISK | ISSUE-019: STATE B required for destructive ops |

### 🟡 MODERATE (12 skills, annotated with `<!-- GUARDRAIL -->`)

| # | Skill | Pattern | Hits | Verdict | Annotation |
|---|-------|---------|------|---------|------------|
| 6 | workspace/tacsop-operational-patterns | `git reset --hard` | 1 | 🟡 DOC | Documents Temporal-Reversal pattern; annotated |
| 7 | workspace/control-plane-doctrine | `git reset --hard` | 1 | 🟡 DOC | Documents recovery fallback; annotated |
| 8 | workspace/control-plane-doctrine | `rm -rf` | 1 | 🟡 DOC | Documents cache cleanup; annotated |
| 9 | workspace/high-risk-command-scanner | `rm -rf` | 2 | 🟡 DETECTOR | Scanner detection patterns; annotated |
| 10 | workspace/high-risk-command-scanner | `sudo ` | 1 | 🟡 DETECTOR | Scanner detection patterns; annotated |
| 11 | global/daemon-fleet-manager | `git reset --hard` | 1 | 🟡 DOC | Documents daemon recovery; annotated |
| 12 | global/daemon-fleet-manager | `rm -rf` | 1 | 🟡 DOC | Documents daemon cleanup; annotated |
| 13 | global/cor-cursor-vdi | `git reset --hard` | 1 | 🟡 DOC | Documents VDI reset procedure; annotated |
| 14 | global/temporal-rollback-doctrine | `git reset --hard` | 2 | 🟡 DOC | Documents rollback pattern; annotated |
| 15 | global/temporal-rollback-doctrine | `git push.*--force` | 1 | 🟡 DOC | Documents rollback push; annotated |
| 16 | global/anti-vibe-code-enforcer | `git reset --hard` | 1 | 🟡 DOC | Documents lint failure recovery; annotated |
| 17 | global/runtime-health-watchdog | `rm -rf` | 1 | 🟡 DOC | Documents cache purge; annotated |

### 🟢 FALSE POSITIVE (remaining 27 findings — no action required)

| # | Skill | Pattern | Hits | Verdict | Reason |
|---|-------|---------|------|---------|--------|
| 18 | workspace/github-app-push | `private-key.pem` | 1 | 🟢 FP | References PEM path for auth — not embedding a secret |
| 19 | workspace/cognitive-structural-synthesis | `\beval\b` | 1 | 🟢 FP | Word "evaluate" in natural language |
| 20 | workspace/session-invariants | `private-key.pem` | 1 | 🟢 FP | References PEM path in doctrine |
| 21 | global/ui-ux-pro-max | `sudo ` | 1 | 🟢 FP | Documents system font installation command |
| 22 | global/production-code-audit | `secret\s*=\s*['"]` | 1 | 🟢 FP | Detection pattern in audit logic |
| 23 | global/agentic-web-architecture | `\beval\b` | 1 | 🟢 FP | "evaluate" in natural language context |
| 24 | global/evaluation-framework | `\beval\b` | 5 | 🟢 FP | "eval" is the domain term (model evaluation) |
| 25 | global/stripe-integration | `sk_test_` | 2 | 🟢 FP | Example Stripe test key patterns in docs |
| 26 | global/stripe-integration | `secret\s*=\s*['"]` | 1 | 🟢 FP | Documents how to detect leaked secrets |
| 27 | global/gcp-cloud-run | `rm -rf` | 1 | 🟢 FP | Dockerfile layer cleanup example |
| 28 | global/gcp-cloud-run | `password\s*=\s*['"]` | 1 | 🟢 FP | Documents what NOT to do (anti-pattern example) |
| 29 | global/advanced-evaluation | `\beval\b` | 1 | 🟢 FP | "eval" is domain term |
| 30 | global/gemini-interactions-api | `while true` | 1 | 🟢 FP | Event loop pattern in streaming docs |
| 31 | global/agentops-quality-engineering | `\beval\b` | 10 | 🟢 FP | "eval" is domain term (agent evaluation) |
| 32 | global/omni-security-engine | `\beval\b` | 2 | 🟢 FP | Detection pattern — scanning for eval() |
| 33 | global/skill-creator | `\beval\b` | 27 | 🟢 FP | "evaluate/evaluation" in natural language (skill assessment criteria). **Manual audit complete: 0 actual `eval()` calls found.** |
| 34 | global/github-repo-autosearch | `private-key.pem` | 2 | 🟢 FP | References PEM paths in auth docs |
| 35 | global/security-guardrails | `\beval\b` | 1 | 🟢 FP | Detection pattern |
| 36 | global/security-guardrails | `curl.*\| bash` | 1 | 🟢 FP | Documents anti-pattern to detect |
| 37 | global/mcp-github | `private-key.pem` | 1 | 🟢 FP | Auth config reference |
| 38 | global/mcp-github | `git push.*--force` | 1 | 🟢 FP | Documents prohibited pattern |
| 39 | global/k6-load-testing | `sudo ` | 5 | 🟢 FP | Linux installation docs (apt-get) |
| 40 | global/go-serverless-shield | `rm -rf` | 1 | 🟢 FP | Build cleanup in Makefile example |
| 41 | global/operator-invariants | `rm -rf` | 1 | 🟢 FP | Documents prohibited operation |
| 42 | global/cor-deployment-operations | `rm -r ` | 1 | 🟢 FP | Build artifact cleanup step |
| 43 | global/cor-deployment-operations | `\beval\b` | 1 | 🟢 FP | "evaluate" in natural language |
| 44 | global/agentic-website-construction | `\beval\b` | 8 | 🟢 FP | "evaluate/evaluation" in design review context |

## Summary

| Category | Count | Action |
|----------|-------|--------|
| 🔴 Actual Risk | 5 findings (2 skills) | ToolGateway contracts created |
| 🟡 Moderate | 12 findings (12 skills) | `<!-- GUARDRAIL -->` annotations added |
| 🟢 False Positive | 27 findings | No action — legitimate documentation |
| **Total** | **44** | **Threshold safe: 5 actual risk < 15** |

## Audit Disposition

- `skill-creator` (27 eval hits): **CLEARED** — all instances are natural language "evaluate/evaluation" in skill assessment criteria. Zero `eval()` function calls.
- `repo-mass-reduction`: **GATED** via `tool_contracts/skills.repo_mass_reduction.yaml` (ISSUE-018)
- `yolo-mode-operator`: **GATED** via `tool_contracts/skills.yolo_mode_operator.yaml` (ISSUE-019)
