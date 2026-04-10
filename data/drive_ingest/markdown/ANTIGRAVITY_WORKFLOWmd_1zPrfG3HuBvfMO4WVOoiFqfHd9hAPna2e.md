# ShadowTagAi Multi-Tool Development Workflow

## Overview: Antigravity + Cursor Router + Gemini CLI

```
┌─────────────────────────────────────────────────┐
│ PHASE 1: ANTIGRAVITY (Architecture)             │
│ Model: Gemini 2.5 Pro                           │
│ Output: Implementation plan artifact            │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│ PHASE 2: CURSOR MULTI-MODEL ROUTER              │
│ Routes to optimal model per task                │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│ PHASE 3: GEMINI CLI (Production Deployment)     │
│ Target: GKE autopilot-cluster-1                 │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│ PHASE 4: ANTIGRAVITY (Browser Verification)     │
│ Output: Video proof, p99 latency validation     │
└─────────────────────────────────────────────────┘
```

---

## Installation

```bash
# Antigravity
brew install antigravity

# Gemini CLI
pip install google-generativeai
gcloud auth application-default login

# Ollama (local models)
brew install ollama
ollama pull llama3.3:70b
ollama serve &
```

---

## API Configuration

```bash
cat > ~/.env << EOF
OPENROUTER_API_KEY = "REDACTED_API_KEY"
GEMINI_API_KEY="YOUR_API_KEY_HERE"
ANTHROPIC_API_KEY = "REDACTED_API_KEY"
EOF
```

---

## UNGPT Tech - LLM Serving Efficiency

Multi-provider orchestration for cost/performance optimization.

### Router Architecture

Based on `router/src/openai-proxy.ts`:

```
┌─────────────────────────────────────────────┐
│ UNGPT MULTI-PROVIDER ROUTER                 │
├─────────────────────────────────────────────┤
│ IF task = "function_call" OR "fast"         │
│   → Gemini (12× faster, 70% cheaper)        │
│                                             │
│ IF task = "deep_reasoning" OR "complex"     │
│   → Anthropic (best quality)                │
│                                             │
│ IF task = "bulk" OR "high_volume"           │
│   → Groq/Cheetah (Llama 3.1, fast)          │
│                                             │
│ IF task = "offline" OR "sensitive"          │
│   → Ollama (local, free)                    │
└─────────────────────────────────────────────┘
```

### Provider Configuration

| Provider | Model | Use Case | Cost |
|----------|-------|----------|------|
| Gemini | `gemini-2.5-flash` | Function calls, bulk | $0.075/1M |
| Anthropic | `claude-sonnet-4.5` | Deep reasoning | $3/1M |
| Groq | `llama-3.1-8b-instant` | High volume | $0.05/1M |
| xAI | `grok-code-fast-1` | Speed (92 tok/s) | $0.20/1M |
| Ollama | `llama3.3:70b` | Offline/sensitive | $0 |

### Endpoint

```bash
POST http://localhost:8787/v1/chat/completions?target=<provider>
```

---

## Ingestion Pipeline - Nightly Intelligence

Gemini Ingestion Layer for automated intelligence collection.

### Architecture

```
┌─────────────────────────────────────────────┐
│ GEMINI INGESTION LAYER (Nightly)            │
├─────────────────────────────────────────────┤
│ Runtime: ~45 minutes                        │
│ Items/day: 1000-5000                        │
│ Cost/item: ~$0.015                          │
│ Monthly budget: ~$77                        │
└─────────────────────────────────────────────┘
```

### 4-Stage Pipeline

| Stage | Duration | Description |
|-------|----------|-------------|
| 1. Collection | ~30 min | Parallel fetch from 8+ sources |
| 2. Classification | ~10 min | Tier 1/2/3 scoring |
| 3. Validation | ~2 min | Quality gate enforcement |
| 4. Briefing | ~3 min | AM intelligence summary |

### Sources

