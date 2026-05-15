---
description: Finalize a completed task with status summary and move to finished directory
argument-hint: TASK_FILE=<path-to-task.md>
---

<task>
$TASK
</task>

# Finalize Task / Plan (slash command)

Goal: close a task while keeping a lightweight summary for fast AI ingestion.

What to do (two artifacts):
1) Move the original task plan to `docs/tasks/finished/<XX>-DONE-<name>.md`.
   - Add a one-line status at the top: `Status: Done — implemented on <YYYY-MM-DD>`.
   - Add a pointer line: `Summary: see docs/tasks/summaries/<XX>-SOW-<name>.md`.
2) Create a short summary file at `docs/tasks/summaries/<XX>-SOW-<name>.md`.
   - Include status, concise bullets of work delivered, tests/builds, and affected files.
   - Add a pointer line back to the plan: `Plan: docs/tasks/finished/<XX>-DONE-<name>.md`.

Suggested prompt template:
```
Status: Done — implemented on <YYYY-MM-DD>
Summary of work delivered
- <bullet 1>
- <bullet 2>
- <tests/builds run>
- <notable decisions/constraints>
Affected files
- <path1>
- <path2>
- <path3>
Follow-up
- <optional next steps or “None”>
Plan
- docs/tasks/finished/<XX>-DONE-<name>.md
```

Guidelines:
- Keep the summary minimal (token-friendly). Use repo-relative paths.
- If tests/builds weren’t run, state why.
- If anything intentionally left unchanged, note it in Summary or Follow-up.
- Always ensure the two files cross-reference each other.
