# Quick Start Guide

## 30-Second Overview

**What**: Extract 2,121+ LLM conversations → Generate metadata → Persist to GitHub → Load into Claude Code/Vertex/4-LLM

**Why**: Claude Code remembers YOUR ShadowTagAi architecture (Judge #6, ShadowTag, JR framework) forever

**Cost**: $0.45 one-time + $0.02/month

## Installation (5 Minutes)

### Step 1: Setup Repository (30 seconds)

```bash
cd /path/to/erik-hancock-llm-memory
git remote add origin https://github.com/ehanc69/erik-hancock-llm-memory.git

```

### Step 2: Install Dependencies (1 minute)

```bash
pip install google-generativeai google-cloud-storage

```

### Step 3: Set API Key (10 seconds)

```bash
export GOOGLE_API_KEY=your_gemini_flash_api_key

```

### Step 4: Extract Conversations (2 minutes)

```bash
python scripts/extract_and_commit.py

```

Expected output:

```

Extracting Cursor conversations...
  Found 1,243 Cursor conversations
Extracting Claude Code conversations...
  Found 878 Claude Code conversations

Total: 2,121 conversations
Estimated tokens: 542,891
Estimated cost: $0.45

Creating snapshot v1.0.0...
  Snapshot: memory/snapshots/memory_v1.0.0.json
  Delta: memory/deltas/2025-01-16_delta.json

Committing to Git...
✓ Successfully committed and pushed to GitHub

```

### Step 5: Deploy to Claude Code (1 minute)

```bash
python scripts/claude_code_memory_local.py

```

Expected output:

```

✓ Memory installed to ~/.claude-code/memory.md
✓ Size: 47,234 bytes
✓ Config created at ~/.claude-code/config.json

Claude Code Memory Loaded
========================
Version: 1.0.0
Conversations: 2,121
Last Updated: 2025-01-16T12:34:56Z

Architecture contexts loaded:


- Judge #6 (98% coverage, p99 ≤90ms)


- ShadowTag 2.0 (DCT watermarking)


- Cor/NS (Execution brain + service mesh)

Ready to assist with ShadowTagAi-aligned decision making.

```

### Step 6: Test (30 seconds)

Restart Claude Code, then ask:

> "What is Judge #6?"

Expected response:
> Judge #6 is ShadowTagAi's content moderation system using Gemini + PyTorch + Rules engine. It provides 98% coverage with p99 latency ≤90ms for high-scale content filtering...

**✅ Installation complete!**

---

## Daily Usage

### Morning (Pull Updates)

```bash
./scripts/sync_to_devices.sh pull

```

### Evening (Push Changes)

```bash
./scripts/sync_to_devices.sh push

```

---

## Advanced: Vertex AI Workbench

### Setup (5 minutes)

```bash

# From Vertex Workbench terminal

python configs/vertex_workbench_config.py memory/current.json

```

### Usage

Restart Jupyter kernel, then:

```python

# Auto-loaded variable

print(shadowtagai_memory['version'])  # 1.0.0
print(shadowtagai_memory['shadowtagai_architecture']['judge_6'])

# Manual sync

sync_memory()

```

---

## Advanced: 4-LLM Orchestration

### Setup (10 minutes)

```bash

# Set all API keys

export GOOGLE_API_KEY=your_gemini_key
export ANTHROPIC_API_KEY=your_anthropic_key
export OPENAI_API_KEY=your_openai_key
export GROK_API_KEY=your_grok_key
export PERPLEXITY_API_KEY=your_perplexity_key

```

### Usage

```bash
python scripts/llm_blender_rotation.py

```

Flow:


1. **Grok**: Decomposes your query into threads


2. **Sonnet 4.5**: Assigns threads to Gemini (40%), GPT-5 (15%), Perplexity (5%)


3. **Round 1**: Each LLM answers


4. **Round 2**: Rotate right → peer review


5. **Round 3**: Rotate right → second review


6. **Claude Code**: Synthesizes final answer → publishes to GitHub

---

## Troubleshooting

### "No conversations found"

```bash

# Find your Cursor databases

find ~ -name "state.vscdb" 2>/dev/null

# Update paths in scripts/extract_and_commit.py

CURSOR_DB_PATHS = [
    Path("/path/you/found/workspaceStorage"),
    # ...
]

```

### "Memory not loaded in Claude Code"

```bash

# Verify file exists

cat ~/.claude-code/memory.md

# Re-run installation

python scripts/claude_code_memory_local.py

# Hard restart Claude Code (quit completely)

```

### "Git push failed with 403"

Your branch must start with `claude/`. Create it:

```bash
git checkout -b claude/add-superpowers-marketplace-011CUuLnhzCNrXYhosFmMAt9
git push -u origin claude/add-superpowers-marketplace-011CUuLnhzCNrXYhosFmMAt9

```

---

## What's Loaded into Memory?

When you deploy to Claude Code/Vertex, these contexts are available:

### ShadowTagAi Architectures



- **Judge #6**: Gemini + PyTorch + Rules (98% coverage, p99 ≤90ms)


- **ShadowTag 2.0**: DCT watermarking for content protection


- **Cor/NS**: Unified execution brain + service mesh

### Frameworks



- **JR Framework**: Purpose • Reasons • Brakes decision gate


- **Bootstrap Gates**: ROI ≥3× (18mo), LTV:CAC ≥4:1 (12mo), p99 ≤90ms, Security 100%

### LLM Allocation Strategy



- Gemini: 40% (bulk processing)


- Claude: 35% (coordination)


- GPT-5: 15% (structured output)


- Perplexity: 5% (research)


- Grok: 5% (intake)

### Operational Patterns



- Boy Scout Rule: Leave code cleaner


- Functions ≤20 lines, no external libs


- Evidence-only reasoning


- Security as 100% gate


- Simplicity mandate

### Tech Stack



- Extraction: 0xSero scripts


- Metadata: Gemini Flash 2.0


- Storage: GitHub + GCS


- Deployment: MacBook → Vertex → GKE

---

## Cost Summary

| Item | Cost | When |
|------|------|------|
| Initial extraction | $0.45 | One-time |
| GitHub storage | $0.00 | Monthly |
| GCS storage | $0.02 | Monthly (optional) |
| 4-LLM query | $0.08-0.12 | Per query (optional) |

**Total**: $0.45 one-time, then ~$0.02/month

---

## Next Steps



1. ✅ Extract conversations: `python scripts/extract_and_commit.py`


2. ✅ Deploy to Claude Code: `python scripts/claude_code_memory_local.py`


3. ✅ Test: Ask Claude Code about ShadowTagAi architecture


4. Optional: Deploy to Vertex (`vertex_workbench_config.py`)


5. Optional: Setup 4-LLM orchestration (`llm_blender_rotation.py`)


6. Optional: Enable GitHub Actions for daily auto-sync

---

## Support



- **Full docs**: See [README.md](README.md)


- **Deployment guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)


- **Issues**: https://github.com/ehanc69/erik-hancock-llm-memory/issues

**Built for ShadowTagAi by ShadowTagAi Team**
