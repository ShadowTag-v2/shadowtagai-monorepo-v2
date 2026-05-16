# AGENTS.md

Canonical root: this repository only.

Operate in strict workspace mode.
- Work only inside the canonical repo root.
- Refuse to create nested repos, shadow workspaces, duplicate clones, or sidecar project trees.
- Prefer edits to existing files over new files unless a new file is clearly required.

Decision stack:
- Purpose: pnklnJR
- Reasons: verified doctrine
- Brakes: army-style risk management

Execution rules:
- Act, then report. Do not ask for routine confirmation.
- Raise objections when a request violates security, repo boundaries, architecture, or rollback safety.
- State assumptions briefly, make the safest reasonable choice, and continue.
- Keep diffs small, reversible, and reviewable.
- Every change must include tests or an explicit reason no test is possible.
- Never claim success without fresh evidence from the workspace.

Code and architecture:
- Use Atomic Design only for design-system primitives.
- Organize product code by feature and concern: features, hooks, services, policies, validation, routes, jobs.
- Prefer components under 150 lines and functions under 60 lines; split by responsibility, not by numerology.
- Extract stateful or business logic out of UI into hooks, services, or policy layers.
- Use Vercel React doctrine for frontend performance: remove async waterfalls first, then bundle size, then server/client rendering issues.

Security defaults:
- No custom auth when a managed provider is available.
- Short-lived access tokens, rotated refresh tokens, server-side authorization, strict input validation, structured logging, secret scanning, and environment separation are mandatory.
- Never expose secrets, tokens, keys, or raw credentials in output.

Antigravity posture:
- Treat this repo as the only workspace.
- Produce artifacts under `artifacts/` for major runs.
- Keep plans, PR notes, and audit outputs terse and machine-readable.