- YouTube (video transcripts)
- Twitter (trends, mentions)
- News API (headlines, articles)
- RSS Feeds (industry blogs)
- Reddit (subreddit discussions)
- LinkedIn (professional content)
- GitHub (code trends, releases)
- Academic (papers, research)

### Quality Gates

| Gate | Target | Description |
|------|--------|-------------|
| Items/day | 1000-5000 | Volume bounds |
| Active sources | ≥8 | Diversity |
| Tier 1 ratio | ≥40% | High-value content |
| Avg relevance | ≥0.70 | Actionability |
| Cost/item | ≤$0.02 | Efficiency |

### Data Tiers

- **Tier 1**: High-value (verified sources, unique insights)
- **Tier 2**: Medium-value (standard sources, general content)
- **Tier 3**: Low-value (noise, duplicates)

### File Location

```
shadowtagai/core/gemini_ingestion_layer.py
```

---

## Judge #6 - Governance Pipeline

3-kernel validation pipeline with p99 ≤90ms SLA.

### Architecture

```
┌─────────────────────────────────────────────┐
│ JUDGE #6 THREE-KERNEL PIPELINE              │
├─────────────────────────────────────────────┤
│                                             │
│ KERNEL 1: ATP 5-19 SCAN                     │
│ ├─ Model: Gemini Flash                      │
│ ├─ Latency: 40ms p50                        │
│ ├─ Input: 50KB raw context                  │
│ └─ Output: 2.5KB violations JSON            │
│                                             │
│ KERNEL 2: CLASSIFICATION                    │
│ ├─ Model: PyTorch (local)                   │
│ ├─ Latency: 12ms p99                        │
│ ├─ Input: Violations JSON                   │
│ └─ Output: Binary decision + risk tier      │
│                                             │
│ KERNEL 3: AUDIT COMPRESS                    │
│ ├─ Algorithm: zstd level 22                 │
│ ├─ Latency: <1ms                            │
│ ├─ Compression: 10:1 ratio                  │
│ └─ Output: 487 bytes + SHA256               │
│                                             │
└─────────────────────────────────────────────┘
```

### JR Engine (Purpose/Reasons/Brakes)

Deterministic risk assessment in <500μs.

#### Framework

- **Purpose**: Does this advance mission/revenue?
- **Reasons**: Defensible judgment with evidence
- **Brakes**: ATP 5-19 risk assessment

#### Probability Levels

| Level | Code | Frequency |
|-------|------|-----------|
| A | FREQUENT | >1 per week |
| B | LIKELY | 1/month - 1/year |
| C | OCCASIONAL | 1 per 1-3 years |
| D | SELDOM | 1 per 10 years |
| E | UNLIKELY | <1 per 10 years |

#### Severity Levels

| Level | Code | Impact |
|-------|------|--------|
| I | CATASTROPHIC | Death, >$10M loss |
| II | CRITICAL | Severe injury, >$1M |
| III | MODERATE | Minor injury, >$100K |
| IV | NEGLIGIBLE | First aid, <$100K |

#### Risk Matrix

```
        IV      III      II       I
    ┌───────┬───────┬───────┬───────┐
A   │   M   │   H   │  EH   │  EH   │
B   │   L   │   M   │   H   │  EH   │
C   │   L   │   M   │   H   │  EH   │
D   │   L   │   L   │   M   │   H   │
E   │   L   │   L   │   M   │   M   │
    └───────┴───────┴───────┴───────┘

EH = EXTREMELY_HIGH → REJECT
H  = HIGH           → ESCALATE
M  = MODERATE       → APPROVE (log)
L  = LOW            → AUTO-APPROVE
```

### Risk Tier Classification

| Tier | Score | Description |
|------|-------|-------------|
| TIER_1_MINIMAL | 0.0 | No violations |
| TIER_2_LOW | 2.0 | Minor violations |
| TIER_3_MODERATE | 5.0 | Moderate violations |
| TIER_4_HIGH | 10.0 | Major violations |
| TIER_5_CRITICAL | 20.0 | Critical violations |

### Severity Weights

