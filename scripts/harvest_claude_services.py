import os
import json
from pathlib import Path

SKILLS_DIR = Path(".agents/skills")

skills_to_create = [
    {
        "name": "prevent-sleep-daemon",
        "description": "Standard Operating Procedure for preventing system sleep during long-running autonomous agent tasks using `caffeinate` or platform-native power management.",
        "content": """# Prevent Sleep Daemon

## Overview
This skill codifies the behavior of preventing the host machine or IDE from sleeping during long-running asynchronous tasks (e.g., mass refactoring, deployment, or mass ingestion). It was harvested from the `preventSleep.ts` architecture.

## Execution
- **macOS:** Wrap long-running shell commands with `caffeinate -i -s -u <command>`.
- **Linux:** Use `systemd-inhibit <command>`.
- **Node/Python:** If implementing a daemon, use native OS bindings or subprocess calls to acquire wake locks.

## Rules
1. Do NOT acquire wake locks for tasks expected to finish in under 60 seconds.
2. Always ensure the wake lock is released upon task completion, failure, or panic.
3. Log sleep prevention acquisition to `.beads/issues.jsonl` if the task is critical.
"""
    },
    {
        "name": "magic-docs-engine",
        "description": "Architecture for the Magic Docs engine, providing intelligent documentation retrieval, caching, and contextual injection.",
        "content": """# Magic Docs Engine

## Overview
Harvested from the `MagicDocs/` service, this skill defines the fallback behavior for when the Google Developer Knowledge MCP does not cover a specific framework or internal library.

## Protocol
1. If documentation is missing, the agent MUST fetch the remote documentation (e.g., via `curl` or browser automation).
2. The fetched documentation MUST be cached locally in `knowledge/magic_docs/`.
3. Only the most relevant snippets (extracted via `grep_search` or semantic search) should be injected into the context window to preserve the context budget.
"""
    },
    {
        "name": "progressive-tip-scheduler",
        "description": "Defines the tip registry and scheduler for surfacing contextual usage tips to operators.",
        "content": """# Progressive Tip Scheduler

## Overview
Harvested from the `tips/` architecture, this skill defines how the agent should surface non-intrusive, contextual tips to the user about CLI features, shortcuts, or optimization strategies.

## Rules
1. Do not spam the user. Tips should only be surfaced after successful completion of a task, or during idle "Away Summary" reports.
2. Maintain a registry of shown tips in the global memory (via `save_memory` with global scope) to prevent repetition.
3. Tips should focus on advanced features like "Did you know you can use `/notebooklm` to ingest this PDF securely?"
"""
    },
    {
        "name": "away-summary-generation",
        "description": "Protocol for generating an 'Away Summary' detailing autonomous work completed while the operator was offline or idle.",
        "content": """# Away Summary Generation

## Overview
Harvested from `awaySummary.ts` and `AgentSummary/`. When the agent operates in `STATE A` (YOLO) or executes a long-running batch job, it must generate a concise summary for the operator upon their return.

## Implementation
1. Track the start state and end state of the workspace.
2. Aggregate all tool uses, files modified, and errors encountered.
3. Write the summary to `MERGE_STATUS.md` or output it directly to the chat interface.
4. Format:
   - **Time Elapsed:** [Time]
   - **Actions Taken:** [Bullet points]
   - **Anomalies:** [Any errors or warnings]
"""
    },
    {
        "name": "voice-stt-input",
        "description": "Integration path for Voice and Speech-to-Text streaming and keyterm detection.",
        "content": """# Voice STT Input

## Overview
Harvested from `voice.ts` and `voiceStreamSTT.ts`. While `gemini-live-api-dev` handles building voice apps, this skill dictates how the agent handles voice transcriptions fed into its own context.

## Protocol
1. If the input contains `[VOICE TRANSCRIPT]`, the agent must account for potential STT hallucinations or phonetic misspellings (e.g., "right file" instead of "write file").
2. Keyterm detection (e.g., "stop", "undo") should trigger immediate safety circuit breakers.
3. Keep responses conversational and concise if the input modality indicates it was spoken.
"""
    },
    {
        "name": "active-token-estimation",
        "description": "Strict token counting and estimation interceptor to enforce the Context Budget Discipline.",
        "content": """# Active Token Estimation

## Overview
Harvested from `tokenEstimation.ts`. This skill works alongside the `context-budget-discipline` skill.

## Rule
1. Before performing a `read_file` or `run_shell_command` expected to yield > 5000 lines, the agent MUST estimate the token cost.
2. 1 line of code ≈ 10 tokens.
3. If the estimated cost exceeds 50,000 tokens for a single read, the agent MUST paginate, use `grep_search`, or use the `ast-grep` tool instead of a raw read.
"""
    },
    {
        "name": "lsp-passive-feedback",
        "description": "Deep integration with Language Server Protocol diagnostics for preemptive error correction.",
        "content": """# LSP Passive Feedback

## Overview
Harvested from `lsp/` (LSPServerManager, passiveFeedback.ts). This skill enhances the `post-edit-validation-loop`.

## Protocol
1. Instead of waiting for a manual `npm run lint` or `tsc` command, the agent should assume the IDE's LSP is generating diagnostics in real-time.
2. If available, read the `.lint-results/` or LSP dump files.
3. Preemptively auto-fix errors (e.g., missing imports, type mismatches) BEFORE reporting task completion to the user.
"""
    },
    {
        "name": "prompt-speculation-engine",
        "description": "Architecture for prompt caching, speculation, and auto-suggestion of next actions.",
        "content": """# Prompt Speculation Engine

## Overview
Harvested from `PromptSuggestion/`. This governs the generation of the 5-22 nag prompts/suggestions at the end of the agent's turn.

## Protocol
1. Suggestions must be speculative and anticipate the user's next logical request.
2. If a test fails, suggest "View test logs" and "Attempt auto-fix".
3. If a deployment succeeds, suggest "Run Lighthouse audit" and "View live URL".
4. Never suggest redundant or purely rhetorical actions (e.g., "Should I continue?").
"""
    },
    {
        "name": "team-memory-sync",
        "description": "Secure team memory synchronization and secret guarding protocol.",
        "content": """# Team Memory Sync

## Overview
Harvested from `teamMemorySync/` and `remoteManagedSettings/`.

## Protocol
1. Team memory (shared context, architecture decisions) MUST be synchronized via standard Git ops on `GEMINI.md` or `knowledge/` directory.
2. **Secret Guarding:** Before committing any shared memory, the agent MUST run the `gitleaks_guardian.py` or equivalent secret scanner to ensure no API keys or local `.env` variables leak into the shared repository context.
"""
    }
]

for skill in skills_to_create:
    skill_dir = SKILLS_DIR / skill["name"]
    skill_dir.mkdir(parents=True, exist_ok=True)
    
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(skill["content"])
    print(f"Created {skill_file}")

print("All 9 skills harvested and saved.")
