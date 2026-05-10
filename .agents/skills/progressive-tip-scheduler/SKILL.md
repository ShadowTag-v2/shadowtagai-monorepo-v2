# Progressive Tip Scheduler

## Overview
Harvested from the `tips/` architecture, this skill defines how the agent should surface non-intrusive, contextual tips to the user about CLI features, shortcuts, or optimization strategies.

## Rules
1. Do not spam the user. Tips should only be surfaced after successful completion of a task, or during idle "Away Summary" reports.
2. Maintain a registry of shown tips in the global memory (via `save_memory` with global scope) to prevent repetition.
3. Tips should focus on advanced features like "Did you know you can use `/notebooklm` to ingest this PDF securely?"
