# REVIEW.md

## Review posture

Optimize for correctness, maintainability, bounded scope, and commercial leverage.

Prefer:
- one source of truth per layer
- small, reviewable diffs
- split by concern, not arbitrary line count
- explicit tests for new behavior
- documentation updates when control-plane or runtime truth changes

## Always check

- Any new API route has tests.
- Any path move includes import/script/runtime verification.
- Any config change removes stale model IDs and stale project IDs.
- Any retention-sensitive feature avoids persistent logging by default.
- Any migration step has a dry-run path and rollback path.
- Any generated BUILD files are minimal and readable.

## Monolith / refactor rules

- Prefer components under 150 lines.
- If a component exceeds this, evaluate whether it contains distinct concerns:
  - data fetching
  - sub-UI sections
  - reusable logic
- Extract stateful logic into custom hooks.
- Never split purely to hit a line count.
- Never refactor large existing files unprompted in unrelated PRs.

## Security / execution rules

- No real secrets in repo.
- No fallback dev secrets in production paths.
- No wildcard CORS in production config.
- No test webhooks touching real systems.
- No new repo creation or forking from agent workflows.
- No destructive migration without snapshot + verify + rollback.

## Skip / deprioritize

- Formatting-only commentary in generated files
- speculative architectural rewrites outside PR scope
- reviving superseded thread artifacts once canonical files exist

## Severity

- 🔴 Normal: verified correctness, security, migration, or runtime issue
- 🟡 Nit: maintainability, clarity, minor hygiene issue
- 🟣 Pre-existing: issue not introduced by this PR
