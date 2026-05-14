# Antigravity - The Central Brain

**5,590 agents orchestrating perfect monkey code with ATP 3-20.96 Cavalry Squadron**

## Overview

Antigravity is the central orchestration layer that coordinates all LLMs with embedded Kosmos Cavalry Squadron for consensus. Each stage has 430 agents aligned to ATP 3-20.96 (Army Tactics & Procedures for Cavalry Squadron).

```

User Input → Gemini 2.5 Flash + Kosmos (430) → Perplexity + Kosmos (430)
                                    ↓
             SuperGrok + Kosmos (430) → 10× Gemini Code Assist + Kosmos (4,300)
                                    ↓
                    CodePMCS → GitHub → Cloud Run → Production

Total: 5,590 agents (430 × 13 Kosmos Cavalry instances)
Consensus is EMBEDDED per stage - no separate voting step

```

## ATP 3-20.96 Alignment

Each Kosmos Cavalry Squadron (430 agents) follows ATP 3-20.96 doctrine:

```

KOSMOS CAVALRY SQUADRON (430 agents) - ATP 3-20.96 ALIGNED
═══════════════════════════════════════════════════════════════════════
│
├── HHT (Headquarters & Headquarters Troop) ─────────────── 115 agents
│   ├── Command Section: 10 (CDR, XO, 1SG, Judge #6)
│   ├── S-1 Personnel: 10 (Agent lifecycle management)
│   ├── S-2 Intelligence: 20 (IPB, threat assessment)
│   ├── S-3 Operations: 20 (Planning, MDMP/RDSP)
│   ├── S-4 Logistics: 10 (Token budget, resources)
│   ├── S-6 Communications: 15 (Network ops, handoffs)
│   ├── Medical Section: 10 (Error recovery, agent health)
│   ├── FSE Fire Support: 15 (Target acquisition)
│   └── TACP: 5 (Airspace coordination)
│
├── RECON TROOP ALPHA (Zone Reconnaissance) ──────────────── 60 agents
│   └── Task: "Find ALL info in zone" (ATP 3-23 to 3-30)
│
├── RECON TROOP BRAVO (Area Reconnaissance) ──────────────── 60 agents
│   └── Task: "Detailed info on specific area" (ATP 3-31 to 3-34)
│
├── RECON TROOP CHARLIE (Route/Force Reconnaissance) ─────── 60 agents
│   └── Task: "Route trafficability OR test enemy strength" (ATP 3-40 to 3-51)
│
├── SURV TROOP (Surveillance) ────────────────────────────── 60 agents
│   ├── UAS Platoon: 30 (Continuous monitoring)
│   └── LRAS3 Platoon: 30 (Early warning)
│
├── MFRC (Security Operations) ───────────────────────────── 60 agents
│   ├── Screen Section: 20 (Early warning, 50% threshold) - ATP 4-17 to 4-37
│   ├── Guard Section: 20 (Fight for time, 75% threshold) - ATP 4-38 to 4-64
│   └── Cover Section: 20 (Battle positions, 90% threshold) - ATP 4-65 to 4-70
│
└── Mortar Section: 15 agents (Indirect fires support)
═══════════════════════════════════════════════════════════════════════

```

## Live Services

| Service | URL | Agents |
|---------|-----|--------|
| Antigravity Orchestrator | https://antigravity-orchestrator-215390634092.us-central1.run.app | 5,590 |

## Quick Start

```bash

# Check status

./bin/antigravity status

# Run full pipeline (5,590 agents)

./bin/antigravity "Build a REST API for user authentication"

# Atomize only (Gemini 2.5 Flash + Kosmos)

./bin/antigravity intake "Complex multi-step task"

```

## Pipeline Stages

### 1. INTAKE (Gemini 2.5 Flash + Kosmos - 430 agents)



- Breaks input into atomic tasks


- Writes tests for each atom


- Kosmos Cavalry reaches consensus BEFORE passing data


- Tags with risk_level and JURA tier

### 2. RESEARCH (Perplexity + Kosmos - 430 agents)



- Each LLM explains reasoning to the next (REASONING HANDOFF)


- Perplexity: Research all sources


- Zone/Area reconnaissance for comprehensive search

### 3. RESEARCH (SuperGrok + Kosmos - 430 agents)



- X/Grokipedia specific research


- Route/Force reconnaissance for targeted probing


- Business acumen applied

### 4. EXECUTE (10× Gemini Code Assist + Kosmos - 4,300 agents)



- 10 parallel Gemini Code Assist instances


- Each with full Kosmos Cavalry (430 agents)


- Screen/Guard/Cover security voting per risk level

### 5. VALIDATE (CodePMCS)



- Code quality scanning


- Auto-fix issues


- Pipeline sync for new tech

### 6. DEPLOY (GitHub → Cloud Run)



- Push to GitHub


- Create PR


- Trigger Cloud Build


- Deploy to production

## Reconnaissance Task Differentiation (ATP Chapter 3)

