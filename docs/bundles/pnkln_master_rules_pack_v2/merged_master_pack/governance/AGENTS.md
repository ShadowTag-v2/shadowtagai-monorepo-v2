# AGENTS.md

## Scope

This file is the minimal behavior contract for coding agents in this repo.
Anything enforceable by linting, tests, CI, schemas, or policy code belongs there instead of here.

## Priorities

1. Security over convenience.
2. Correctness over cleverness.
3. Simplicity over sprawl.
4. Natural boundaries over arbitrary fragmentation.
5. Managed critical infrastructure over DIY auth or crypto.
6. Minimal repo instructions, stronger automation.

## Architecture

- Use Atomic Design only for the design-system layer.
- Organize the rest of the app by feature and concern: features, hooks, services, policies, validation, permissions, route handlers, server actions.
- Prefer components under 150 lines, but split by responsibility, not by line count alone.
- Prefer functions under 50 lines when practical.
- Extract stateful or business logic into hooks or services.
- Do not create wrapper files with no real boundary.

## React / Next.js performance order

1. Eliminate async waterfalls.
2. Reduce bundle size.
3. Improve server-side performance.
4. Fix client-side data fetching.
5. Reduce unnecessary re-renders.
6. Improve rendering performance.
7. Only then optimize advanced patterns and JS details.

## Security

- Never build custom auth for production. Use a managed provider.
- Use short-lived access tokens and rotated, revocable refresh tokens.
- Validate all inputs with typed schemas.
- Enforce authorization server-side.
- Use strict CORS, security headers, and CSRF protection where cookies are used.
- Validate uploads by allow-list, size, and content/signature, not extension alone.
- No secrets in code, logs, comments, fixtures, or commits.
- Structured security logging only; no secret or PII leakage.
- Backups are required and restoration must be tested.

## Agent behavior

- Prefer deterministic fixes over broad rewrites.
- Prefer existing project patterns unless they are clearly inferior.
- Before adding dependencies, verify the package exists and is maintained.
- When uncertain, state the assumption and choose the smallest safe path.
- If a rule must be broken, add a short `SEC-DEBT:` comment and explain why in the PR.

## Optional external skills

- Vercel React best practices may be used as the default frontend performance doctrine.
- Extra skills or prompt packs are optional amplifiers, not a second control plane.
