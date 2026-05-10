---
name: magic-docs
description: Auto-maintained markdown documentation files that update from conversation context. Port of Claude Code MagicDocs service.
---

# Magic Docs — Auto-Maintained Documentation

**Source**: `src/services/MagicDocs/magicDocs.ts` + `prompts.ts` (Claude Code v2.1.91)
**Status**: CP-09 — Ported to Antigravity skill

## Overview

Magic Docs automatically maintains markdown documentation files marked with a special header.
When a file containing `# MAGIC DOC: [title]` is read during a session, the system registers
it for periodic background updates. A forked subagent updates the document with new learnings
from the conversation when the main loop is idle (no pending tool calls).

## Detection Protocol

1. **Header Pattern**: `# MAGIC DOC: <title>` — first line of the file.
2. **Optional Instructions**: Italicized line immediately after the header (`_instructions_` or `*instructions*`).
3. Registration is idempotent — once tracked, re-reads don't re-register.

## Update Trigger

- Only fires when `querySource === 'repl_main_thread'`
- Only fires when conversation is idle (no tool calls in last assistant turn)
- Updates are serialized via `sequential()` to prevent concurrent doc edits

## Antigravity Integration

In the Antigravity context, Magic Docs works as follows:

1. **Detection**: When any file is read (via `view_file` or similar), check for the Magic Doc header.
2. **Registration**: Track the file path in a session-scoped registry.
3. **Update Cycle**: After each assistant response without tool calls, iterate tracked docs:
   - Re-read the file to get current contents
   - Re-detect header (if header removed, untrack and skip)
   - Build update prompt with conversation context
   - Execute edit via the standard file edit tool (constrained to the Magic Doc file only)

## Custom Prompts

Users can override the default update prompt by placing a file at:
`~/.claude/magic-docs/prompt.md` (or equivalent config home)

Variables available for substitution:
- `{{docContents}}` — current file contents
- `{{docPath}}` — absolute file path
- `{{docTitle}}` — title from the Magic Doc header
- `{{customInstructions}}` — instructions from italicized subtitle

## Update Philosophy (from source)

- **BE TERSE**. High signal only.
- Document OVERVIEWS, ARCHITECTURE, and ENTRY POINTS — not code walkthroughs
- Keep documents CURRENT — update in-place, don't append changelog entries
- Remove outdated information rather than adding "Previously..." notes
- Fix obvious errors: typos, grammar, broken formatting

## Tool Constraints

The update subagent is restricted to:
- **File Edit** on the Magic Doc file ONLY
- No Bash, no file creation, no other tools
- Read-only access to conversation context

## Implementation Notes

- The `sequential()` wrapper ensures updates don't overlap when multiple Magic Docs are tracked
- File read uses a cloned `FileStateCache` with the doc's entry deleted to force re-read
- If the file is deleted or unreadable (ENOENT/EACCES), it's silently untracked
