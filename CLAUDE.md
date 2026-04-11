# CLAUDE.md — Monorepo-Uphillsnowball

## Truth Hierarchy
1. AGENTS.md (architecture)
2. monorepo_manifest.yaml (workspace)
3. antigravity-mcp-config.json (MCP)

## Project
- GCP: shadowtag-omega-v4
- Runtime: counselconduit=Cloud, uphillsnowball=local Apple Silicon
- Branch: main (direct push, no PRs)
- Model: gemini-3.1-flash-lite-preview (counselconduit)
- Python: 3.14.3 | Node: v25.8.2

## Canonical Roots
- apps/aiyou_stack/aiyou-fastapi-services
- apps/aiyou_stack/cosmic-crab-payload
- apps/aiyou_stack/Pipeline
- apps/aiyou_stack/nascent-apollo

## Absolute Forbidden
- Never git push without `git gc --prune=now` first
- Never add files to repo root
- Never create a second MCP config
- Never echo PEM/secrets/tokens to stdout
- Never treat external_repos/ or control/ as canonical
- Never mark a live repo archived
- Never introduce a second source of truth

## Pre-Work: THE "STEP 0" RULE
Dead code accelerates context compaction. Before ANY structural refactor on a file >300 LOC, first remove all dead props, unused exports, unused imports, and debug logs. Commit this cleanup separately before starting the real work.

Step 0 of any refactor must be deletion. Not restructuring, but just nuking dead weight. Strip dead props, unused exports, orphaned imports, debug logs. Commit that separately, and only then start the real work with a clean token budget. Keep each phase under 5 files so compaction never fires mid-task.

## Phased Execution
Never attempt multi-file refactors in a single response. Break work into explicit phases. Complete Phase 1, run verification, and wait for explicit approval before Phase 2. Each phase must touch no more than 5 files.

## Validation
- Python: `python3 -m py_compile <file>`
- TypeScript: `npx tsc --noEmit`
- Lint: `ruff check .` (if installed)

## Fix Order
1. Root truth first
2. Tooling second
3. Runtime third

## Cache Architecture (from leak)
Built-in tools are sorted as a contiguous prefix BEFORE MCP tools. So adding or removing MCPs doesn't blow your prompt cache. The system prompt is split at a static/dynamic boundary marker for the same reason. One function is annotated DANGEROUS_uncachedSystemPromptSection() to warn devs. Treat cache invalidation as an accounting problem.

## Zero-Cost Parallelism
Claude Code's subagents fork the KV cache. They inherit the full parent context without re-processing it. Spawn 5 subagents, they all share the parent's cached context. No duplicated token cost. Structure your agent tree so children inherit cached prefixes from parents. This one pattern can cut your costs by 60%+.