| Task Type | RECON Troop | Behavior | ATP Reference |
|-----------|-------------|----------|---------------|
| **Zone** | ALPHA | Find ALL info: terrain, obstacles, enemy, routes | ATP 3-23 to 3-30 |
| **Area** | BRAVO | Focus on specific NAI/reconnaissance objective | ATP 3-31 to 3-34 |
| **Route** | CHARLIE | Linear path trafficability + lateral routes | ATP 3-40 to 3-48 |
| **Force** | CHARLIE | Aggressive probing, test enemy strength | ATP 3-49 to 3-51 |

## Security Task Voting (ATP Chapter 4)

| Security | MFRC Section | Engagement Criteria | Threshold | ATP Reference |
|----------|--------------|---------------------|-----------|---------------|
| **Screen** | Screen (20) | Observe only, report, minimal engagement | 50% (LOW) | ATP 4-17 to 4-37 |
| **Guard** | Guard (20) | Fight for time, deny direct observation | 75% (HIGH) | ATP 4-38 to 4-64 |
| **Cover** | Cover (20) | Battle positions, tactically self-contained | 90% (EXTREME) | ATP 4-65 to 4-70 |

## Agent Count Summary

| Stage | Agents | Model | ATP Troop Breakdown |
|-------|--------|-------|---------------------|
| Gemini Intake | 430 | gemini-3.1-flash | HHT(115)+RECON(180)+SURV(60)+MFRC(60)+Mortar(15) |
| Perplexity Research | 430 | llama-3.1-sonar | Same structure |
| SuperGrok Research | 430 | grok-2-latest | Same structure |
| 10× Gemini Code Assist | 4,300 | gemini-3.1-flash | Same structure × 10 |
| **TOTAL** | **5,590** | | 13 Kosmos × 430 agents |

## JURA Tier Routing

| Tier | Traffic | Security | Threshold | Use Case |
|------|---------|----------|-----------|----------|
| FREE | 30% | Screen | 50% | Simple, low risk |
| FLASH | 60% | Guard | 75% | Standard, medium risk |
| PRO | 10% | Cover | 90% | High risk, governance |

## API Endpoints

```

POST /pipeline     Full pipeline execution (5,590 agents)
POST /intake       Gemini 2.5 Flash + Kosmos (430 agents)
POST /research     Perplexity + SuperGrok + Kosmos (860 agents)
POST /execute      10× Gemini Code Assist + Kosmos (4,300 agents)
POST /validate     CodePMCS scan
POST /deploy       GitHub + Cloud Build
GET  /health       Service health (ATP 3-20.96 aligned)
GET  /status       Detailed status
GET  /sessions     Active sessions

```

## Files

```

src/antigravity/
├── __init__.py          # Module exports (v2.0.0)
├── pipeline.py          # Full pipeline with Kosmos Cavalry
├── intake.py            # Gemini 2.5 Flash (2M context)
├── research.py          # Perplexity + SuperGrok
├── execute.py           # 10× Gemini Code Assist pool
├── validate.py          # CodePMCS scanning
└── deploy.py            # GitHub + Cloud Build

agents/
├── rsta_squadron.py     # ATP 3-20.96 Cavalry Squadron (430 agents)
└── cavalry_squadron.py  # Backward compatibility alias

kosmos/core/
├── recon_tasks.py       # Zone/Area/Route/Force reconnaissance
└── security_tasks.py    # Screen/Guard/Cover security voting

bin/
├── antigravity              # Local CLI
├── antigravity-orchestrator # Cloud Run server (v2.0.0)
└── Dockerfile.antigravity   # Container

cloudbuild-antigravity.yaml  # CI/CD

```

## Cost Comparison

| Provider | Model | Cost/1M Input | Cost/1M Output |
|----------|-------|---------------|----------------|
| Claude | claude-sonnet-4 | $3.00 | $15.00 |
| Gemini | gemini-3.1-flash | $0.075 | $0.30 |

**Token savings**: ~97% per token (vs Claude)
**Previous architecture**: 8,450 agents with Claude Code
**New architecture**: 5,590 agents with Gemini (ATP 3-20.96 aligned)

## Success Metrics

| Metric | Target |
|--------|--------|
| Code correctness | 97%+ |
| Defect escape | ≤3% |
| Auto-merge success | 93%+ |
| MTTR | ≤45 min |
| Cost per commit | ~$0.25 (down from $1.05) |

## Environment Variables

```bash
GEMINI_API_KEY        # Gemini 2.5 Flash + Code Assist
PERPLEXITY_API_KEY    # Perplexity Research
GROK_API_KEY          # SuperGrok/X
GITHUB_TOKEN          # GitHub PRs
CODEPMCS_URL          # CodePMCS service (optional)

```

## Sources



- [ATP 3-20.96 Cavalry Squadron](https://armypubs.army.mil/) - Primary doctrine reference


- [FM 3-21.31 SBCT RSTA](https://www.globalsecurity.org/military/library/policy/army/fm/3-21-31/) - RSTA foundation


- [Kosmos AI Scientist](https://arxiv.org/pdf/2511.02824) - Autonomous agent architecture

---

*Antigravity v2.0: ATP 3-20.96 Cavalry Squadron - Punch Perfect Monkey Code*
