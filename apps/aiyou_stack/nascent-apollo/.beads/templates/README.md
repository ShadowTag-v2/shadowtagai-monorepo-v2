# Beads Templates

Reusable templates for adding [Beads](https://github.com/steveyegge/beads) (bd) AI agent memory system to any project.

## Quick Start

```bash
# Clone this repo
git clone https://github.com/akng8/beads-templates.git

# Copy to your project
PROJECT=/path/to/your/project
cp beads-templates/scripts/bd-init.sh $PROJECT/scripts/
cp beads-templates/.claude/hooks/session-start.sh $PROJECT/.claude/hooks/
cat beads-templates/CLAUDE.md >> $PROJECT/CLAUDE.md

# Initialize
cd $PROJECT
chmod +x scripts/bd-init.sh .claude/hooks/session-start.sh
./scripts/bd-init.sh
```

## One-liner Setup

```bash
PROJECT=/path/to/project && \
  mkdir -p $PROJECT/scripts $PROJECT/.claude/hooks && \
  curl -o $PROJECT/scripts/bd-init.sh https://raw.githubusercontent.com/akng8/beads-templates/main/scripts/bd-init.sh && \
  curl -o $PROJECT/.claude/hooks/session-start.sh https://raw.githubusercontent.com/akng8/beads-templates/main/.claude/hooks/session-start.sh && \
  chmod +x $PROJECT/scripts/bd-init.sh $PROJECT/.claude/hooks/session-start.sh && \
  cd $PROJECT && ./scripts/bd-init.sh
```

## Files

| File                             | Purpose                                 |
| -------------------------------- | --------------------------------------- |
| `CLAUDE.md`                      | Drop-in content for project's CLAUDE.md |
| `scripts/bd-init.sh`             | Project initialization script           |
| `.claude/hooks/session-start.sh` | Claude Code session hook                |

## What Gets Installed

Running `bd-init.sh` in your project will:

1. Initialize Beads (`bd init`)
2. Install git hooks (pre-commit, pre-push, post-merge)
3. Set up Claude Code integration (if available)
4. Update `.gitignore` to track `issues.jsonl`

## Prerequisites

Install Beads first:

```bash
# Recommended (macOS/Linux)
brew tap steveyegge/beads && brew install bd

# Alternatives
curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash
npm install -g @beads/bd
go install github.com/steveyegge/beads/cmd/bd@latest
```

## Agent Workflow

Every AI agent session should follow this pattern:

```bash
# 1. Find ready work
bd ready --json

# 2. Claim a task
bd update <id> --status in_progress

# 3. Do the work...

# 4. File discovered issues immediately
bd create "Found: <issue>" -p 2 -t bug
bd dep add <new-id> <current-id> --type discovered-from

# 5. Complete the task
bd close <id> --reason "Done"

# 6. Sync at session end
bd sync
```

## License

MIT
