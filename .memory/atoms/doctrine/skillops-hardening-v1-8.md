# v1.8 Hardening Milestone — SkillOps Security Triage

**Type:** milestone
**Created:** 2026-04-28
**Version:** v1.8

## What Changed

The SkillOps subsystem was hardened with a dangerous-pattern security scanner,
full triage of all findings, CI gating, and integration into the operational heartbeat.

## Key Metrics

| Metric | Value |
|--------|-------|
| Total skills audited | 271 active |
| Dangerous patterns scanned | 22 distinct patterns |
| Total findings | 44 |
| ACTUAL RISK | 12 (27%) — 6 skills |
| MODERATE RISK | 12 (27%) — 6 skills |
| DOC REFERENCE (false positive) | 20 (45%) — 20 skills |
| Beads issues seeded | ISSUE-018, ISSUE-019 (high priority) |
| CI gate deployed | `.github/workflows/skillops-audit.yml` |
| Heartbeat probe | Subsystem 10/10 (SkillOps) |

## Infrastructure Delivered

1. **Security Scanner:** `scripts/skills-audit.sh` — 22-pattern regex scanner
2. **Triage Report:** `.reports/skills/unsafe_findings.md` — categorized findings
3. **CI Gate:** `.github/workflows/skillops-audit.yml` — PR gate with threshold
4. **Heartbeat Probe:** Subsystem 10/10 in `scripts/monorepo-heartbeat.sh`
5. **Clone Yard:** `agent_protocols` group pulled (7 repos: MCP spec, MCP servers, LangGraph, LiteLLM, Browser-Use, Stagehand, Chrome DevTools MCP)
6. **Beads Issues:** ISSUE-018 (repo-mass-reduction), ISSUE-019 (yolo-mode-operator)

## Top Priority Skills for Remediation

1. `repo-mass-reduction` — 3 destructive patterns (reset, force-push, rm -rf)
2. `yolo-mode-operator` — 2 patterns (unrestricted mode + rm -rf)
3. `daemon-fleet-manager` — 2 patterns (reset + rm -rf)
4. `temporal-rollback-doctrine` — 3 patterns (inherent to rollback ops)
