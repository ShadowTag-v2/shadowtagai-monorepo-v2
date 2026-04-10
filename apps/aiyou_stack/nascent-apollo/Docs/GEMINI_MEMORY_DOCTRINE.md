# JUDGE 6: GEMINI MEMORY DOCTRINE

**Goal:** Prevent the AI from making the same mistake twice.

## PILLARS

1. **Interaction Learning:** Parse Merged PRs for human overrides.
2. **Rule Generalization:** Convert specific overrides into general rules (e.g., "Allow wildcards in tests").
3. **Contextual Application:** Filter findings based on repository context.

## IMPLEMENTATION

- **Static Memory:** `Docs/styleguide.md`
- **Dynamic Memory:** `src/governance/memory/learned_rules.json`
- **The Filter:** `JudgeSixSentinel.apply_memory_filter(findings)`
