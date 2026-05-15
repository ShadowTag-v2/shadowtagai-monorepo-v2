# Rule 08: Edit Integrity

Before EVERY file edit, re-read the file. After editing, read it again to confirm the change applied correctly.

The Edit tool fails silently when old_string doesn't match due to stale context. Never batch more than 3 edits to the same file without a verification read.

## Rules
- Re-read file BEFORE every edit
- Re-read file AFTER every edit to confirm
- Never batch >3 edits to the same file without verification read
- If an edit silently fails, re-read and retry with fresh context
- Stale context from auto-compaction is the #1 cause of silent edit failures

## Absolute Paths Always (v2.1.97)
- ALWAYS use absolute file paths for Read, Write, and Edit operations
- No conditional relative paths — this was removed in v2.1.97
- Agent threads, worker forks, and parent contexts all use absolute paths unconditionally
- Rationale: relative paths resolve differently in forked agents vs parent CWD
