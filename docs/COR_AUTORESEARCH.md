# Cor.autoresearch — Canonical Doctrine

**Status**: Canonical
**Replaces**: FlyingMonkeys (retired 2026-04-24)
**Architecture**: See [UPHILLSNOWBALL_ARCHITECTURE.md](./UPHILLSNOWBALL_ARCHITECTURE.md)

## Canonical Doctrine Line

> **UphillSnowball uses Cor.autoresearch as its engine: Kosmos directs, BioAgents routes,
> n-autoresearch executes, iii tracks state, JudgeSix-Human gates human/server actions,
> JudgeSix-Agent gates every agent output, the whiteboard persists unresolved issues,
> and RKILL terminates unsafe or non-convergent runs.**

## Three-Layer Architecture

### 1. Kosmos — Research Director

Kosmos owns literature-aware hypothesis generation, research planning, validation,
knowledge graph state, context compression, and multi-cycle scientific workflow.

**In UphillSnowball**: Kosmos = Research Director. It decides what should be tried next.

Reference: [jimmc414/Kosmos](https://github.com/jimmc414/Kosmos) |
[arXiv 2511.02824](https://arxiv.org/abs/2511.02824)

### 2. BioAgents — Routing and Research API

BioAgents owns the HTTP layer, job routing, research agents, file upload, planning,
literature, analysis, hypothesis, reflection, reply, state, JWT auth, WebSocket updates.

**In UphillSnowball**: BioAgents = Research API + queue/router + progress stream.
It receives work, routes it, and reports progress.

Six BioAgents: Architect, Builder, Critic, Corrector, Vault, Jetski.

### 3. n-autoresearch + iii — Execution Substrate

n-autoresearch owns the bottom layer: experiment setup, search suggestions, GPU
acquisition, `train.py` edits, 5-minute training runs, `val_bpb` metrics,
keep/discard decisions, crash tracking, and adaptive search modes.

**In UphillSnowball**: n-autoresearch + iii = execution substrate.
It does the measurable experimental work.

Reference: [karpathy/autoresearch](https://github.com/karpathy/autoresearch)

## Replacement Map

### Code Identifiers

| Legacy | Replacement |
|---|---|
| `FlyingMonkeys` (class) | `AutoresearchEngine` |
| `flying_monkeys` (module) | `cor_autoresearch` or `autoresearch_engine` |
| `flyingmonkeys-server` (service) | `uphillsnowball-engine` |
| `deploy-flyingmonkeys.yml` | `deploy-uphillsnowball-engine.yml` |
| `monkey watchdog` | `runtime_watchdog` |
| `600-agent swarm` | Kosmos + BioAgents + n-autoresearch triad |

### Naming Standard

| Context | Value |
|---|---|
| Human/display | Cor.autoresearch |
| Python package | `cor_autoresearch` |
| Class name | `AutoresearchEngine` |
| Cloud Run service | `uphillsnowball-engine` |
| Docker image | `uphillsnowball/engine` |
| API prefix | `/v1/autoresearch` |

### Concepts Removed

- FlyingMonkeys (all forms)
- 600-agent monkey swarm
- UCMJ discipline language
- God mode / IQ lock
- Tauri desktop wrapper
- Local biometric hooks
- Apple Silicon lab framing

### Concepts Kept

- RKILL → routed through JudgeSix-Agent + RuntimeWatchdog
- Whiteboard → Firestore durable issue board
- JudgeSix-Human → fast MITM sidecar
- JudgeSix-Agent → autonomous output gate
- Jetski → browser research adapter

## Critical Warning

A prior commit attempted to replace FlyingMonkeys with the literal string
`n-autoresearch/Kosmos/BioAgents` inside Python identifiers, class names, and
Cloud Run service names. This created syntactically invalid code:

```python
# WRONG — NEVER DO THIS
class AntigravitySwarm(n-autoresearch/Kosmos/BioAgents):
    pass
```

The corrected approach uses valid identifiers as documented in this file.

## File Locations

```
labs/uphillsnowball/engine/cor_autoresearch.py       → AutoresearchEngine
labs/uphillsnowball/engine/kosmos_bridge.py           → KosmosBridge
labs/uphillsnowball/engine/bioagents_worker.py        → BioAgentsWorker
labs/uphillsnowball/engine/n_autoresearch_client.py   → NAutoresearchClient
labs/uphillsnowball/governance/Claude_Code_6_human.py     → JudgeSixHuman
labs/uphillsnowball/governance/Claude_Code_6_agent.py     → JudgeSixAgent
labs/uphillsnowball/governance/runtime_watchdog.py    → RuntimeWatchdog
labs/uphillsnowball/governance/rkill.py               → RKillHandler
```
