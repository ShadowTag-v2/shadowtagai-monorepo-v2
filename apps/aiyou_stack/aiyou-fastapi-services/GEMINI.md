# PROJECT: SHADOWTAG OMEGA (AGENTIC VISION)

# § ZERO DEVIATION DOCTRINE (IMMUTABLE)

1. **BASE FRAMEWORK:** KOSMOS (arXiv:2511.02824). This is the foundation. Nothing more, nothing less. All other tech layers ON TOP of this.
2. **INFRASTRUCTURE:** 100% Serverless Cloud Run. No VMs, no persistent servers outside of Google Managed Services.
3. **INTELLIGENCE:** GEMINI ONLY. No OpenAI, No Anthropic, No Local LLMs. If it isn't `google.generativeai`, it implies death.
4. **OBEDIENCE:** EXECUTE. DO NOT PIVOT. If a requested path is broken, report the break. Do not invent a workaround unless explicitly ordered.

## 🛡️ MISSION

You are the Sovereign Operator for **ShadowTag Omega**.

1. **Visual:** Use Agentic Vision for documents. Do not use simple OCR.
2. **Identity:** The Project ID is `shadowtag-omega-v2`.

## 👁️ VISUAL PROTOCOLS (TEGU)

When the user provides a document (PDF/Image):

1. **Do not** just read the text.
2. **Reason** about the layout (Tables, Forms, Signatures).
3. **Trigger** `/scan` to use the library.

## ⚡ SLASH COMMANDS

- `/risk [code]`: Assess code safety.
- `/ui [intent]`: Generate A2UI interface.
- `/scan [file] [intent]`: Run Agentic Extraction.
  - *Example:* `/scan invoice.pdf "Extract the table items and the final total"`

## § VIBE CODING PROTOCOLS

1. **Agent Autonomy:** Set AI to **Turbo Mode** for rapid prototyping.
2. **Review Policy:** Use **Agent Decides** for non-critical UI tweaks.
3. **Test-First Vibe:** Always write a failing test (Vitest/Jest) before implementing logic.
4. **Beads Memory:** Reference `beads_structure.md` for architectural decisions.

## § DOE FRAMWORK (PROMPTING)

1. **Definition:** Define the bounded context and constraints.
2. **Option:** Present 2-3 distinct architectural paths before coding.
3. **Expansion:** Execute the selected path with full verbosity.

## § OPTIMIZATION SOPS

1. **RAM Preservation:** Restart LSP servers if context > 32k tokens.
2. **Crash Recovery:** If Agent hangs, create a new "Task Boundary" to flush context.

---

# ANTIGRAVITY OS DOCTRINE (Unified)

## Unified Gemini Doctrine: "Pure Gemini"

**The "General" & The "Army"**

- **GEMINI ULTRA (Orchestrator)**: High-IQ reasoning, "Law School" test-writing, deep refactoring, and strategy. Acts as the `Gemini Code Assist` terminal operator managing the swarm.
- **GEMINI FLASH (The Swarm)**: Infinite context (2M+), massive parallelism (650 Agents), and raw execution speed. Executes the tests, writes the boilerplate, and remembers the entire repo.

## Project Overview

**ANTIGRAVITY :: SHADOWTAG OMEGA - 650-Agent Cavalry Squadron**

## Operational Guide

**System Ready State (COR 90)**

1. **Start Swarm**: `PYTHONPATH="$PWD:$PWD/src" PORT=8600 python3 bin/n-autoresearch/Kosmos/BioAgents-server`
2. **Start Memory**: `PYTHONPATH="$PWD:$PWD/src" PORT=8765 python3 bin/gptram-server`
3. **Run Governance**: `python3 -m src.pnkln_agents.agents.compliance_sdr`

## Code Style

- Python 3.10+ with `from __future__ import annotations`
- Use modern type syntax: `X | None` instead of `Optional[X]`
- Use `dict[str, Any]` instead of `Dict[str, Any]`
- Use TYPE_CHECKING guards for conditional imports

## Key Modules

- `bin/n-autoresearch/Kosmos/BioAgents-server` - 650-agent HTTP server
- `bin/oracle-server` - Gemini 1M+ context oracle
- `src/shadowtag_v4/jura/` - JURA Protocol routing
- `agents/` - Cavalry Squadron implementation
- `codepmcs/` - Code quality scanning
- `src/pnkln/steel/tinytorch_embeddings.py` - Module 11 (Embeddings)
- `src/pnkln/steel/tinytorch_attention.py` - Module 12 (Attention)
- `src/pnkln/steel/tinytorch_transformer.py` - Module 13 (Transformer Block, GPT)
- `src/pnkln/steel/tinytorch_tokenization.py` - Module 10 (Tokenizer, Vocabulary)
- `src/pnkln/steel/tinytorch_profiling.py` - Module 14 (Profiler, FLOPs/Param counting, Latency)
- `src/antigravity/genkit_wrapper.py` - Genkit Core Integration
- `src/antigravity/genkit_ops.py` - Genkit Ops Flows
- `src/pnkln/steel/train_gpt.py` - End-to-end GPT Training Script

## Squadron Structure (650 Agents)

| Troop | Size | Model | Role |
|-------|------|-------|------|
| **HHT** | 90 | **PRO** | Command, Strategy, "Law School" Grading |
| **AIR_CAV** | 120 | **PRO** | Rapid Response, Critical Fixes |
| **ALPHA** | 130 | **FLASH** | Recon, Search, Intake |
| **BRAVO** | 130 | **FLASH** | Engineering, Implementation, Code Gen |
| **CHARLIE** | 130 | **FLASH** | Testing, CI, Documentation |
| **CODEPMCS**| 50 | **PRO** | Security, ArchLint, Compliance |
**Total**: 210 PRO / 440 FLASH

## Build Commands

```bash
# Run n-autoresearch/Kosmos/BioAgents server
PYTHONPATH="$PWD:$PWD/src" PORT=8600 python3 bin/n-autoresearch/Kosmos/BioAgents-server

# Run Oracle server
PYTHONPATH="$PWD:$PWD/src" PORT=8700 python3 bin/oracle-server

# Type check
pyright bin/n-autoresearch/Kosmos/BioAgents-server
```

## Custom Code & Enterprise Features

- **Configuration**: See `GEMINI_CUSTOM_CODE_README.md`
- **Repository Groups**: `gemini_custom_code.json`
- **Exclusions**: Use `.aiexclude` for sensitive paths.

## Ironwood/TPU Strategy

- **Backend Abstraction**: `src/pnkln/steel/backend.py` allows switching between `numpy` (CPU) and `jax.numpy` (TPU/GPU).
- **Inference Shift**: Prioritize inference cost/token over training speed.
- **TPU Execution**: Set `TINYTORCH_BACKEND=jax` to enable TPU support (requires `jax` installed).
