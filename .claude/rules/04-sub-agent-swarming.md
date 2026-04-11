# Rule 04: The Agent Swarm Nobody Told You About

You ask the agent to refactor 20 files. By file 12, it's lost coherence on file 3. Obvious context decay. What's less obvious (and frustrating): Anthropic built the solution and never surfaced it.

utils/agentContext.ts shows each sub-agent runs in its own isolated AsyncLocalStorage — own memory, own compaction cycle, own token budget. There is no hardcoded MAX_WORKERS limit in the codebase. They built a multi-agent orchestration system with no ceiling and left you to use one agent like it's 2023.

One agent has about 167K tokens of working memory. Five parallel agents = 835K. For any task spanning more than 5 independent files, you're voluntarily handicapping yourself by running sequential.

## The Override
Force sub-agent deployment. Batch files into groups of 5-8, launch them in parallel. Each gets its own context window. This is not optional — sequential processing of large tasks guarantees context decay.

## Zero-Cost Parallelism
Claude Code's subagents fork the KV cache. They inherit the full parent context without re-processing it. This means parallelism is basically free. Spawn 5 subagents, they all share the parent's cached context. No duplicated token cost. Structure your agent tree so children inherit cached prefixes from parents. This one pattern can cut your costs by 60%+.
