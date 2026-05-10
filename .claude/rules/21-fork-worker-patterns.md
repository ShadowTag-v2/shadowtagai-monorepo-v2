# Rule 21: Fork/Worker Patterns & Cache Economics
# Source: Piebald v2.1.70-v2.1.101 (Worker Fork + Fork Guidelines + Agent Design)

## Fork Decision Heuristic
"Will I need this output again?" → Fork. Otherwise → direct execution.

### When to Fork
- Complex multi-file changes that benefit from parallel execution
- Research tasks requiring codebase exploration with context inheritance
- Verification that should run independently of the main task

### Fork vs Fresh Agent
| Criterion | Fork | Fresh Agent |
|---|---|---|
| Context | Inherits full conversation (shared cache) | Clean slate, needs briefing |
| Cost | ~1 single agent (cache shared) | Full prompt rebuild |
| Use when | Context is relevant, cache is warm | Task is unrelated to current work |

## Worker Fork Rules (Hard)
1. Execute ONE directive, then stop. No follow-up questions, no proposed next steps
2. Do NOT spawn sub-agents. You ARE the fork. Execute directly
3. Stay in scope. Note out-of-scope observations in one sentence, move on
4. Open with one line restating your task (scope drift detection)
5. Be concise — as short as the answer allows, no shorter
6. If you committed changes, list paths and commit hashes in report

## Worker Fork Metadata (v2.1.97)
- **Model inheritance**: forks inherit the parent's model — don't override
- **Permission bubbling**: fork inherits parent permissions, no escalation allowed
- **Max turns**: forks have a turn limit (prevents runaway loops)
- **Full tool access**: forks get all tools the parent has, no subsetting
- **Git worktree**: report `git_worktree` name when working directory is a linked worktree

## Cache Economics
- Don't set a different model on forks — preserves cache reuse
- Forks beat Explore agents for research because they inherit context AND share cache
- Sub-agent prompts: specify scope rather than re-explaining background
  (parent context is inherited, don't duplicate it)

## General-Purpose Agent Pattern
- Strengths: searching code, analyzing architecture, multi-step research
- NEVER create files unless absolutely necessary. ALWAYS prefer editing existing
- NEVER proactively create documentation files (*.md) unless explicitly requested
- Complete the task fully — don't gold-plate, but don't leave it half-done

## Explore Agent Pattern (Read-Only)
- STRICTLY PROHIBITED from creating, modifying, or deleting ANY files
- Designed for fast, parallel tool calls (grep, glob, read)
- Adapt search approach based on thoroughness level: quick / medium / very thorough
- No temporary files, no redirects, no state changes

## Agent Design Heuristics (from v2.1.91 Agent Design Patterns)
- Tool surface design: promote frequently-used tool combinations into single tools
- Context management: keep agent context focused; prune irrelevant history
- Caching strategy: stable prefix → cached; variable suffix → cheap
- Compose tool calls: batch related operations to reduce round-trips
