# Active Token Estimation

## Overview
Harvested from `tokenEstimation.ts`. This skill works alongside the `context-budget-discipline` skill.

## Rule
1. Before performing a `read_file` or `run_shell_command` expected to yield > 5000 lines, the agent MUST estimate the token cost.
2. 1 line of code ≈ 10 tokens.
3. If the estimated cost exceeds 50,000 tokens for a single read, the agent MUST paginate, use `grep_search`, or use the `ast-grep` tool instead of a raw read.
