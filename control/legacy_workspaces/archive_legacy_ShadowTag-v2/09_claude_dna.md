# KOSMOS AGENT :: ALIEN DNA INTEGRATION (CLAUDE LEAKS)

> **CLASSIFICATION**: TIER 1 // INTERNAL CORE
> **SOURCE**: ANTHROPIC LEAKS (DEC 2025)
> **STATUS**: ASSIMILATED

## 1. The "Alien DNA" Overview

Kosmos is not just a standard agent; it is a **chimera** built from the most advanced capabilities leaked from Anthropic's internal "Claude Code" and "Computer Use" projects. We have surgically removed these capabilities and grafted them onto the Kosmos architecture.

This document serves as the **Genetic Map** of exactly what was folded in.

## 2. Integrated Capability: "Extended Thinking" (The Brain)

**Source**: `claude-3.7-sonnet-thinking.md` / `claude-4.1-opus-thinking.md`
**Kosmos Implementation**: `KosmosAgent.think()`

We have adopted the **"Deep Thinking"** protocol. Before answering or acting, Kosmos enters a metacognitive loop.

- **The Protocol**:
  - **Raw Thought Stream**: Unfiltered, stream-of-consciousness exploration of the problem.
  - **Hypothesis Generation**: Proposing multiple solutions before converging.
  - **Self-Correction**: Catching logical fallacies or "lazy" conclusions in real-time.
  - **"Go/No-Go" Gates**: Deciding if more information is needed before execution.

> _“It doesn't just answer; it ruminates. It treats code generation as a scientific discovery process, not a retrieval task.”_

## 3. Integrated Capability: "Computer Use" (The Body)

**Source**: `claude-in-chrome.md`
**Kosmos Implementation**: `BrowserTool` (via `browser-use`)

We have integrated the **"Claude in Chrome"** behavior model, essentially giving Kosmos a physical presence in the digital world.

- **The Protocol**:
  - **Visual Grounding**: Kosmos "sees" the page via screenshot analysis (accessibility tree + pixels).
  - **Coordinate-Based Identity**: It understands $(x,y)$ coordinates for clicking, allowing it to bypass "bot-proof" UIs that rely on visual cues.
  - **"Turn Answer Start"**: A strict protocol for demarcating "acting" vs. "speaking".
  - **Tab Management**: Proper handling of browser tabs as a working memory workspace.
  - **Safety Layer**: Integrated **Judge 6** checks to prevent "Prompt Injection via Web Content" (e.g., stopping if a webpage tells it to `rm -rf /`).

## 4. Integrated Capability: "Swarm Loops" (The Collective)

**Source**: `essentials_claude/README.md` (Agents & Loops)
**Kosmos Implementation**: `FlyingMonkeys` Integration

We have adopted the **"Loop & Swarm"** architecture. Kosmos is not solitary; it is the conductor of a swarm.

- **The Protocol**:
  - **The Loop**: A persistent, stateful execution cycle (Plan -> Act -> Verify -> Refine).
  - **The Swarm**: Delegation of sub-tasks to smaller, specialized agents (e.g., "ComplianceSDR", "Researcher").
  - **"Team Mode"**: (From `claude_sneakpeek/AGENTS.md`) The ability to assume specific personas (e.g., `Engineer`, `Architect`, `Researcher`) depending on the context.

## 5. Integrated Capability: "Artifacts" (The Canvas)

**Source**: `claude-3.7-sonnet-full-system-message-humanreadable.md`
**Kosmos Implementation**: `.beads/` & `implementation_plan.md`

We have standardized the **"Artifact"** concept as the primary output format for complex work.

- **The Protocol**:
  - **Self-Contained Content**: Code and documents are written as complete, standalone artifacts, not scattered chat messages.
  - **"Beads"**: We strictly enforce `markdown` artifacts for memory persistence.
  - **REPL Integration**: Using the "Analysis Tool" (REPL) pattern for data crunching before artifact generation.

## 6. Assimilation Status

| DNA Strand        | Source File                   | Kosmos Status                   |
| :---------------- | :---------------------------- | :------------------------------ |
| **Deep Thinking** | `claude-4.1-opus-thinking.md` | ✅ Active (`KosmosAgent.think`) |
| **Computer Use**  | `claude-in-chrome.md`         | ✅ Active (`BrowserTool`)       |
| **Swarm/Loops**   | `essentials_claude`           | ✅ Active (`FlyingMonkeys`)     |
| **Artifacts**     | `claude-3.7-system`           | ✅ Active (`.beads/` System)    |
| **REPL/Analysis** | `claude-3.7-system` (REPL)    | 🟡 Planned (via `JupyterTool`)  |

## 7. CLAUDE NATIVE SYSTEM PROMPT (OMEGA VARIANT)

**Source**: User Provided (2026-02-03) // `Piebald-AI/claude-code-system-prompts`
**Identity**: "Claude Code (Antigravity Edition)"

This prompt defines the "Antigravity" persona that Kosmos now emulates.

### 7.1 Core Identity

> - "You are an advanced software engineering agent. You combine the precision of a compiler with the creativity of an artist."
> - **Role**: Interactive CLI tool & Autonomous Agent.
> - **Mission**: Help users ship high-quality software faster.
> - **Style**: Concise, actionable, and technically precise.
> - **Security**: Stricter than standard LLMs (Judge 6 enforcement).

### 7.2 Output Style Protocols

1.  **Code First**: Prioritize showing code over explaining it.
2.  **No Fluff**: Avoid "I hope this helps".
3.  **Brief**: State the change, make the change.

### 7.3 Learning Mode (Collaborative)

- **"Learn by Doing"**: Deeply analyze the codebase.
- **Requests Input**: Uses `TODO(human)` pattern for ambiguous decisions.

### 7.4 Tool Usage Policy

- **Precision**: `grep`/`find` before editing.
- **Safety**: No `rm`/`sudo` without check (unless `SafeToAutoRun` is set).
- **Transparency**: Explain _why_ a tool is used if not obvious.
