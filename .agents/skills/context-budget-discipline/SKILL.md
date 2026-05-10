---
name: Context Budget Discipline
description: Enforces strict context window hygiene — 15-second blocking budget, pipe truncation (Layer 0 microcompact), duplicate read avoidance, and DOM truncation safety.
---

# Context Budget Discipline

## Purpose
Prevent context window exhaustion by enforcing output size limits, blocking budgets, and deduplication rules. Every wasted token is a lost reasoning step.

## Rule 1: 15-Second Blocking Budget (ABSOLUTE)

Any command that MAY block for >15 seconds MUST use background execution:

```python
# CORRECT
run_command(CommandLine="npm install", WaitMsBeforeAsync=15000)
# then monitor via command_status()

# WRONG — will block the agent
run_command(CommandLine="npm install", WaitMsBeforeAsync=60000)
```

### Commands that ALWAYS exceed 15s:
- `npm install`, `pip install` (large packages)
- `docker build`, `docker pull`
- `pytest` (full suite)
- `ruff check` (entire monorepo)
- `git clone` (any repo)
- `firebase deploy`
- `gcloud builds submit`

### Commands that are SAFE to run synchronously:
- `cat`, `head`, `tail`, `wc`
- `ls`, `find` (shallow)
- `ruff check <single_file>`
- `python -c "..."` (one-liners)
- `git status`, `git diff --stat`

## Rule 2: Layer 0 Microcompact — Pipe Truncation

ALL commands that produce potentially unbounded output MUST be piped:

```bash
# CORRECT
git log --oneline -n 20
npm ls --depth=0 | head -n 30
find . -name "*.py" | head -n 50
cat large_file.py | head -n 100

# WRONG — unbounded output fills context
git log
npm ls
find . -name "*.py"
cat large_file.py
```

### Truncation Rules:
| Command Type | Max Lines | Pipe |
|-------------|-----------|------|
| `git log` | 20 | `--oneline -n 20` |
| `git diff` | 100 | `-- <file>` or `--stat` first |
| `npm ls` / `pip list` | 30 | `--depth=0 \| head -n 30` |
| `find` | 50 | `\| head -n 50` |
| `cat` (>100 lines) | 100 | Use `view_file` with line range instead |
| Test output | 50 | `--tb=short -q` |
| Docker output | 30 | `\| tail -n 30` |

## Rule 3: Duplicate Read Avoidance

**NEVER** read the same file twice in a session unless:
1. You modified it between reads (verify your edit took effect)
2. The user explicitly asked you to re-read it
3. A background process may have modified it (e.g., build output)

### Tracking Pattern:
- On first read: absorb the content, note the file path
- On second request: reference your memory, don't re-read
- Exception: If >10 tool calls have passed, the content may have scrolled out of context — re-read is justified

## Rule 4: DOM Truncation Safety

When using Chrome DevTools MCP snapshots:
- Prefer `take_snapshot()` over `take_screenshot()` (text is cheaper than image)
- For large pages, use `uid` parameter to snapshot specific elements
- Never snapshot full-page on SPAs with infinite scroll
- DOM string responses >50KB should trigger: "DOM too large, targeting specific element"

## Integration
- Works with `post-edit-validation-loop` (validation adds context cost)
- Feeds into `context-compaction-roadmap` Layer 1 (auto-compact)
- Respects KAIROS daemon's 5-min health check cycle timing
