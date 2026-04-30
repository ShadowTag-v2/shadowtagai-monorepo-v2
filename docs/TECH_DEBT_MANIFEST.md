# Technical Debt Manifest

> Canonical tracking document for all identified technical debt.
> Generated: 2025-04-11 | Audit: Invariant #67 + #90
> Status: **ACKNOWLEDGED** — push-ready with this contract.

## Executive Summary

| Category | Count | Owner | Priority |
|---|---|---|---|
| Syntax-broken files (quarantined) | 77 | `archive/broken/` | ✅ RESOLVED |
| Ruff lint errors (F401/F811/F841) | 0 | N/A | ✅ RESOLVED |
| Vulture dead code (100% confidence) | 134 | `apps/aiyou_stack/` | 🟡 Sprint 2 |
| Monolithic files (>500 LOC) | 256 | `apps/`, `labs/` | 🔴 Sprint 2-3 |
| Complected modules (>8 imports) | 481 | `apps/`, `tools/` | 🟡 Sprint 3 |
| Long functions (>50 LOC) | 2,086 | All dirs | 🟡 Sprint 3-4 |
| Hardcoded configs (localhost:) | 113 | `apps/` | 🟡 Sprint 2 |
| console.log in production | 3,516 | `apps/` (vendored) | 🟢 Low |
| Dead links (href="#") | 6 | `apps/` | 🟢 Low |

---

## Phase 1 Completed: Auto-Fix ✅

- **181 unused imports (F401)** removed via `ruff --fix` across `apps/`, `labs/`, `tools/`, `scripts/`
- Post-test: 0 regressions in app-owned code
- Ruff now reports **0 issues** for F401/F811/F841

## Phase 2 Completed: Syntax Error Quarantine ✅

**77 files** with unfixable syntax errors moved to `archive/broken/`:

### Error Taxonomy
| Pattern | Count | Root Cause |
|---|---|---|
| `ShadowTag-v2` in Python identifiers | ~30 | Hyphens invalid in Python names |
| `n-autoresearch` in Python identifiers | ~10 | Same hyphen issue |
| `REDACTED_USER:REDACTED_PASS` artifacts | ~5 | Credential scrubbing broke syntax |
| Incomplete/scaffolded vibe code | ~32 | Never compiled or tested |

### Quarantine Layout
```
archive/broken/
├── aiyou_fastapi_agents/      (11 files)
├── aiyou_fastapi_scripts/     (9 files)
├── aiyou_fastapi_src/         (21 files)
├── aiyou_fastapi_apps_src/    (5 files)
├── aiyou_fastapi_misc/        (24 files)
├── legaltrack/                (1 file)
├── thermal_ride/              (2 files)
├── scripts_legacy/            (1 file)
└── (3 standalone files)
```

> [!IMPORTANT]
> These files were **never functional**. Moving them does not break any runtime behavior.

---

## Phase 3: Dead Code Removal (Sprint 2 Target)

### Vulture 100% Confidence (134 items)

Top candidates for removal:

| File | Line | Issue |
|---|---|---|
| `antigravity.py` | 70 | unused `stream_name` |
| `enterprise_compliance_api.py` | 758 | unused `certificate_hash` |
| `mcp_bridge.py` | 96 | unused `target_bytes` |
| `decision.py` | 48 | unused `__context` |
| `validation_service.py` | 355 | unused `coverage_threshold` |
| `judge_csrmc.py` | 189 | unreachable code after `return` |
| `swarm_endpoint.py` | 25 | unused imports `SwarmVoter`, `VoteDecision` |
| `orchestrator.py` | 232/262 | unused `llm_backend`, `track_metrics` |
| `layers.py` | 357/408 | unused `multi_silicon_mix`, `sbom` |

> Full list: `.reports/vulture-20260411T172239.txt`

---

## Phase 4: Monolith Refactoring Targets (Sprint 2-3)

### Top 15 Monoliths (by LOC)

| File | LOC | Refactoring Plan |
|---|---|---|
| `apps/pnkln/core/ecosystem.py` | 1,240 | Split: config/, orchestrator/, lifecycle/ |
| `pnkln/core/gemini_ingestion_layer.py` | 1,100+ | Extract: ingestion/, validation/, storage/ |
| `ultrathink_framework.py` | 1,015 | Separate: prompts, chains, formatters |
| `atomic_consensus_orchestrator.py` | 988 | Extract: voting, consensus, persistence |
| `src/agents/claude_code.py` | 954 | Split agent logic from HTTP transport |
| `ts-src/agents/claudeCode.ts` | 947 | Mirror Python refactoring |
| `rsta_squadron.py` | 932 | Decompose per-agent modules |
| `cor_orchestrator.py` | 922 | Extract: pipeline, routing, error handling |
| `multi_agent_debate.py` | 912 | Separate: debate protocol, scoring, history |
| `judge6/nodes.py` | 907 | Extract per-node modules |
| `walt/mcp_server.py` | 865 | Split: tools, handlers, config |
| `mitmproxy_ultra.py` | 862 | Extract: interceptors, transforms, logging |
| `enterprise_compliance_api.py` | 834 | Split per-domain routers |
| `california_ai_comprehensive.py` | 813 | Extract: rules engine, predicates, reporting |
| `salesforce_adapter.py` | 803 | Separate: auth, CRUD, sync |

### Duplicate Monoliths (code clones)
- `cor_orchestrator.py` exists in 4 locations (907 LOC × 4)
- `enterprise_compliance_api.py` exists in 3 locations (820-834 LOC × 3)
- `mcp_bridge.py` duplicated across `app/` and `apps/app/`

> [!WARNING]
> Deduplication should happen **before** refactoring to avoid doing the work twice.

---

## Phase 5: Complected Module Decomposition (Sprint 3)

### Top App-Owned Complected Files

| File | Import Sources | Decomposition Target |
|---|---|---|
| `apply_re_punch.py` | 33 | Break into domain-specific sub-modules |
| `pnkln/core/ecosystem.py` | 25+ | Already in monolith list |
| Various `pnkln/governance/` | 15-20 | Extract per-layer modules |

---

## Hardcoded Config Centralization (Sprint 2)

**113 instances** of `localhost:` in non-test code.

Remediation: Create `config/defaults.py` with environment-variable-backed defaults:
```python
import os
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
```

---

## Metrics Baseline

| Metric | Value | Target |
|---|---|---|
| Python files (app-owned) | 7,465 | — |
| Test-to-source ratio | 11.9% | 30% |
| Syntax errors (app-owned, post-quarantine) | 0 | 0 ✅ |
| Ruff F401/F811/F841 | 0 | 0 ✅ |
| Vulture 100% confidence | 134 | 0 |
| Monoliths (>500 LOC) | 256 | <50 |

---

## Reports Archive

All machine-readable reports in `.reports/`:
- `ruff-20260411T172239.txt`
- `vulture-20260411T172239.txt`
- `vibe-code-20260411T172239.txt`
- `dead-code-pre-20260411T172239.txt`
- `dead-code-post-20260411T172239.txt`