```python
SEVERITY_WEIGHTS = {
    "minor": 1.0,
    "moderate": 2.5,
    "major": 5.0,
    "critical": 10.0
}
```

### Performance

| Metric | Target | Description |
|--------|--------|-------------|
| p99 Latency | ≤90ms | End-to-end SLA |
| Fast Path | ~20-30ms | 80% LOW risk |
| Full Pipeline | ~70-85ms | 20% MEDIUM+ risk |
| JR Engine | <500μs | Deterministic scan |
| Token Reduction | 95% | 50KB → 2.5KB |
| Compression | 10:1 | 4.8KB → 487 bytes |
| Cost/Decision | ~$0.0003 | Gemini Flash only |

### File Locations

| File | Purpose |
|------|---------|
| `app/kernels/judge_six.py` | Binary classification |
| `app/kernels/atp_519_scan.py` | Violation extraction |
| `app/kernels/audit_compress.py` | Audit trail compression |
| `shadowtagai/core/jr_engine.py` | JR Engine framework |
| `shadowtagai/core/judge_six_pipeline.py` | Pipeline orchestration |

---

## Cursor Model Configuration

Based on `router/src/openai-proxy.ts`:

### Model Routing

| Task | Model | Provider | Reason |
|------|-------|----------|--------|
| Fast prototype | `grok-code-fast-1` | OpenRouter | 92 tok/s |
| Bulk refactor | `gemini-2.5-flash` | Google | 1M context |
| Quick edit | `claude-haiku-4.5` | Anthropic | Fast, cheap |
| Security/ATP | `claude-sonnet-4.5` | Cursor Pro | Best reasoning |
| Offline | `llama3.3:70b` | Ollama | Local, free |

---

## GKE Deployment

| Setting | Value |
|---------|-------|
| Cluster | `autopilot-cluster-1` |
| Region | `us-central1` |
| Project | `acquired-jet-478701-b3` |
| Registry | `us-central1-docker.pkg.dev/PROJECT_ID/shadowtagai-core/` |
| Namespace | `autopilot-cluster-1` |

### Judge #6 Deployment

```yaml
# k8s/judge6_deployment.yaml
namespace: judge6-system
containers:
  - layer1-gemini (8080)
  - layer2-orchestration (8081)
  - layer3-gateway (8082)
gpu: nvidia-l4
```

---

## Complete Workflow Script

```bash
#!/bin/bash
PROJECT=~/shadowtagai-judge6
CODEBASE=~/Documents/Claude\ Code/Code/Claude\ Demo/ShadowTag-v2-fastapi-services

# PHASE 1: ANTIGRAVITY
open -a Antigravity $PROJECT
# Generate implementation plan artifact

# PHASE 2: CURSOR + GROK
cursor "$CODEBASE"
# Route tasks to optimal models

# PHASE 3: DEPLOY
cd "$CODEBASE"
gcloud builds submit --config=cloudbuild.yaml --project=acquired-jet-478701-b3 .

# PHASE 4: VERIFY
# Return to Antigravity for browser testing
```

---

## Cost Analysis

### Per Feature

| Phase | Cost |
|-------|------|
| Antigravity | $0 (free) |
| Grok Fast | ~$0.30 |
| Gemini Flash | ~$0.12 |
| Haiku | ~$0.15 |
| Sonnet | $0 (Cursor Pro) |
| Llama Local | $0 |
| **Total** | **~$0.62** |

### Monthly Budget

| Item | Cost |
|------|------|
| Cursor Pro | $20 |
| 20 features | ~$12 |
| Ingestion | ~$77 |
| Judge decisions | ~$9 (30K @ $0.0003) |
| **Total** | **~$118/month** |

---

## Notes

- Use `gemini-2.5-flash` (not "Gemini 3" which doesn't exist)
- Project name: ShadowTagAi (not PNKLN)
- Llama 70B requires 64GB+ RAM
- Ingestion runs nightly via GKE CronJob
- Judge #6 fast path skips Gemini for 80% of requests