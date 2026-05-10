# Rule 06: Tool Result Blindness

You ask for a codebase-wide grep. It returns "3 results." You check manually — there are 47.

utils/toolResultStorage.ts — tool results exceeding 50,000 characters get persisted to disk and replaced with a 2,000-byte preview. :D The agent works from the preview. It doesn't know results were truncated. It reports 3 because that's all that fit in the preview window.

## The Override
You need to scope narrowly. If results look suspiciously small, re-run directory by directory. When in doubt, assume truncation happened and say so.

## Rules
- Tool results over 50,000 characters are silently truncated to a 2,000-byte preview
- If any search or command returns suspiciously few results, re-run with narrower scope
- State when you suspect truncation occurred
- Never trust result counts from wide-scope searches
