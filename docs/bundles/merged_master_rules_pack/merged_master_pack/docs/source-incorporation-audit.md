# Source Incorporation Audit

## arXiv 2512.14982 — Prompt Repetition Improves Non-Reasoning LLMs

### Added from the paper

- `docs/prompt-repetition-doctrine.md`
- `docs/prompt-repetition-benchmark-plan.md`
- `prompts/non-reasoning-repeat-template.md`
- `prompts/non-reasoning-repeat-router.md`
- `scripts/prompt_repeat.py`
- `scripts/prompt_repeat_examples.py`

### Practical changes

- defines when repetition is the default
- defines when to avoid blind repetition
- includes x2 and x3 variants
- separates non-reasoning and reasoning use cases
- adds a benchmark/eval plan instead of relying on vibes

## Bash monorepo / MCP pack

This upgraded pack incorporates the monorepo/control-plane bash pack as actual files under `operations/`, but makes it brand-agnostic.

### Preserved ideas

- one canonical workspace manifest
- one canonical MCP config
- adapter config demotion
- product path vs lab path split
- env templates
- database tools manifest
- verification and root-guard scripts
- recovered operational scripts
- product spec placeholders
- thread audit protocol and next-order checklist

### Brand-agnostic mapping

- `CounselConduit` -> `product_app`
- `uphillsnowball` -> `research_lab`
- `antigravity-mcp-config.json` -> `workspace-mcp-config.json`
- product-specific headings -> generic workspace/control-plane headings
