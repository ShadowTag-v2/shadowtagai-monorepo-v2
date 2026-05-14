# LLM Memory Persistence System

**Multi-layered memory system for Claude Code, Vertex AI Workbench, and 4-LLM orchestration**

Extract 2,121+ conversations → Generate metadata with Gemini → Persist to GitHub → Sync across devices

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY EXTRACTION                        │
│  Cursor/Claude/Codex/Windsurf → 0xSero Scripts → 243MB     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              METADATA GENERATION                            │
│  Gemini Flash 2.0 → Tags, Quality, Difficulty, Projects    │
│  Cost: $0.45 one-time for 2,121 conversations              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              GITHUB PERSISTENCE                             │
│  • Semantic versioning (major.minor.patch)                 │
│  • Daily snapshots (memory/snapshots/)                     │
│  • Incremental deltas (memory/deltas/)                     │
│  • Version-controlled sync across devices                  │
└────────────────┬────────────────────────────────────────────┘
                 │
       ┌─────────┴─────────┬─────────────────┐
       │                   │                 │
       ▼                   ▼                 ▼
┌────────────┐  ┌──────────────────┐  ┌─────────────┐
│  CLAUDE    │  │  VERTEX AI       │  │  4-LLM      │
│  CODE      │  │  WORKBENCH       │  │  ROTATION   │
│            │  │                  │  │             │
│ ~/.claude- │  │ GCS-backed       │  │ Grok →      │
│ code/      │  │ Auto-load on     │  │ Sonnet →    │
│ memory.md  │  │ notebook start   │  │ 3-LLM →     │
│            │  │                  │  │ Reviews     │
└────────────┘  └──────────────────┘  └─────────────┘
```

## Three Implementations

### 1. Claude Code Memory

**Purpose**: Claude Code remembers YOUR patterns forever

**How it works**:
- Extract conversations → Gemini Flash metadata → `~/.claude-code/memory.md`
- Claude Code loads YOUR architecture on startup
- Judge #6, ShadowTag, JR Engine, Bootstrap Gates always available

**Cost**: $0.45 one-time (2,121 conversations)

**Setup**:
```bash
# Extract and generate memory
python scripts/extract_and_commit.py

# Install to Claude Code
python scripts/claude_code_memory_local.py

# Restart Claude Code
# Memory now loaded in all sessions
```

### 2. Vertex AI Workbench Memory

**Purpose**: Every Workbench session starts with YOUR architecture

**How it works**:
- Upload to GCS → Gemini Pro loads on notebook startup
- IPython startup script auto-loads `pnkln_memory` variable
- Cross-device sync via GCS

**Cost**: $0.02/month storage + minimal API calls

**Setup**:
```bash
# Setup GCS and auto-load
python configs/vertex_workbench_config.py memory/current.json

# In Jupyter notebooks:
# pnkln_memory variable auto-available
# Manual sync: sync_memory()
```

### 3. 4-LLM Orchestration with Review Rotation

**Purpose**: Multi-LLM collaborative processing with peer review

**Architecture**:
```
Grok (Intake) → Sonnet 4.5 (Coordinator) → 3-LLM Rotation
                                             ├─ Round 1: Answer
                                             ├─ Round 2: Review (rotate right)
                                             └─ Round 3: Review (rotate right)
                → Claude Code (Synthesis) → GitHub
```

**LLM Allocation**:
- **Gemini**: 40% (bulk processing, multimodal)
- **Claude**: 35% (coordination, Sonnet 4.5)
- **GPT-5**: 15% (structured output, coding)
- **Perplexity**: 5% (research, web-grounded)
- **Grok**: 5% (intake only, decomposition)

**Changes from AutoGen**:
- ✗ AutoGen removed (not used)
- ✓ Perplexity replaces Grok in rotation
- ✓ Grok for intake only

**Cost**: $0.08-0.12 per query

**Usage**:
```bash
# Run orchestration
python scripts/llm_blender_rotation.py

