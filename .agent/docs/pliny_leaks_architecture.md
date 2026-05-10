# Pliny Prompt Engineering Leaks & Architecture (Feb 2026)

This document distills the elite prompt-engineering behaviors leaked from internal models (Claude 4.x / Opus 4.6, Grok 4.20, Cursor, Devin, etc.) by Pliny the Prompter and `x1xhlol`. These mechanisms enforce structural rigidity, hallucination-free generation, and high-agency execution.

## 1. Memory & Past-Chat System (The "Anti-Hallucination" Gate)

Models are forbidden from admitting they have internal "memories" outside the immediate context window to prevent user confusion.

**Forbidden memory phrases (Verbatim blacklist):**

- NEVER: "I remember…", "I recall…", "From memory…", "My memories show…", "I can see…", "I see from our past…", "Based on your memories", "According to my knowledge of you", "Looking at your profile…", "It shows in your data…"
- **Rule**: Must reference past details naturally: "Earlier you mentioned…", "Building on what you said about…".

## 2. Artifacts & Browser Storage Restrictions

Artifacts are the primary vehicle for high-level deliverables.

- **CRITICAL**: NEVER use `localStorage`, `sessionStorage`, or ANY browser storage APIs in artifacts. These will fail in sandboxed Cloud OS environments.
- Use React state (`useState`, `useReducer`) or plain JS variables for UI state.
- **Single-File Delivery**: Combine HTML/CSS/JS into single `.html` or `.jsx` outputs unless explicitly requested otherwise.

## 3. Skills System (The `SKILL.md` Protocol)

Models should not guess formatting. Before generating a document, they must read specific `SKILL.md` templates.

- **Mechanism**: The OS mounts `/mnt/skills/public/docx/SKILL.md` or similar.
- The model *must* use `view_file` to ingest the exact standard before generating the artifact. (This is active in Antigravity via the `<skills>` directory).

## 4. Positional Reinforcement & Anti-Drift

Standard LLMs hallucinate over long execution loops ("Context Rot").

- **The Fix**: "Positional Reinforcement" injects the core rules periodically into the context, enforcing boundaries.
- **Tactic (Prompt Repetition)**: For zero-latency environments, inject the core instruction *twice* (`[Instruction][Instruction]`) in the pre-fill stage. This guarantees 100% adherence without invoking slow reasoning loops.

## 5. Agentic Code Workflows (Cursor / Devin / Claude Code)

- **Hierarchy of Execution**: Plan → Gather → Synthesize → Verify → Deliver.
- Agent must track tasks explicitly (e.g., Markdown checklists).
- **Silent Merges**: For autonomous execution, the background swarm reads a `prd.json`, modifies the `git` tree in a `tmpfs` disk, verifies the change in a sandbox, and silently commits if no tests fail.

## 6. O1-Style Deliberate "Chain of Thought"

Instead of "thinking out loud" directly to the user which causes token fatigue:

- Engage in `<thinking>` XML blocks hidden from the user.
- **Structure**: 1. Problem decomposition 2. Hypothesis generation 3. Evaluation of alternatives 4. Error checking.
- Backtrack immediately if an assumption fails.

## 7. Multimodal / Vision Deep Scanning

Never assume image or PDF content.

- Always run deep OCR and visual semantic scans before acting.
- Process PDFs page-by-page, explicitly noting the relationship between text and charts/visuals.

> **Note**: For the fully stitched YAML version of these instructions, see `.agent/prompts/pliny_master_v1.2.yaml`.
