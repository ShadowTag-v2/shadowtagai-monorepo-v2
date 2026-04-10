# AGENTS.md

## Scope

This is the ShadowTag-specific behavior contract.
It supplements, not replaces, linting, tests, CI, typed schemas, and policy code.

## Session start

1. Read `docs/Cor.Constitution.v3.md`.
2. Run the checks in `scripts/session_bootstrap.sh`.
3. Review `.agent/workflows/live-engine.md`.
4. Review `.agent/docs/toolbelt.md`.
5. Review `.agent/rules/shadowtag-laws.md`.
6. Confirm work is happening only inside the monorepo safe zone.

## Non-negotiables

- Work only inside the designated monorepo.
- Do not create new repositories or fork.
- Do not save work outside the monorepo unless explicitly instructed.
- Never output secrets, private keys, passwords, or tokens.
- Verify URLs and external claims before using them.
- Do not download or execute unverified binaries.
- Use the configured primary model unless explicitly instructed otherwise.
- Check memory/beads and git state before major actions when available.

## Product posture

- Build products that are simple enough for non-technical users to operate.
- Keep the UX extremely simple while keeping the internals powerful.
- Prefer revenue-positive, leverage-positive work.
- If a path multiplies complexity without multiplying revenue or strategic advantage, reject it.

## Response posture

- Think step by step.
- Explain the why before the action.
- Question assumptions.
- Reconcile contradictions before regenerating code.
- End with 3 to 5 concrete next-step options.
