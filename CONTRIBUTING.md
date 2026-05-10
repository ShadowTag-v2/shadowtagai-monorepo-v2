# Contributing to ShadowTag Monorepo

## Prerequisites
- Python 3.14+ (`/opt/homebrew/bin/python3.14`)
- Node.js 24+ with npm
- Go 1.24+ (for Gideon OS Go blocks)
- Rust/Cargo (for Tauri cockpit)
- .NET 10.0+ (for AiYou Kernel)
- Google Cloud SDK (`gcloud`)
- Firebase CLI v15+ (installed globally, not via npx)

## Development Setup

```bash
# Clone
git clone git@github.com:ShadowTag-v2/Monorepo-Uphillsnowball.git
cd Monorepo-Uphillsnowball

# Python deps
/opt/homebrew/bin/python3.14 -m pip install -r requirements.txt

# MCP secrets (requires GCP auth)
source scripts/load_mcp_secrets.sh

# Run tests
/opt/homebrew/bin/python3.14 -m pytest
```

## Architecture

| Component | Path | Language | Owner |
|-----------|------|----------|-------|
| CounselConduit | `apps/counselconduit/` | Python | pnkln-backend |
| KovelAI | `apps/kovelai/` | TypeScript | pnkln-frontend |
| AiYou Kernel | `apps/aiyou-kernel/` | C# | pnkln-backend |
| Gideon OS | `labs/uphillsnowball/gideon-os/` | Multi | pnkln-architecture |

## Gideon OS Development

Gideon OS spans 7 languages across 14 blocks. See `labs/uphillsnowball/EXECUTION_BRIEF_OMNI_SWEEP.md` for the full architecture.

### Block-Specific Commands

| Block | Build | Test |
|-------|-------|------|
| Python | `ruff check --fix` | `pytest` |
| Go (Shield1) | `go build ./cmd/gideon-go/...` | `go test ./...` |
| Rust (Tauri) | `cargo build` | `cargo test` |
| C++ (Midas) | `gcloud builds submit` | Manual |
| TypeScript | `npx @biomejs/biome check` | `jest` |
| Terraform | `terraform plan` | `terraform validate` |

## Security Requirements (Cor.30)

All contributions MUST comply with the Cor.30 security framework:
1. No secrets in code — use GCP Secret Manager
2. All inputs validated with Pydantic (Python) or Zod (TypeScript)
3. Errors via RFC 9457 — never expose stack traces
4. IPI quarantine maintained — no raw external data in agent context

## Commit Convention

Use Conventional Commits:
```
feat(gideon-os): add shield1 ingress Go service
fix(counselconduit): resolve magic link token expiry
chore(ci): update ruff to v0.15.11
```

## PR Process

1. Create branch from `main`
2. Use the Gideon OS PR template if touching `labs/uphillsnowball/`
3. All tests must pass (499+ pytest, 0 .NET errors)
4. Gitleaks pre-commit must pass
5. Ruff + Biome lint must be clean
