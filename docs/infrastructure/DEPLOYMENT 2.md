# Deployment Guide

## Quick Start (5 Minutes)

### 1. Initialize Git Repository

```bash
cd erik-hancock-llm-memory
git init
git add .
git commit -m "Initial commit: LLM memory persistence system"
git branch -M main
git remote add origin https://github.com/ehanc69/erik-hancock-llm-memory.git
git push -u origin main

```

### 2. Extract Conversations (One-Time)

```bash

# Install dependencies

pip install google-generativeai google-cloud-storage

# Set API key

export GOOGLE_API_KEY=your_gemini_api_key

# Run extraction

python scripts/extract_and_commit.py

# Output:

# ✓ Extracted 2,121 conversations

# ✓ Total tokens: ~500,000

# ✓ Cost: $0.45

# ✓ Committed to Git as v1.0.0

```

### 3. Deploy to Claude Code (MacBook)

```bash
python scripts/claude_code_memory_local.py

# Restart Claude Code

# Memory now auto-loaded in all sessions

```

## Deployment Paths

### Path 1: Claude Code Only (Recommended for MVP)

**Time**: 5 minutes
**Cost**: $0.45 one-time
**Value**: Claude Code remembers your architecture forever

```bash

# 1. Extract

python scripts/extract_and_commit.py

# 2. Install

python scripts/claude_code_memory_local.py

# 3. Verify

cat ~/.claude-code/memory.md

# 4. Test

# Open Claude Code → Ask "What is Judge 6?"

# Should respond with ShadowTagAi architecture details

```

### Path 2: Vertex AI Workbench

**Time**: 10 minutes
**Cost**: $0.02/month + $0.45 one-time
**Value**: Cloud notebooks with persistent memory

```bash

# 1. Setup GCS

python configs/vertex_workbench_config.py memory/current.json

# 2. Restart Jupyter kernel

# 3. Test in notebook

print(shadowtagai_memory['version'])
print(shadowtagai_memory['shadowtagai_architecture']['judge_6'])

# 4. Manual sync anytime

sync_memory()

```

**GCS Bucket Created**: `{PROJECT_ID}-workbench-memory`
**Auto-load**: IPython startup script at `~/.ipython/profile_default/startup/00-load-shadowtagai-memory.py`

### Path 3: 4-LLM Orchestration

**Time**: 15 minutes
**Cost**: $0.08-0.12 per query
**Value**: Multi-LLM collaborative processing with peer review

```bash

# 1. Set API keys

export ANTHROPIC_API_KEY=your_anthropic_key
export GOOGLE_API_KEY=your_google_key
export OPENAI_API_KEY=your_openai_key
export GROK_API_KEY=your_grok_key
export PERPLEXITY_API_KEY=your_perplexity_key

# 2. Run orchestration

python scripts/llm_blender_rotation.py

# 3. Customize queries

# Edit llm_blender_rotation.py main() function

# Add your query, run again

```

**Flow**:


1. Grok decomposes query → threads


2. Sonnet 4.5 assigns threads → LLMs (Gemini 40%, GPT-5 15%, Perplexity 5%)


3. Round 1: Each LLM answers


4. Round 2: Rotate right → peer review


5. Round 3: Rotate right → second review


6. Claude Code: Synthesize → publish to GitHub

### Path 4: Full Production (GKE Native)

**Time**: 30 minutes
**Cost**: GKE cluster cost + $0.02/month
**Value**: Cluster-wide memory, auto-sync, init containers

```bash

# 1. Deploy ConfigMap

kubectl apply -f configs/gke_configmap.yaml

# 2. Verify

kubectl get configmap llm-memory -o yaml

# 3. Test with example pod

kubectl apply -f configs/gke_configmap.yaml  # Includes example pod
kubectl logs shadowtagai-worker-example -c sync-memory

# 4. Deploy to your apps

# Add initContainer to your deployments (see gke_configmap.yaml)

```

**ConfigMap**: `llm-memory`
**Init Container**: Syncs from GitHub on pod start
**Shared Volume**: `/shared/memory.json`

## GitHub Actions Automation

### Daily Sync (Automated Extraction)

**File**: `.github/workflows/daily_sync.yml`
**Schedule**: 00:00 UTC daily
**Triggers**: Cron + manual dispatch

**Setup**:


1. Add GitHub secret: `GOOGLE_API_KEY`


2. Enable GitHub Actions in repo settings


3. Workflow runs automatically

**What it does**:


- Extracts new conversations


- Generates metadata with Gemini


- Commits + pushes to main


- Creates tagged release


