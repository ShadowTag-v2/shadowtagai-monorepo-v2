# GEMINI.md - Project Context for Gemini CLI

## Project Overview

**shadowtag_v4-fastapi-services** - Multi-model AI infrastructure platform.

```

┌─────────────────────────────────────────────────────────────────┐
│ ARCHITECTURE: Pure Gemini Pipeline (Google Stack)               │
├─────────────────────────────────────────────────────────────────┤
│ Gemini 2.0 Flash → Speed & Execution (90% of workload)          │
│ Gemini 3 Pro     → Design & Governance (10% of workload)        │
│ Google Vertex    → Search & Grounding                           │
│ Google ADK       → Agent Orchestration                          │
└─────────────────────────────────────────────────────────────────┘

```

## 🚦 Operational Guide

The system is ready for use.



1. **Start the Swarm Server**
   ```bash
   PYTHONPATH="$PWD:$PWD/src" PORT=8600 python3 bin/n-autoresearch/Kosmos/BioAgents-server
   ```



2. **Run a Governance Test**
   ```bash
   PYTHONPATH=. python3 -m src.pnkln_agents.agents.compliance_sdr
   ```



3. **Check Health**
   ```bash
   curl http://0.0.0.0:8600/health
   ```

**Note**: The repository is now fully synced with origin/main. All temporary extraction scripts have been cleaned up.

## @wquguru's 12 Best Practices Applied



1. **YOLO Mode**: Enabled for rapid iteration


2. **Context Files**: GEMINI.md + CLAUDE.md for cross-model memory


3. **Model Selection**: gemini-3-pro-preview for design leadership


4. **Structured Output**: JSON mode for machine-readable specs


5. **Extended Thinking**: Enabled for complex architecture decisions


6. **Code Execution**: Sandbox enabled for validation


7. **Web Grounding**: Research enabled for current patterns


8. **Temperature**: 0.7 for creative, 0.3 for deterministic


9. **Token Limits**: 16384 max output for comprehensive responses


10. **Timeout**: 180s for complex reasoning chains


11. **Streaming**: Enabled for responsive UX


12. **Cost Tracking**: ~$0.087 per design at 7K tokens

## Core Components

### Atomic Pipeline

```

atomic_pipeline/
├── orchestrator.py          # Main pipeline coordinator
├── deploy_flow.py           # 5-prompt deploy workflow
├── antigravity_runner.py    # Chrome automation
└── clients/
    └── gemini_client.py     # Gemini 3 Pro API client

```

### Dashboards

```

dashboards/
└── training_dashboard.py    # Rich terminal GPU job manager

```

### n-autoresearch/Kosmos/BioAgents Swarm

```

agents/autoresearch.py     # 600-agent swarm (570 Flash + 30 Pro)
bin/n-autoresearch/Kosmos/BioAgents-server     # HTTP server on :8600

```

## Gemini 3 Pro Integration

### Design Leadership Pattern (@omarsar0)

```python
from atomic_pipeline.clients import GeminiClient, GeminiModel

async with GeminiClient() as client:
    # Design spec generation
    spec = await client.design_component(
        description="Real-time chat component",
        framework="React",
        style_system="MUI"
    )

    # Requirements parsing
    tasks = await client.parse_requirements("""
        Build user authentication with OAuth2
        Add rate limiting at 100 req/min
        Implement WebSocket for real-time updates
    """)

    # Test generation
    tests = await client.generate_tests(
        code=implementation,
        framework="pytest",
        coverage_target="comprehensive"
    )

```

### Available Models

| Model | Use Case | Cost |
|-------|----------|------|
| gemini-3-pro-preview | Design, complex reasoning | ~$14/M |
| gemini-3-flash | Fast inference, 1M context | ~$0.15/M |
| gemini-2.5-pro-preview | Stable production | ~$7/M |
| gemini-2.0-flash | Economical | ~$0.075/M |
| gemini-2.0-flash-lite | Ultra-fast | ~$0.02/M |

## Deploy Flow (5-Prompt Pattern)

```

IDEA → SCAFFOLD → IMPLEMENT → TEST → DEPLOY
  ↓        ↓          ↓         ↓       ↓
$0.087   $0.02    $0.05/atom  $0.03   FREE

```

### Usage

```bash
python -m atomic_pipeline.deploy_flow "Build a real-time chat API" cloud-run

```

### Targets



- `cloud-run` - Google Cloud Run (default)


- `gke` - Google Kubernetes Engine


- `vertex` - Vertex AI Workbench


- `colab` - Google Colab notebook


- `local` - Local development

## JURA Protocol Tiers

```

FREE  → gemini-2.0-flash-lite (emergencies only)
FLASH → gemini-2.0-flash / gemini-3-flash (standard ops)
PRO   → gemini-3-pro-preview (design leadership)

```

## Key Environment Variables

```bash
GEMINI_API_KEY=your-api-key
GOOGLE_CLOUD_PROJECT=acquired-jet-478701-b3

```

## Conventions

### Code Style



- Python 3.11+ with type hints


- Pydantic for data validation


- Async/await for I/O operations


- Rich library for terminal UI

### File Naming



- Snake_case for Python files


- PascalCase for classes


- lowercase-kebab for directories

### Documentation



- Docstrings with Args/Returns


- Type annotations required


- CLAUDE.md for Claude Code context


- GEMINI.md for Gemini CLI context

## Memory Protocol

On completion of significant actions:

```bash
git add . && git commit -m "Gemini: [action] [$(date)]"

```

## Antigravity Status (December 2025)

### Knowledge Base



- **Status**: COMPLETE


- **Repos**: 99 forked to `ehanc69`, cloned, and flattened


- **Index**: `~/antigravity-flattened/index.json`


- **Sync**: Cloud Function `sync-antigravity-forks` deployed (Daily @ 3:00 AM UTC)

### n-autoresearch/Kosmos/BioAgents Swarm



- **Status**: 100% Readiness (600 Agents)


- **Control**: Advanced Agentic Control (AAC-2025)


  - **Circuit Breakers**: Representation-level intervention


  - **Scopes**: AWS Scoping Matrix (Scope 1-4)


  - **Verification**: VeriGuard (Correctness-by-Construction)


  - **Coordination**: A2A Protocol (Crypto-Identity)


- **Endpoint**: `http://127.0.0.1:8600`


- **Composition**:


  - **HHT**: 90 agents (Governance - Pro)


  - **AIR CAV**: 120 agents (Scouts - Pro)


  - **ALPHA**: 130 agents (Armor - Flash)


  - **BRAVO**: 130 agents (Stryker - Flash)


  - **CHARLIE**: 130 agents (Bradley - Flash)

### Code Assist Integration



- **API**: `cloudaicompanion.googleapis.com` ENABLED


- **IAM**: 5 roles granted to `redacted@shadowtag-v4.local`


- **Bridge**: `agents/` created for Code Assist Bridge

## Cross-Model Interop

This project uses SLIP SCALES for cross-LLM interoperability:


- Claude Code reads CLAUDE.md


- Gemini CLI reads GEMINI.md


- Both share atomic_pipeline/ for consistent behavior

---
*Last updated: December 03, 2025*
*Model: gemini-3-pro-preview*
