# Rule 42: Context Window Hygiene Protocol

> Derived from: iamfakeguru/claude-md, guanyang/context-compression, guanyang/context-degradation, repowise-dev/claude-code-prompts

## Re-Read Before Edit

Before ANY file edit: re-read the file. After editing: read it again.
The Edit tool fails silently on stale old_string matches.

## Dead Code Burns Tokens

Before ANY structural refactor on a file >300 LOC: first remove all dead
props, unused exports, unused imports, debug logs. Commit cleanup
separately. Dead code burns tokens that trigger compaction faster.

## Context Degradation Signals

Recognize three degradation signals and respond:
1. **Lost-in-middle effect**: Attention weakens for mid-context content → force re-read of critical files
2. **Attention scarcity**: Too many competing items → narrow scope, use sub-agents
3. **Context poisoning**: Irrelevant content displaces useful content → run /compact proactively

## Sub-Agent Context Splitting

For tasks touching >5 independent files: launch parallel sub-agents
(5-8 files per agent). Each gets its own ~167K context window. Sequential
processing of 20 files guarantees context decay by file 12.

## After 10+ Messages

After 10+ messages in a session: re-read any file before editing it.
Auto-compaction may have destroyed your memory of its contents.

## Tool Result Truncation

Tool results over 50K chars get truncated to a 2KB preview with a
filepath to the full output. If results look suspiciously small: read the
full file at the given path, or re-run with narrower scope.
