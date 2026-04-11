# Rule 45: Beads Memory Integration Protocol

> Derived from: akng8/beads-templates, miqcie/grepai-beads-helpers

## Agent Workflow Pattern

Every session must follow this memory lifecycle:

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

## Find → Read → Remember → Code Pattern

1. Check beads for existing decisions: `bd search "topic" --json`
2. Find relevant files with semantic search (grepai or grep)
3. Read FULL files (not just snippets)
4. Store new decisions in beads: `bd create "Decision" --body "Details" --tags "tag1,tag2"`

## Key Behaviors

- Automatic queries at session start, no user confirmation needed
- Results loaded silently and used for context
- All architectural decisions stored as beads for cross-session persistence
- Use `--json` output for structured data processing

## Integration with Existing Memory Systems

- `.beads/issues.jsonl` → canonical issue tracker
- `~/.claude/homunculus/` → instinct system (auto-promoted from beads)
- LanceDB → vector embeddings of bead content