- Updates `current.json` symlink

### Cross-Device Sync Notification

**File**: `.github/workflows/cross_device_sync.yml`
**Triggers**: Push to `memory/**`

**What it does**:


- Detects memory updates


- Parses statistics (conversations, tokens, version)


- Sends notification (console output)


- Optional: Slack/Discord/Email (uncomment in YAML)

**Setup Slack/Discord** (optional):

```yaml

# In cross_device_sync.yml, uncomment:



- name: Send Slack notification
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    # ... (already configured in file)

# Add GitHub secret:

# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

```

## Cross-Device Sync

### Daily Workflow

**Morning** (pull latest):

```bash
./scripts/sync_to_devices.sh pull

# Output:

# ✓ Pulled latest from GitHub

# ✓ Updated current.json symlink

# ✓ Synced to Claude Code (if on Mac)

# ✓ Synced to Vertex Workbench (if on Vertex)

```

**Evening** (push changes):

```bash
./scripts/sync_to_devices.sh push

# Output:

# ✓ Extracted new conversations

# ✓ Created snapshot v1.0.1

# ✓ Pushed to GitHub

# ✓ Pushed tags

```

**Check status**:

```bash
./scripts/sync_to_devices.sh status

# Output:

# Version: 1.0.1

# Last Updated: 2025-01-16T12:00:00Z

# Conversations: 2,121

# Git status, recent commits, snapshots

```

### Conflict Resolution

**Automatic** (LLM-powered):

```bash

# After pull with conflicts

python scripts/merge_conflicts.py

# Uses Claude Sonnet 4.5 to intelligently merge

# Preserves semantic intent from both versions

```

**Manual**:

```bash

# Traditional Git workflow

git mergetool

# Or choose one side

git checkout --ours <file>    # Keep local
git checkout --theirs <file>  # Keep remote
git add <file> && git commit

```

## API Keys Required

### Minimum (Claude Code only)

```bash
export GOOGLE_API_KEY=your_gemini_key  # For metadata extraction

```

### Full (4-LLM orchestration)

```bash
export GOOGLE_API_KEY=your_gemini_key
export ANTHROPIC_API_KEY=your_anthropic_key
export OPENAI_API_KEY=your_openai_key
export GROK_API_KEY=your_grok_key
export PERPLEXITY_API_KEY=your_perplexity_key

```

### Vertex AI Workbench

```bash
export GOOGLE_CLOUD_PROJECT=shadowtagai-prod  # Your GCP project

# Uses Application Default Credentials (gcloud auth)

```

## Verification Checklist

### Claude Code Installation



- [ ] `~/.claude-code/memory.md` exists


- [ ] File contains ShadowTagAi architecture sections


- [ ] `~/.claude-code/config.json` created


- [ ] Restart Claude Code


- [ ] Ask Claude Code: "What is Judge 6?"


- [ ] Response includes: "98% coverage, p99 ≤90ms"

### Vertex Workbench Installation



- [ ] GCS bucket `{PROJECT}-workbench-memory` created


- [ ] `~/.workbench/memory.json` exists


- [ ] IPython startup script in `~/.ipython/profile_default/startup/`


- [ ] Restart Jupyter kernel


- [ ] Variable `shadowtagai_memory` available


- [ ] `sync_memory()` function works

### 4-LLM Orchestration



- [ ] All 5 API keys set (Grok, Sonnet, Gemini, GPT-5, Perplexity)


- [ ] `python scripts/llm_blender_rotation.py` runs without errors


- [ ] Output shows: Intake → Coordination → 3 rounds → Synthesis


- [ ] Answer published to `erik-hancock-llm-memory/answers/`

### GitHub Actions



- [ ] GitHub secret `GOOGLE_API_KEY` added


- [ ] Workflow file `.github/workflows/daily_sync.yml` committed


- [ ] Manual trigger works: Actions tab → Daily Memory Sync → Run workflow


- [ ] Cron runs successfully (check next day)

### Cross-Device Sync



- [ ] `./scripts/sync_to_devices.sh pull` works


- [ ] `./scripts/sync_to_devices.sh push` works


- [ ] `./scripts/sync_to_devices.sh status` shows correct info


- [ ] Memory syncs across Mac ↔ Vertex ↔ GKE

## Troubleshooting

### "No conversations found"

**Cause**: 0xSero extraction paths incorrect
**Fix**:

```bash

# Find Cursor DBs

find ~ -name "state.vscdb" 2>/dev/null

# Update paths in extract_and_commit.py:

CURSOR_DB_PATHS = [
    Path("your/actual/path/workspaceStorage"),
    # ...
]

```

