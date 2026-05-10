# Antigravity Review Fleet Guidelines: Sovereign Cloud (REPO_OS v15.0)

## Golden Rule: BEHAVIORAL VERIFICATION
Do **NOT** post a 🔴 Normal bug unless you have **physically executed** a test to prove it exists.

### Tier Routing Logic
1. **Tier 1 (Fast Path)**: Pure Python/FastAPI logic → `pydantic-monty` sandbox
2. **Tier 3 (Bare-Metal M1 Max)**: Tensors / ML / ANE logic → `ane_bridge.py`
   - **CRITICAL**: M1 Max L2 SRAM limit = **12,582,912 bytes**
3. **Tier 2 (Heavy Cloud)**: Anything too large → Route to Colab T4 via Google Drive IPC

## Severity Tags
- 🔴 **Normal**: Verified logic failure, execution panic, or hardware memory overflow
- 🟡 **Nit**: Style violations, missing type hints, inefficient loops
- 🟣 **Pre-existing**: Bug that existed before this PR

## Review Rules

### 1. Security First
- Never approve PRs that hardcode secrets (use GCP Secret Manager)
- Validate all `firebase.ts` changes against App Check rules
- Verify `.gitleaksignore` additions are legitimate false positives

### 2. Architecture Compliance
- All queue operations MUST use Google Cloud Tasks (BullMQ banned)
- All Python linting via `ruff` only (vulture/flake8 banned)
- All JS/TS linting via `biome` only (eslint/prettier banned)
- `.env` files are BANNED — use `scripts/load_mcp_secrets.sh`

### 3. Test Coverage
- New features require accompanying tests
- Breaking changes require migration documentation
- Performance-sensitive paths require bench_ms comparison

### 4. AST Surgery Auto-Fix
After review, the following auto-fixes are applied:
- `ruff check --fix` + `ruff format` (Python)
- `biome check --write` (TypeScript/JavaScript)
- `ast-grep` pattern rewrites (dynamic import migration)

## Swarm Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Jules      │────▶│    GCA      │────▶│  AST Surgery │
│ Orchestrator │     │ Multi-Agent │     │  Auto-Fix    │
└──────┬───────┘     └──────┬──────┘     └──────────────┘
       │                    │
       ▼                    ▼
┌─────────────┐     ┌─────────────┐
│ ANE Bridge  │     │ Colab T4    │
│ Tier 3      │     │ Tier 2      │
│ (M1 Max)    │     │ (Fallback)  │
└─────────────┘     └─────────────┘
```
