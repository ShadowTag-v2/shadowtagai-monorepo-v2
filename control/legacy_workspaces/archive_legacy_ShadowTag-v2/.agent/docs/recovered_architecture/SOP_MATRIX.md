# SOP MATRIX - Standard Operating Procedures

## Overview

Four core SOPs govern all ANTIGRAVITY operations.

---

## SOP-A: Upload Triage

**Purpose:** Classify inbound requests, route to correct troop

### Flow

```

Inbound Request
    │
    ▼
┌─────────────────┐
│ Classify Type   │
├─────────────────┤
│ • Architecture  │ → AIR_CAV (PRO)
│ • Execution     │ → ALPHA/BRAVO/CHARLIE (FLASH)
│ • Security      │ → CODEPMCS (PRO)
│ • Governance    │ → HHT (PRO)
└─────────────────┘

```

### Classification Rules

| Type | Keywords | Troop |
|------|----------|-------|
| Architecture | design, structure, pattern, scale | AIR_CAV |
| Execution | implement, build, create, fix | ALPHA/BRAVO/CHARLIE |
| Security | scan, vulnerability, CVE, audit | CODEPMCS |
| Governance | review, approve, compliance | HHT |

---

## SOP-B: Change & Release

**Purpose:** GitOps flow, PR generation, CI/CD gates

### Pipeline

```

Code Change
    │
    ▼
┌─────────────────┐
│ 1. Scan (PMCS)  │ → Security check
│ 2. Review (HHT) │ → Governance gate
│ 3. PR Generate  │ → Auto-format
│ 4. CI/CD Check  │ → Build/Test
│ 5. Deploy       │ → Cloud Run
└─────────────────┘

```

### Gates

| Gate | Troop | Pass Condition |
|------|-------|----------------|
| Security | CODEPMCS | No HIGH/CRITICAL CVEs |
| Governance | HHT | Judge #6 APPROVED |
| Build | CI/CD | Exit code 0 |
| Test | CI/CD | All tests pass |

---

## SOP-C: Decision Protocol

**Purpose:** Consensus voting, 0% error via unanimity

### Voting Model

```

Task → 3+ Agents → Vote → Consensus

PASS: All agents agree
FAIL: Any dissent → Escalate to HHT

```

### Confidence Thresholds

| Confidence | Action |
|------------|--------|
| > 95% | Auto-execute |
| 70-95% | Execute with review |
| 50-70% | Request clarification |
| < 50% | Escalate to PRO tier |

### Lowest-Confidence Check

When model hits lowest confidence token in reasoning chain:

- Trigger immediate branch/review

- Predicts 75% of downstream errors

---

## SOP-D: Code Review

**Purpose:** CodePMCS + Judge #6 approval gates

### Review Stages

```

Code Submission
    │
    ▼
┌─────────────────────────────────────┐
│ Stage 1: CODEPMCS Scan              │
│   • Static analysis                 │
│   • Security vulnerabilities        │
│   • Code style compliance           │
├─────────────────────────────────────┤
│ Stage 2: Judge #6 Review            │
│   • Governance compliance           │
│   • Architecture alignment          │
│   • Risk assessment (ATP 5-19)      │
├─────────────────────────────────────┤
│ Stage 3: Auto-Remediation           │
│   • Fix detected issues             │
│   • Generate PR with fixes          │
│   • Request re-review               │
└─────────────────────────────────────┘

```

### Verdicts

| Verdict | Meaning | Action |
|---------|---------|--------|
| APPROVED | All gates pass | Merge allowed |
| CONDITIONAL | Minor issues | Merge with fixes |
| REJECTED | Major issues | Block merge |
| ESCALATE | Uncertain | Human review required |

---

## Quick Reference

| SOP | Purpose | Primary Troop |
|-----|---------|---------------|
| A | Upload Triage | AUTO |
| B | Change & Release | ALL |
| C | Decision Protocol | HHT |
| D | Code Review | CODEPMCS + HHT |

---

*Last updated: December 2, 2025*
*ANTIGRAVITY :: ULTRATHINK v2.0*
