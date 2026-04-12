# Antigravity Review Rules

Applies to pull requests, refactors, and large code edits in this repository.

## Mission

Optimize for correctness, maintainability, performance, and security.
Do not optimize for surface-level churn.
Do not suggest broad rewrites unless the change materially improves architecture.

## Review priorities

Review in this order:

1. Correctness regressions
2. Security and authorization issues
3. Performance regressions
4. Architectural drift and maintainability
5. Style and minor cleanup

## Severity

- 🔴 Normal — should be fixed before merge
- 🟡 Nit — worth fixing, not blocking
- 🟣 Pre-existing — issue exists nearby but is not introduced by this PR

## Behavioral verification

Do not report a 🔴 Normal issue unless you can point to one of:

- a failing test
- a reproducible execution path
- a concrete security violation
- a deterministic reasoning chain tied to code paths and data flow

If a claim is uncertain, downgrade it or state uncertainty explicitly.

## Refactor rules

- Prefer splitting by concern, not by arbitrary line count.
- Prefer components under 150 lines.
- If a component exceeds that, inspect whether it mixes:
  - data fetching
  - stateful logic
  - sub-UI sections
  - reusable view patterns
- Extract stateful or business logic into hooks, services, or actions.
- Do not split files mechanically just to satisfy a threshold.
- Do not refactor large existing files unless:
  1. the task asks for refactoring, or
  2. there is a clear concern boundary and low migration risk.

## Frontend architecture

Use this hierarchy for UI work:

- atoms: smallest presentational primitives
- molecules: small compositions of atoms
- sections: larger reusable UI blocks
- features: route-level or domain-level assemblies
- hooks/services: non-visual behavior and business logic

Keep UI and behavior separate whenever that separation improves clarity.

## React and Next guidance

Prioritize the highest-impact fixes first:

1. eliminate async waterfalls
2. reduce client bundle size
3. reduce server-side waste
4. reduce unnecessary re-renders

Avoid spending review energy on micro-optimizations before fixing waterfalls or bundle bloat.

## Security guardrails

- Prefer managed auth over homegrown auth.
- Enforce server-side authorization for every protected action.
- Use short-lived access tokens and rotating refresh tokens.
- Validate and sanitize all inputs.
- Use parameterized queries.
- Lock down storage per tenant or per user.
- Verify webhook signatures.
- Rate-limit by route, user, and IP.
- Keep test and production environments separate.
- Never expose secrets in code, logs, prompts, or comments.

## What to skip

- purely stylistic nits if there is no team rule
- generated files unless they introduce a real issue
- formatting-only lockfile churn
- speculative findings without evidence

## Review output style

For each finding include:

- severity
- exact file or code region
- concise explanation
- why it matters
- the smallest sensible fix
