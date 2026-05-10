# Beads (bd) - AI Agent Memory System

> Drop this file into any project as CLAUDE.md or append to existing one.

Beads is a git-backed issue tracker designed for AI agents. It provides persistent, structured memory with dependency tracking, solving the "dementia problem" where agents lose context across sessions.

## Installation

```bash
# Recommended (macOS/Linux)
brew tap steveyegge/beads && brew install bd

# Alternatives
curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash
npm install -g @beads/bd
go install github.com/steveyegge/beads/cmd/bd@latest
```

## Project Setup

```bash
# Option 1: Use the init script (if copied to project)
./scripts/bd-init.sh

# Option 2: Manual setup
bd init              # Interactive
bd init --quiet      # Non-interactive (for automation)
bd init --stealth    # Local-only, not committed to git
bd hooks install     # Git hooks for auto-sync
bd setup claude      # Claude Code integration (if available)
```

## Agent Workflow (CRITICAL)

**Every session must follow this pattern:**

```bash
# 1. SESSION START - Find ready work
bd ready --json                # Returns unblocked tasks as JSON

# 2. CLAIM TASK - Prevent concurrent work
bd update <id> --status in_progress --assignee claude

# 3. DO THE WORK
# ... implement the task ...

# 4. DISCOVERED ISSUES - File immediately, don't ignore!
bd create "Found: <description>" -p 2 -t bug
bd dep add <new-id> <current-id> --type discovered-from

# 5. COMPLETE TASK
bd close <id> --reason "Implemented X"

# 6. SESSION END - Always sync!
bd sync
```

## Commands

### Issue Management

```bash
bd create "Title" -p 1 -t task    # Create issue
bd create "Epic" -p 0 -t epic     # Create epic
bd show <id>                      # View details
bd list --json                    # List all issues
bd update <id> --status in_progress
bd close <id> --reason "Done"
```

### Dependencies

```bash
bd dep add <child> <parent>              # Child blocked by parent
bd dep add <id> <id> --type blocks       # Explicit blocking
bd dep add <id> <id> --type related      # Related issues
bd dep add <id> <id> --type discovered-from  # Found during work
bd blocked                               # Show blockers
bd dep tree <id>                         # Hierarchical view
```

### Queries

```bash
bd ready                         # Unblocked work
bd ready --json --limit 5        # Top 5 as JSON
bd ready --assignee claude       # Assigned tasks
bd stats                         # Project statistics
```

### Sync

```bash
bd sync                          # Flush to git (run at session end!)
bd compact                       # Summarize old closed issues
```

## Issue Types

| Type      | Use For                      |
| --------- | ---------------------------- |
| `bug`     | Defects, errors              |
| `feature` | New capabilities             |
| `task`    | General work                 |
| `epic`    | Large features with subtasks |
| `chore`   | Maintenance, cleanup         |

## Priority Levels

| Flag   | Level    | Use For             |
| ------ | -------- | ------------------- |
| `-p 0` | Critical | Blocking production |
| `-p 1` | High     | Current sprint      |
| `-p 2` | Medium   | Normal (default)    |
| `-p 3` | Low      | Nice to have        |
| `-p 4` | Backlog  | Future              |

## Git Hooks (Auto-installed via `bd hooks install`)

| Hook         | Purpose                                      |
| ------------ | -------------------------------------------- |
| `pre-commit` | Exports changes to `.beads/issues.jsonl`     |
| `pre-push`   | Prevents push with uncommitted beads changes |
| `post-merge` | Imports updates after `git pull`             |

## Files

| File                  | Git                           |
| --------------------- | ----------------------------- |
| `.beads/issues.jsonl` | **Tracked** (source of truth) |
| `.beads/beads.db`     | Ignored (SQLite cache)        |
| `.beads/daemon.*`     | Ignored                       |

## .gitignore

Add to your project's `.gitignore`:

```
.beads/*
!.beads/issues.jsonl
```

## Why Beads?

1. **Dependencies are queryable** - `bd ready` returns only unblocked work
2. **Work is never lost** - Discovered issues get filed immediately
3. **Session persistence** - No re-reading context each session
4. **Multi-agent coordination** - Git handles merging
5. **Structured data** - `--json` flags for parsing
