# Gemini CLI & n-autoresearch/Kosmos/BioAgents Integration Guide

## Overview

This document outlines the usage of the Gemini CLI and the n-autoresearch/Kosmos/BioAgents agent swarm for the ShadowTag-v2 platform.

## Prerequisites

- **Python 3.13+** (System Python recommended)
- **Google Cloud SDK** (v548.0.0+)
- **Docker & Docker Compose**

## Setup

1. **Install Google Cloud SDK**:

   ```bash
   brew install --cask gcloud-cli
   export CLOUDSDK_PYTHON=$(which python3)
   export CLOUDSDK_PYTHON_SITEPACKAGES=1
   source "$(brew --prefix)/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/path.bash.inc"
   ```

2. **Start n-autoresearch/Kosmos/BioAgents Swarm**:
   ```bash
   docker-compose -f docker-compose.antigravity.yml up -d n-autoresearch/Kosmos/BioAgents
   ```

## n-autoresearch/Kosmos/BioAgents API Usage

The swarm exposes a REST API on port `8600`.

### Health Check

```bash
curl http://localhost:8600/health
```

### Run a Task (JURA Protocol)

Executes a task with cost-aware routing (FREE/FLASH/PRO tiers).

```bash
curl -X POST http://localhost:8600/task \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Analyze revenue model", "context_size": 1000}'
```

### Run Governance Task (PRO Tier)

Forces execution via the "Strategy" tier agents (Judge 6 / JURA).

```bash
curl -X POST http://localhost:8600/governance \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Scan for security leaks", "agents": 5}'
```

### Check Stats

```bash
curl http://localhost:8600/stats
curl http://localhost:8600/jura/stats
```

## Troubleshooting

- **Port Conflicts**: Ensure port `8600` is free.
- **API Key**: `GEMINI_API_KEY` must be set in `.env`.
- **Python Version**: If `gcloud` fails, verify `CLOUDSDK_PYTHON` points to Python 3.13.
