# pnkln Vibe Coding Rules

## Executive summary
This package gives coding agents a lean behavior contract plus stronger automation.
The repo instructions stay minimal; the real enforcement lives in hooks, linting, tests, and CI.

## What to build in
### Include directly
- Lean `AGENTS.md`
- `.cursor/rules/vibe-coding.mdc`
- `.pre-commit-config.yaml`
- secret scanning
- linting, formatting, type checks, tests
- frontend performance order based on Vercel’s framework
- refined security defaults
- feature-and-concern architecture
- Atomic Design only for the design-system layer

### Include as optional integrations
- `vercel-labs/agent-skills`
- `REPOZY/superpowers-optimized`

These are optional skill packs, not mandatory runtime dependencies or a second control plane.

## Architecture
Use Atomic Design only for primitives and small composed UI patterns.
Do not impose it on the whole application.
The rest of the codebase should be organized by feature and concern:
- feature modules
- hooks
- services
- policies
- validation
- permissions
- route handlers / server actions

## Size policy
- Functions: ideal under 50 lines, review above 50.
- Hooks: ideal under 80 lines, review above 100.
- Components: ideal under 120 lines, review above 150, mandatory refactor review above 300.
- Route handlers: keep thin; move business logic out.
- Services: group coherent responsibilities, not random utilities.

## Security defaults
- Managed auth only for production.
- Access tokens short-lived; refresh tokens rotated and revocable.
- Password reset and recovery flows hardened against enumeration and abuse.
- Input validation at every boundary.
- Authorization enforced server-side.
- Upload validation by allow-list, size, signature/content, and safe storage policy.
- Structured security logging; no secret or PII leakage.
- Rate limits by IP, user, and route where appropriate.
- Security headers by default.
- CSRF protection when cookies are used.
- Secret scanning in pre-commit and CI.
- Lockfile discipline and reviewed dependency remediation.
- Backups plus restoration testing.
- Test/prod separation.

## React / Next.js doctrine
Default order:
1. Kill async waterfalls.
2. Reduce shipped JS.
3. Improve server-side performance.
4. Fix client-side fetching.
5. Reduce re-renders.
6. Improve rendering behavior.
7. Only then chase advanced micro-optimizations.
