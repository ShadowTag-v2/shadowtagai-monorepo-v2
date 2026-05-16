# FlyingMonkeys VSCode Integration Guide

**Auto-Run-Command Setup for 200-Agent Swarm Development**

## Overview

This guide explains how to use the VSCode `auto-run-command` extension with FlyingMonkeys orchestrator to automatically configure your development environment when opening the project.

---

## Installation

### 1. Install Auto-Run-Command Extension

```bash
code --install-extension fabiospampinato.vscode-auto-run-command

```

Or install from VSCode Marketplace: [Auto Run Command](https://marketplace.visualstudio.com/items?itemName=fabiospampinato.vscode-auto-run-command)

### 2. Verify Extension Settings

The `.vscode/settings.json` file contains 4 auto-run rules that execute when VSCode opens:

| Rule | Condition | Action |
|------|-----------|--------|
| **Gemini API Auth** | Project = `aiyou-fastapi-services` + has orchestrator | Load `GEMINI_API_KEY` from GCP Secret Manager |
| **Python Interpreter** | Project has orchestrator | Set Python interpreter for swarm |
| **Dependencies** | Has `requirements.txt` | Install Gemini Antigravity packages |
| **Diagnostics** | Python files open | Enable Pyright for type checking |

---

## How It Works

### On VSCode Start (Automatic)

When you open `/Users/pikeymickey/Documents/Claude Code/Code/Claude Demo/aiyou-fastapi-services`:



1. **5-second delay** (allows VSCode to fully load)


2. **Rule evaluation**:
   ```

   ✓ hasFile: shadowtagai/agents/flyingmonkeys_orchestrator.py
   ✓ isRootFolder: aiyou-fastapi-services
   → Execute shell commands

 and VSCode commands
   ```


3. **Environment setup**:
   ```bash
   # Loads from GCP Secret Manager
   export GEMINI_API_KEY=$(gcloud secrets versions access latest \
     --secret='gemini-api-key' \
     --project='acquired-jet-478701-b3')

   # Sets GCP credentials
   export GOOGLE_APPLICATION_CREDENTIALS=$HOME/.config/gcloud/application_default_credentials.json
   ```


4. **Dependency installation**:
   ```bash
   pip install -q google-generativeai google-cloud-secret-manager
   ```

### Terminal Environment Variables

Auto-configured in every terminal session:

```bash
GEMINI_PROJECT_ID=acquired-jet-478701-b3
FLYINGMONKEYS_TOTAL_AGENTS=200
FLYINGMONKEYS_BOOTSTRAP_ROI=3.0          # ROI ≥ 3×
FLYINGMONKEYS_BOOTSTRAP_LTV_CAC=4.0       # LTV:CAC ≥ 4:1
FLYINGMONKEYS_BOOTSTRAP_P99_MS=90.0       # p99 ≤ 90ms

```

---

## VSCode Tasks

The `.vscode/tasks.json` provides 6 predefined tasks accessible via:

```

Cmd+Shift+P → Tasks: Run Task → [Choose task]

```

### Available Tasks

#### 🐒 Start FlyingMonkeys Orchestrator

```bash
python3 -m shadowtagai.agents.flyingmonkeys_orchestrator

```

Starts 200-agent swarm with:


- 120 specialists (60%)


- 80 generalists (40%)


- 8-hour shift rotation


- Gemini Antigravity API integration

#### 🧪 Test Gemini Antigravity API

```bash
python3 -m shadowtagai.agents.gemini_antigravity_api

```

Runs test suite:


- PiCO trace generation


- RLM (Recursive Language Model) query


- Performance SLA validation (p99 ≤ 90ms)

#### 📊 Show Agent Swarm Status

```bash
python3 -c "from shadowtagai.agents.core.legal_whiteboard import Whiteboard; ..."

```

Displays:


- Total agents


- Level distribution (0-5)


- Total tasks completed


- Average success rate


- Average knowledge nodes

#### 🔄 Run Shift Handoff

```bash
python3 -c "from shadowtagai.agents.core.shift_management import ShiftManager; ..."

```

Handoff process:


- NIGHT (50 agents) → DAY (100 agents) → EVENING (50 agents)


- 15-minute knowledge transfer overlap


- Git commit with shift summary

#### 🚀 Deploy to GKE (ShadowTagAi)

```bash
gcloud builds submit --config=cloudbuild.yaml --project=acquired-jet-478701-b3

```

Triggers Cloud Build:


- Builds container image


- Pushes to Artifact Registry (`shadowtagai-core`)


- Deploys to GKE `autopilot-cluster-1`

#### 🔍 Check Bootstrap Gates

```bash
python3 -c "from shadowtagai.agents.gemini_antigravity_api import ValueLock; ..."

```

Validates:


- ROI Gate: ≥ 3.0×


- LTV:CAC Gate: ≥ 4.0:1


- p99 SLA: ≤ 90.0ms

---

## Custom Rules

### Example: Run Custom Command on File Type

Add to `.vscode/settings.json`:

```json
{
  "condition": [
    "isRootFolder: aiyou-fastapi-services",
    "isLanguage: python"
  ],
  "command": "echo '🐒 FlyingMonkeys agent file detected!'",
  "message": "Agent development mode activated",
  "shellCommand": true
}

```

### Example: Auto-Format on Save for Agents

```json
{
  "condition": "hasFile: shadowtagai/agents/**/*.py",
  "command": "editor.action.formatDocument",
  "message": "Auto-formatting agent code"
}

```

### Example: Load Environment from .env File

```json
{
  "condition": "hasFile: .env.flyingmonkeys",
  "command": "set -a && source .env.flyingmonkeys && set +a",
  "message": "Loaded FlyingMonkeys environment",
  "shellCommand": true
}

```

---

## Troubleshooting

### Rule Not Executing

**Symptoms**: No notification appears, commands don't run

**Solutions**:


1. Check extension is installed: `code --list-extensions | grep auto-run-command`


2. Verify condition matches:
   ```bash
   pwd  # Should be in aiyou-fastapi-services
   ls shadowtagai/agents/flyingmonkeys_orchestrator.py  # Should exist
   ```


3. Check VSCode Output panel: `View → Output → Auto Run Command`

### API Key Not Loading

**Symptoms**: `GEMINI_API_KEY` is empty in terminal

**Solutions**:


1. Verify secret exists:
   ```bash
   gcloud secrets versions access latest \
     --secret='gemini-api-key' \
     --project='acquired-jet-478701-b3'
   ```


2. Check GCP authentication:
   ```bash
   gcloud auth application-default print-access-token
   ```


3. Manual fallback:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

### Python Interpreter Not Set

**Symptoms**: Import errors, wrong Python version

**Solutions**:


1. Manual selection: `Cmd+Shift+P → Python: Select Interpreter`


2. Verify Python path in `.vscode/settings.json`:
   ```json
   "python.pythonPath": "/usr/local/bin/python3"
   ```


3. Check virtual environment:
   ```bash
   which python3
   python3 --version  # Should be 3.10+
   ```

### Tasks Not Appearing

**Symptoms**: `Tasks: Run Task` menu is empty

**Solutions**:


1. Reload VSCode: `Cmd+Shift+P → Developer: Reload Window`


2. Verify `.vscode/tasks.json` exists


3. Check JSON syntax: `jq . .vscode/tasks.json`

---

## Performance Optimization

### Reduce Startup Delay

Default delay is 5 seconds. To reduce (if VSCode loads fast):

Edit extension setting:

```json
"auto-run-command.delay": 3000  // 3 seconds

```

### Disable Specific Rules

Comment out rules in `.vscode/settings.json`:

```json
// {
//   "condition": "hasFile: requirements.txt",
//   "command": "pip install -q ...",
//   ...
// }

```

### Cache Dependencies

Create local requirements cache:

```bash
pip download -d .pip-cache google-generativeai google-cloud-secret-manager

```

Update rule:

```json
{
  "command": "pip install --no-index --find-links=.pip-cache google-generativeai",
  ...
}

```

---

## Security Best Practices

### ✅ DO:



- Use GCP Secret Manager for API keys


- Load credentials from `~/.config/gcloud/application_default_credentials.json`


- Set `shellCommand: true` only for trusted commands


- Review auto-run rules before committing

### ❌ DON'T:



- Hardcode API keys in `.vscode/settings.json`


- Run arbitrary shell commands without verification


- Commit `.env` files with secrets


- Use `always` condition for destructive operations

---

## Advanced: Multi-Condition Rules

### Run Only in Container

```json
{
  "condition": [
    "isRunningInContainer",
    "hasFile: Dockerfile"
  ],
  "command": "echo 'Running in Docker container'",
  "shellCommand": true
}

```

### Project-Specific Python Version

```json
{
  "condition": [
    "isRootFolder: aiyou-fastapi-services",
    "hasFile: .python-version"
  ],
  "command": "pyenv install $(cat .python-version) --skip-existing && pyenv local $(cat .python-version)",
  "shellCommand": true
}

```

### Conditional GKE Deployment

```json
{
  "condition": [
    "hasFile: cloudbuild.yaml",
    "isRootFolder: aiyou-fastapi-services"
  ],
  "command": "echo '🚀 GKE deployment available. Run: gcloud builds submit'",
  "shellCommand": true
}

```

---

## Integration with FlyingMonkeys

### Agent-Specific Workflows



1. **Open Project** → Auto-load Gemini API key


2. **Edit Agent** → Auto-format with Black


3. **Save Changes** → Auto-run linter (Ruff)


4. **Run Tests** → Use `🧪 Test Gemini Antigravity API` task


5. **Deploy** → Use `🚀 Deploy to GKE` task

### Shift Handoff Automation

Create cron rule (external to VSCode):

```bash

# Run shift handoff every 8 hours

0 */8 * * * cd /Users/pikeymickey/Documents/Claude\ Code/Code/Claude\ Demo/aiyou-fastapi-services && python3 -m shadowtagai.agents.core.shift_management --handoff

```

### Continuous Monitoring

Use VSCode Terminal with watch:

```bash
watch -n 30 'python3 -c "from shadowtagai.agents.core.legal_whiteboard import Whiteboard; import json; print(json.dumps(Whiteboard.get_swarm_stats(), indent=2))"'

```

---

## Manifest Summary

| File | Purpose |
|------|---------|
| `.vscode/settings.json` | Auto-run rules + Python/editor config |
| `.vscode/tasks.json` | Predefined tasks for FlyingMonkeys ops |
| `shadowtagai/agents/flyingmonkeys_orchestrator.py` | 200-agent swarm orchestrator |
| `shadowtagai/agents/gemini_antigravity_api.py` | Gemini API client with PiCO/PRISM/Value.Lock |
| `task.md` | Development checklist |

---

## Bootstrap Gates Reference

All operations must meet these gates:

```python
ROI ≥ 3.0×          # Minimum 300% return on investment
LTV:CAC ≥ 4.0:1     # Customer lifetime value to acquisition cost ratio
p99 ≤ 90.0ms        # 99th percentile latency for Judge#6 governance

```

Validated via `🔍 Check Bootstrap Gates` task.

---

## Quick Start



1. Install auto-run-command extension


2. Open project: `/Users/pikeymickey/Documents/Claude Code/Code/Claude Demo/aiyou-fastapi-services`


3. Wait 5 seconds for auto-setup


4. Open terminal → verify `echo $GEMINI_API_KEY` is set


5. Run task: `Cmd+Shift+P → Tasks: Run Task → 🐒 Start FlyingMonkeys Orchestrator`

**Status**: ✅ FlyingMonkeys swarm ready for code generation!

---

## Support



- **Auto-Run-Command Docs**: https://marketplace.visualstudio.com/items?itemName=fabiospampinato.vscode-auto-run-command


- **VSCode Tasks**: https://code.visualstudio.com/docs/editor/tasks


- **Gemini API**: https://cloud.google.com/gemini/docs


- **GKE Deployment**: `cloudbuild.yaml` in project root

**Author**: Gemini 2.0 Flash (Antigravity)
**Created**: 2025-11-22
**Bootstrap Gates**: ROI ≥3×, LTV:CAC ≥4:1, p99≤90ms
