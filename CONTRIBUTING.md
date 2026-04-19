# Contributing to Monorepo-Uphillsnowball

## Before You Start

1. Read `AGENTS.md` — the canonical contract
2. Read `SECURITY.md` — responsible disclosure policy
3. Check `monorepo_manifest.yaml` — workspace truth

## Development Setup

### Prerequisites

- macOS (Apple Silicon recommended)
- Python 3.13+ (3.14.3 primary)
- Node.js 20+ (via nvm)
- .NET 11.0 Preview 2 (for Semantic Kernel)
- Google Cloud SDK (`gcloud`)
- Firebase CLI (`npx firebase-tools`)

### Clone

```bash
git clone git@github.com:ShadowTag-v2/Monorepo-Uphillsnowball.git
cd Monorepo-Uphillsnowball
```

### Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

This installs: Gitleaks, detect-private-key, Ruff, Bandit, YAML validation, trailing whitespace.

## Code Standards

### Python

- **Linter**: Ruff (0.11.8+)
- **Type checker**: basedpyright
- **Dead code**: Vulture (90%+ confidence)
- **Style**: Google Python Style Guide
- **Imports**: `ruff --fix` auto-sorts

### TypeScript

- **Style**: Google TypeScript Style Guide
- **Lint**: ESLint with strict config

### Shell

- **Style**: Google Shell Style Guide
- **Lint**: shellcheck

### All Languages

- Functions ≤ 500 LOC
- No duplicated logic — check for existing utilities first
- Every async operation needs loading + error states

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

feat(counselconduit): add Kovel attestation endpoint
fix(kovelai): resolve SSR hydration mismatch
harden(ci): add timeout-minutes to all workflows
docs(readme): update architecture diagram
```

Types: `feat`, `fix`, `harden`, `docs`, `refactor`, `test`, `chore`, `perf`, `ci`

## Pull Requests

1. Branch from `main`
2. Keep PRs focused — one concern per PR
3. Run locally before pushing:
   ```bash
   ruff check . --fix
   vulture . --min-confidence 90
   pytest
   ```
4. CI must pass (when Actions minutes are available)
5. PRs are auto-reviewed by GCA (Gemini Code Assist)

## Architecture Rules

### Immutable Zones

These files require explicit approval to modify:

- `AGENTS.md`, `GEMINI.md` — control plane
- `monorepo_manifest.yaml` — workspace truth
- `antigravity-mcp-config.json` — MCP truth
- `BUSINESS_CONTEXT_LOCKED.md` — pricing truth
- `RISK_REGISTER.md` — operational risk

### Product Split

| Product | Path | Runtime |
|---------|------|---------|
| KovelAI | `apps/kovelai/` | Firebase Hosting |
| CounselConduit | `apps/counselconduit/` | Cloud Run |
| AiYou Stack | `apps/aiyou_stack/` | Cloud Run |
| Uphillsnowball | `labs/uphillsnowball/` | Local only |

### Security

- No secrets in code, logs, or frontend
- All API routes authenticated by default
- Validate all inputs with Zod/Pydantic
- Use parameterized queries only
- See `SECURITY.md` for full policy

## Prohibited Patterns

- ❌ BullMQ (use Google Cloud Tasks)
- ❌ `rm -rf` or `sudo` in scripts
- ❌ Personal Access Tokens (use GitHub App)
- ❌ Docker Hub (migrating to Artifact Registry)
- ❌ Hardcoded API keys anywhere
- ❌ `npm audit fix --force` without review

## Getting Help

- Open an issue for bugs or feature requests
- Check existing KIs in `.gemini/antigravity/knowledge/`
- Reference the doctrine docs in `docs/doctrine/`