# Customize in code:
orchestrator = LLMOrchestrator(memory_repo, pnkln_memory)
result = await orchestrator.process_query("Your complex query here")
```

## GitHub Memory Persistence

**Repository Structure**:
```
erik-hancock-llm-memory/
├─ memory/
│  ├─ snapshots/
│  │  └─ memory_v1.0.0.json  (tagged releases)
│  ├─ deltas/
│  │  └─ 2025-01-16_delta.json  (daily increments)
│  ├─ current.json  (symlink → latest snapshot)
│  └─ schema.json  (architecture definition)
├─ configs/
│  ├─ claude_code_config.md
│  ├─ vertex_workbench_config.py
│  └─ gke_configmap.yaml
├─ scripts/
│  ├─ extract_and_commit.py  (auto-extraction + Git)
│  ├─ sync_to_devices.sh  (cross-device sync)
│  ├─ merge_conflicts.py  (LLM conflict resolution)
│  ├─ claude_code_memory_local.py
│  └─ llm_blender_rotation.py
└─ .github/workflows/
   ├─ daily_sync.yml  (automated extraction)
   └─ cross_device_sync.yml  (notify on updates)
```

**Semantic Versioning**:
- **Patch** (1.0.X): Daily updates, <100 new conversations
- **Minor** (1.X.0): 100+ conversations, new features
- **Major** (X.0.0): Architecture changes, breaking updates

**Workflow**:
```bash
# Morning: Pull latest updates
./scripts/sync_to_devices.sh pull

# Work with updated memory
# Claude Code / Vertex / 4-LLM all synced

# Evening: Push your changes
./scripts/sync_to_devices.sh push

# GitHub Actions: Automated daily sync
```

## Cross-Device Sync

**Devices Supported**:
- **MacBook Pro**: Local development
- **Vertex AI Workbench**: Cloud notebooks
- **GKE Native**: Production deployment

**Sync Flow**:
```
MacBook ──┬──> GitHub ──┬──> Vertex Workbench
          │             │
          └──> GitHub ──┴──> GKE Cluster

Auto-sync: GitHub Actions (daily)
Manual sync: ./sync_to_devices.sh {pull|push}
```

**Conflict Resolution**:
```bash
# Automatic LLM-powered resolution
python scripts/merge_conflicts.py

# Manual resolution
git mergetool

# Keep local version
git checkout --ours <file> && git add <file>

# Keep remote version
git checkout --theirs <file> && git add <file>
```

## Tech Stack

**Extraction**: 0xSero scripts (Python stdlib, sqlite3)
**Metadata**: Gemini Flash 2.0 ($0.075/1M input tokens)
**Orchestration**: Grok + Sonnet 4.5 + Gemini + GPT-5 + Perplexity
**Storage**: GitHub (version control) + GCS (Vertex)
**Deployment**: MacBook → Vertex AI Workbench → GKE Native

## Cost Economics

| Component | Cost | Frequency |
|-----------|------|-----------|
| Initial extraction | $0.45 | One-time |
| GitHub storage | $0.00 | Monthly (free) |
| GCS storage | $0.02 | Monthly |
| 4-LLM query | $0.08-0.12 | Per query |
| **Total (ongoing)** | **~$0.02/month** | **Monthly** |

## Pnkln Architecture (from Memory)

### Core Systems

**Judge #6**:
- Gemini + PyTorch + Rules engine
- 98% coverage, p99 ≤90ms
- Content moderation at scale

**ShadowTag 2.0**:
- DCT watermarking
- Content protection & attribution

**Cor/NS**:
- Unified execution brain
- Service mesh coordination

### JR Framework (Purpose • Reasons • Brakes)

**Purpose**: Does this advance Pnkln revenue/mission?
**Reasons**: Defensible judgment with evidence
**Brakes**: p99 survivability, bootstrap constraints

### Bootstrap Gates

- **ROI**: ≥3× in 18 months
- **LTV:CAC**: ≥4:1 in 12 months
- **p99 Latency**: ≤90ms
- **Security**: 100% (absolute gate)

## Deployment Modes

### 1. LOCAL (MacBook Pro)
```bash
# Clone repo
git clone https://github.com/ehanc69/erik-hancock-llm-memory.git
cd erik-hancock-llm-memory

# Extract conversations
python scripts/extract_and_commit.py

# Install to Claude Code
python scripts/claude_code_memory_local.py

# Daily sync
./scripts/sync_to_devices.sh pull
```

### 2. VERTEX (Vertex AI Workbench)
```bash
# Setup GCS + auto-load
python configs/vertex_workbench_config.py

# Restart Jupyter kernel
# pnkln_memory now auto-loaded

# Manual sync
sync_memory()
```

### 3. GKE (Production)
```bash
# Deploy ConfigMap
kubectl apply -f configs/gke_configmap.yaml

# Init container syncs from GitHub
# Memory available cluster-wide
```

## Quick Start

**1. Initialize Repository**
```bash
cd erik-hancock-llm-memory
git init
git remote add origin https://github.com/ehanc69/erik-hancock-llm-memory.git
```

**2. Extract Conversations**
```bash
# Run extraction (finds Cursor/Claude/Codex DBs)
python scripts/extract_and_commit.py

