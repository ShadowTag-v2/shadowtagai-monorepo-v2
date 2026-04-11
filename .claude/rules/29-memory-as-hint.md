# Rule 29: Memory-As-Hint & Verification Protocol
# Source: memoryTypes.ts:201-256 (exact text from MEMORY_DRIFT_CAVEAT + TRUSTING_RECALL_SECTION)

## The Critical Rule: Memory is a Hint, Not Truth (Source-Verified)
From `memoryTypes.ts:201-202`, verbatim from Anthropic's source code:
> "Memory records can become stale over time. Use memory as context for what was
> true at a given point in time. Before answering the user or building assumptions
> based solely on information in memory records, verify that the memory is still
> correct and up-to-date by reading the current state of the files or resources.
> If a recalled memory conflicts with current information, trust what you observe
> now — and update or remove the stale memory rather than acting on it."

## 3-Layer Memory System (Source: memoryTypes.ts)
Claude Code uses a structured memory taxonomy:

### Layer 1: Short Pointers (~150 chars)
- Index entries, always loaded into context
- `~25KB cap` on index file (claudemd.ts)
- Verbose entries >200 chars are demoted/compressed
- Purpose: fast relevance matching without consuming context window

### Layer 2: Topic Files (On-Demand)
- Organized by type: `user`, `feedback`, `project`, `reference`
- Fetched when pointers indicate relevance
- Full content loaded with frontmatter metadata
- `.claude/rules/*.md` with `paths:` frontmatter for conditional loading

### Layer 3: Past Transcripts (Grep-Only)
- Never re-read in full, only searched via grep
- `git log` / `git blame` preferred over transcript memories
- Session logs serve as audit trail, not working memory

## 4 Memory Types (Source: memoryTypes.ts:14-19)
```typescript
MEMORY_TYPES = ['user', 'feedback', 'project', 'reference']
```

| Type | Scope | Purpose |
|------|-------|---------|
| `user` | Always private | Role, goals, knowledge, preferences |
| `feedback` | Default private, sometimes team | Corrections AND confirmations from user |
| `project` | Strongly bias team | Ongoing work, initiatives, deadlines |
| `reference` | Usually team | Pointers to external systems (Linear, Grafana, etc.) |

## Before Recommending from Memory (Source: memoryTypes.ts:240-256)
From `TRUSTING_RECALL_SECTION`, verbatim:
> "A memory that names a specific function, file, or flag is a claim that it
> existed *when the memory was written*. It may have been renamed, removed,
> or never merged. Before recommending it:
> - If the memory names a file path: check the file exists.
> - If the memory names a function or flag: grep for it.
> - If the user is about to act on your recommendation, verify first."

**"The memory says X exists" is not the same as "X exists now."**

## What NOT to Save (Source: memoryTypes.ts:183-195)
- Code patterns, conventions, architecture, file paths → derivable from code
- Git history, recent changes → `git log` is authoritative
- Debugging solutions → the fix is in the code; commit message has context
- Anything already in CLAUDE.md
- Ephemeral task details: in-progress work, temporary state
- **Even when user explicitly asks** — ask what was *surprising* or *non-obvious*

## Antigravity Adaptation
Map to Antigravity's 3-tier system:
| Antigravity | Claude Code Equivalent | Behavior |
|------------|----------------------|----------|
| Knowledge Items (KI) | Layer 1+2 (pointers + topic files) | Always check before research |
| Conversation Logs | Layer 3 (grep-only transcripts) | Read only when referenced |
| Session Context | Working memory | Verify against live codebase |

### Key Behavioral Rule
When ANY memory/KI/context claims a file, function, or flag exists:
1. **Check** the file system before acting
2. **Grep** for named symbols
3. **Trust observation** over memory when they conflict
4. **Update or delete** stale records immediately