### "Git push failed with 403"

**Cause**: Branch name doesn't start with `claude/`
**Fix**:

```bash

# Check current branch

git branch

# Must be: claude/add-superpowers-marketplace-011CUuLnhzCNrXYhosFmMAt9

# Create if needed

git checkout -b claude/add-superpowers-marketplace-011CUuLnhzCNrXYhosFmMAt9
git push -u origin claude/add-superpowers-marketplace-011CUuLnhzCNrXYhosFmMAt9

```

### "Memory not loaded in Claude Code"

**Cause**: File not in correct location or Claude Code not restarted
**Fix**:

```bash

# Verify file exists

ls -lh ~/.claude-code/memory.md

# Re-run installation

python scripts/claude_code_memory_local.py

# Hard restart Claude Code (quit + reopen)

```

### "Vertex Workbench: shadowtagai_memory not found"

**Cause**: IPython startup script not executed
**Fix**:

```bash

# Check startup script

cat ~/.ipython/profile_default/startup/00-load-shadowtagai-memory.py

# Restart kernel (not just refresh)

# In Jupyter: Kernel → Restart

# Manual load

from pathlib import Path
import json
with open(Path.home() / ".workbench" / "memory.json") as f:
    shadowtagai_memory = json.load(f)

```

### "4-LLM: API call failed"

**Cause**: Missing or invalid API key
**Fix**:

```bash

# Check keys are set

echo $ANTHROPIC_API_KEY
echo $GOOGLE_API_KEY

# etc.

# Set missing keys

export ANTHROPIC_API_KEY=sk-ant-...

# Test individually

curl -H "x-api-key: $ANTHROPIC_API_KEY" \
  https://api.anthropic.com/v1/messages

```

### "Merge conflicts"

**Cause**: Divergent changes on different devices
**Fix**:

```bash

# Option 1: LLM resolution

python scripts/merge_conflicts.py

# Option 2: Keep local

git checkout --ours <file>
git add <file> && git commit

# Option 3: Keep remote

git checkout --theirs <file>
git add <file> && git commit

# Option 4: Manual edit

vim <file>  # Resolve conflicts
git add <file> && git commit

```

## Cost Breakdown

### One-Time Costs

| Item | Cost | When |
|------|------|------|
| Initial extraction | $0.45 | First run |
| **Total** | **$0.45** | **One-time** |

### Recurring Costs

| Item | Cost | Frequency |
|------|------|-----------|
| GitHub storage | $0.00 | Monthly (free) |
| GCS storage (~100MB) | $0.02 | Monthly |
| Gemini metadata (incremental) | ~$0.10 | Monthly (100 new convos) |
| **Total** | **~$0.12** | **Monthly** |

### Per-Query Costs (4-LLM)

| Component | Cost |
|-----------|------|
| Grok (intake) | $0.01 |
| Sonnet (coordination) | $0.015 |
| Gemini (40% exec) | $0.001 |
| GPT-5 (15% exec) | $0.0012 |
| Perplexity (5% exec) | $0.00025 |
| Reviews (2 rounds) | $0.03 |
| Claude Code (synthesis) | $0.015 |
| **Total per query** | **$0.08-0.12** |

### ROI Calculation

**Efficiency Gains**:


- Context loading: 5 min → 0 min (saved per session)


- Architecture lookup: 10 min → instant


- Decision validation: 15 min → 2 min (JR framework pre-loaded)

**Time Saved per Week**:


- 5 sessions × 5 min = 25 min


- 10 lookups × 10 min = 100 min


- 3 decisions × 13 min = 39 min


- **Total: 164 min/week = 2.7 hours/week**

**Value per Hour**: $200 (eng salary)
**Weekly Value**: 2.7 × $200 = $540
**Monthly Value**: $540 × 4 = $2,160
**Monthly Cost**: $0.12

**ROI**: $2,160 / $0.12 = **18,000%** 🚀

## Next Steps



1. **Initialize Git**: `git init && git remote add origin ...`


2. **Extract**: `python scripts/extract_and_commit.py`


3. **Deploy Claude Code**: `python scripts/claude_code_memory_local.py`


4. **Test**: Ask Claude Code about ShadowTagAi architecture


5. **Automate**: Enable GitHub Actions for daily sync


6. **Scale**: Deploy to Vertex (GCS) and/or GKE (production)

## Support

**Issues**: https://github.com/ehanc69/erik-hancock-llm-memory/issues
**Docs**: See README.md for detailed architecture
**Contact**: ShadowTagAi Team (ShadowTagAi CEO)