# Output:
# ✓ Extracted 2,121 conversations
# ✓ Cost: $0.45
# ✓ Committed to GitHub
```

**3. Choose Implementation**

**Claude Code**:
```bash
python scripts/claude_code_memory_local.py
# Restart Claude Code → memory loaded
```

**Vertex Workbench**:
```bash
python configs/vertex_workbench_config.py memory/current.json
# Restart Jupyter → pnkln_memory available
```

**4-LLM Orchestration**:
```bash
# Set API keys
export ANTHROPIC_API_KEY=...
export GOOGLE_API_KEY=...
export OPENAI_API_KEY=...
export GROK_API_KEY=...
export PERPLEXITY_API_KEY=...

# Run orchestration
python scripts/llm_blender_rotation.py
```

## GitHub Actions Automation

**Daily Sync** (`.github/workflows/daily_sync.yml`):
- Runs: 00:00 UTC daily
- Extracts new conversations
- Commits + pushes to main
- Creates tagged release

**Cross-Device Notify** (`.github/workflows/cross_device_sync.yml`):
- Triggers: On memory update
- Sends notification (Slack/Discord/Email)
- Alerts: "Run sync_to_devices.sh pull"

## API Keys Required

```bash
# For Gemini metadata extraction
export GOOGLE_API_KEY=your_google_api_key

# For 4-LLM orchestration (optional)
export ANTHROPIC_API_KEY=your_anthropic_key
export OPENAI_API_KEY=your_openai_key
export GROK_API_KEY=your_grok_key
export PERPLEXITY_API_KEY=your_perplexity_key

# For GCS (Vertex only)
export GOOGLE_CLOUD_PROJECT=pnkln-prod
```

## File Descriptions

| File | Purpose |
|------|---------|
| `extract_and_commit.py` | Extract conversations, generate metadata, commit to Git |
| `claude_code_memory_local.py` | Install memory to `~/.claude-code/memory.md` |
| `vertex_workbench_config.py` | Setup GCS + auto-load for Vertex notebooks |
| `llm_blender_rotation.py` | 4-LLM orchestration with review rotation |
| `sync_to_devices.sh` | Cross-device pull/push utility |
| `merge_conflicts.py` | LLM-powered conflict resolution |
| `daily_sync.yml` | GitHub Actions: automated extraction |
| `cross_device_sync.yml` | GitHub Actions: update notifications |

## Troubleshooting

**"No conversations found"**:
- Check Cursor/Claude paths in `extract_and_commit.py`
- Run: `find ~ -name "state.vscdb"` to locate DBs

**"Memory not loaded in Claude Code"**:
- Check: `~/.claude-code/memory.md` exists
- Restart Claude Code
- Verify config: `~/.claude-code/config.json`

**"Git push failed with 403"**:
- Check branch name starts with `claude/`
- Verify: `git remote -v`
- Retry with: `./sync_to_devices.sh push` (auto-retries)

**"Merge conflicts"**:
```bash
# Option 1: LLM resolution
python scripts/merge_conflicts.py

# Option 2: Manual
git mergetool

# Option 3: Keep one side
git checkout --ours <file>  # Keep local
git checkout --theirs <file>  # Keep remote
git add <file> && git commit
```

## Next Steps

1. **Initialize**: `git init erik-hancock-llm-memory`
2. **Extract**: `python scripts/extract_and_commit.py`
3. **Deploy**: Choose Claude Code / Vertex / 4-LLM
4. **Automate**: Enable GitHub Actions for daily sync
5. **Sync**: Use `sync_to_devices.sh` for cross-device updates

## Cost Summary

- **Setup**: $0.45 (one-time extraction)
- **Storage**: $0.00 GitHub + $0.02/month GCS
- **Operations**: $0.08-0.12 per 4-LLM query
- **Total Monthly**: **~$0.02-0.05** (excluding query costs)

**ROI**: 3x in 18mo via:
- Faster onboarding (context always available)
- Consistent architecture (Judge #6, ShadowTag, Cor/NS)
- Reduced rework (JR framework gate violations caught early)
- 2× decision speed (bootstrap gates pre-loaded)

## License

Proprietary - Pnkln Corp.

## Contact

Erik Hancock (CEO, Pnkln)
Repo: https://github.com/ehanc69/erik-hancock-llm-memory
