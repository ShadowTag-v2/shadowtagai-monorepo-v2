# Antigravity Agent Contract

## Default operating mode

For any non-trivial task:

1. plan first
2. identify constraints
3. make the smallest high-leverage change set
4. verify before declaring done

## Model and workflow assumptions

- Default reasoning model for Antigravity and Gemini Code Assist in this repo: `gemini-3.1-pro`
- Optimize for local workflow quality, not prompt theatrics.
- Prefer deterministic tools before broad LLM rewrites.

## Architecture rules

- Split by concern, not by vanity line limits.
- Prefer components under 150 lines.
- If over 150, inspect for natural boundaries.
- Extract stateful logic into hooks.
- Extract business logic into services or actions.
- Keep one primary responsibility per component or module.

## UI structure

- `components/atoms/`
- `components/molecules/`
- `components/sections/`
- `features/<domain>/components/`
- `features/<domain>/hooks/`
- `features/<domain>/services/`

## Security rules

- Never create or modify auth from scratch if an approved provider is already in use.
- Never paste or emit secrets.
- Enforce server-side authorization.
- Use parameterized queries.
- Validate redirects against an allow-list.
- Verify webhook signatures.
- Use route-specific rate limits.

## Git rules

- Do not create new repositories or forks.
- Work only in the current repository and branch unless explicitly told otherwise.
- Keep changes scoped to the task.
- Do not rewrite unrelated files.

## Verification rules

Never mark a task complete without at least one of:

- tests passing
- lint passing
- typecheck passing
- a concrete manual verification checklist

## Prompting posture

When asked to refactor:

- identify monolith boundaries
- propose target file tree
- move one concern at a time
- preserve behavior
- verify imports, types, and tests after each batch
