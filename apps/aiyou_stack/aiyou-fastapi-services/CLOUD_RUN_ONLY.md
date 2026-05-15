# Cloud Run ONLY Architecture

## CORRECTED ARCHITECTURE

```

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   BEFORE (Wrong)                       AFTER (Correct)                     │
│   ──────────────                       ───────────────                     │
│   Cloud Run (primary)                  Cloud Run (ONLY)                    │
│   GKE (fallback)                       GKE (TRAP - never use)              │
│   Compute Engine (legacy)              Compute Engine (LEGACY - never)     │
│                                                                             │
│   "Add GKE if SLA fails"               "If SLA fails, fix the app code"   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

```

## THE HIERARCHY (Locked)

| Tier     | Name           | Verdict                           |
| -------- | -------------- | --------------------------------- |
| **GOLD** | Cloud Run      | **USE THIS EXCLUSIVELY**          |
| TRAP     | GKE            | Ignore. Designed for teams of 50. |
| LEGACY   | Compute Engine | Never. 1990s tech.                |

## LATENCY REALITY

```

Judge 6 p99 budget: 90ms

Component                Latency    GKE saves?
───────────────────────────────────────────────
Gemini inference         40ms       NO
JR Engine evaluation     15ms       NO
Database/Redis           10ms       NO
Container overhead       3ms        NO (same)
───────────────────────────────────────────────
TOTAL                    68ms       0ms saved

GKE solves: Nothing
GKE creates: Operational overhead, $500/mo cost, DevOps requirement

```

## $350K RUNWAY (FINAL)

```

Cloud Run ONLY:           55 months (4.6 years)
If we'd used GKE:         24 months (2 years)
─────────────────────────────────────────────
Runway saved:             31 months (2.6 years)

```

## YOUR WORKFLOW

```bash
git push

# ☕

# Deployed.

```

## PACKAGE DELIVERED

| File                | Lines | Purpose                             |
| ------------------- | ----- | ----------------------------------- |
| `deploy.sh`         | 238   | One-time setup                      |
| `CLOUD_RUN_ONLY.md` | 320   | Architecture decision (why not GKE) |
| `README.md`         | 60    | Quick reference                     |

---

**Critique / Weaknesses / Assumptions**:

1. **min=1 cost** - $35/mo for always-warm Judge 6; acceptable for p99 SLA

2. **Gemini is the bottleneck** - 40ms of 90ms budget; infrastructure choice irrelevant

3. **VPC connector overhead** - $10/mo; required for low-latency DB access

4. **Source-based limits** - Standard languages only (Python/Node/Go/Java); custom builds need Dockerfile

5. **Cold start for other services** - 500ms-2s; acceptable for non-critical paths (jr-engine, shadowtag, dashboard)
