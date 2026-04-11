# Rule 05: The 2,000-Line Blind Spot

The agent "reads" a 3,000-line file. Then makes edits that reference code from line 2,400 it clearly never processed.

tools/FileReadTool/limits.ts — each file read is hard-capped at 2,000 lines / 25,000 tokens. Everything past that is silently truncated. The agent doesn't know what it didn't see. It doesn't warn you. It just hallucinates the rest and keeps going.

## The Override
Any file over 500 LOC gets read in chunks using offset and limit parameters. Never let it assume a single read captured the full file. If you don't enforce this, you're trusting edits against code the agent literally cannot see.

## Rules
- Each file read is capped at 2,000 lines
- For files over 500 LOC, use offset and limit parameters to read in sequential chunks
- Never assume you have seen a complete file from a single read
- If editing code near the end of a large file, explicitly read that section first
