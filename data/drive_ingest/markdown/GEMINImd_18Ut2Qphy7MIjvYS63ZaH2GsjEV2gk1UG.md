# GEMINI.md - Project Context for Gemini CLI

## Project Overview

**ShadowTag-v2-fastapi-services** - Multi-model AI infrastructure platform.

```
┌─────────────────────────────────────────────────────────────────┐
│ ARCHITECTURE: Multi-Model Pipeline with Gemini 3 Pro Leadership │
├─────────────────────────────────────────────────────────────────┤
│ Gemini 3 Pro  → Design & Creative Direction (~$0.087/design)    │
│ Perplexity    → Deep Research & Citations                       │
│ Grok Code     → Trend Analysis & Rapid Coding                   │
│ Opus 4.5      → Integration & Final Output                      │
└─────────────────────────────────────────────────────────────────┘
```

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

### n-autoresearch/Kosmos/BioAgentss Swarm
```
agents/autoresearch.py     # 600-agent swarm (570 Flash + 30 Pro)
bin/n-autoresearch/Kosmos/BioAgentss-server     # HTTP server on :8600
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

## Cross-Model Interop

This project uses SLIP SCALES for cross-LLM interoperability:
- Claude Code reads CLAUDE.md
- Gemini CLI reads GEMINI.md
- Both share atomic_pipeline/ for consistent behavior

---
*Last updated: November 27, 2025*
*Model: gemini-3-pro-preview*