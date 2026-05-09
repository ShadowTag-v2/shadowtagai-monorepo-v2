# Contributing to shadowtagai-monorepo-v2

Thank you for your interest in contributing to the AGNT_OS monorepo.

## Getting Started

```bash
git clone git@github.com:ShadowTag-v2/shadowtagai-monorepo-v2.git
cd shadowtagai-monorepo-v2

# Install tools
mise install

# Clone all reference repositories (22 groups)
./scripts/clone-external-reference-repos.sh

# Run full health check
python scripts/repo_doctor.py
```

## Development Workflow

1. **Create a feature branch** from `main`
2. **Make your changes** following the coding standards below
3. **Run linting** before committing: `pre-commit run --all-files`
4. **Open a PR** targeting `main`
5. **Wait for CI** to pass and get at least one review

## Coding Standards

- **Python**: `ruff` for linting + formatting. No vulture, no flake8.
- **TypeScript/JS**: `biome` for linting + formatting. No ESLint/Prettier.
- **Bazel**: `buildifier` for BUILD file formatting.
- **Shell**: `shellcheck` for all `.sh` scripts.
- **No file should exceed ~400 lines** — split into focused modules.

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(counselconduit): add webhook retry logic
fix(agent): resolve memory leak in orchestrator
docs: update migration plan with Phase 3 details
chore: bump ruff to 0.9.x
```

## Architecture Decisions

All significant architecture decisions must be documented in `docs/decision-log.md`.

## Security

- Never commit secrets or API keys
- All secrets go through GCP Secret Manager
- Run `betterleaks` + `trufflehog` before every push
- See `docs/RISK_REGISTER.md` for known risks

## Questions?

Open an issue or reach out to the Platform Team.
