# Antigravity Review Fleet Guidelines: Sovereign Cloud (REPO_OS v15.0)

## Golden Rule: BEHAVIORAL VERIFICATION

Do **NOT** post a 🔴 Normal bug unless you have **physically executed** a test to prove it exists using our Three-Tier architecture.

### Tier Routing Logic

1. **Tier 1 (Fast Path)**: Pure Python/FastAPI logic → local pytest sandbox (<1ms)
2. **Tier 3 (Bare-Metal M1 Max)**: Tensors / ML / ANE logic → `ane_bridge.py`
   - **CRITICAL**: M1 Max L2 SRAM limit = **12,582,912 bytes**
   - If `enforce_m1_max_constraints()` detects overflow → flag as 🔴 Normal (Kernel Panic Risk)
3. **Tier 2 (Heavy Cloud)**: Anything too large for ANE → Generate `.ipynb` → route to Colab T4 via Google Drive IPC

## Severity Tags

- 🔴 **Normal**: Verified logic failure, execution panic, or hardware memory overflow
- 🟡 **Nit**: Style violations, missing type hints, inefficient loops
- 🟣 **Pre-existing**: Bug that existed before this PR

## Always Check

- New API endpoints have corresponding integration tests
- Database migrations are backward-compatible
- Error messages don't leak internal details to users
- Stripe webhook handlers verify signatures before processing
- All new Python files pass `ruff check --select F401,F841`
- Pydantic models use strict typing (no `Any` without justification)
- No Python file exceeds 400 lines
- Zero unused imports (enforced by Ruff)
- Firestore security rules updated when schema changes

## Style

- Prefer `match` statements over chained `isinstance` checks
- Use structured logging, not f-string interpolation in log calls
- Prefer early returns over nested conditionals
- Use `httpx` for async HTTP, `requests` for sync-only scripts

## Skip

- Generated files under `external_repos/`
- Archived files under `archive/` and `_archive*/`
- Formatting-only changes in `*.lock` files
- Files in `.venv/` and `node_modules/`
- Third-party vendored code under `third_party/`

## Hardware Constraints (M1 Max Enforcement)

Any PR that modifies tensor operations, model loading, or ANE dispatch must pass through the
hardware verification tier:

```
max_ane_payload = 12_582_912  # bytes (M1 Max L2 SRAM)
attention_cost = seq_len * dim * 4 * 3  # float32 × QKV
if attention_cost > max_ane_payload:
    # Flag as 🔴 Normal — Kernel Panic Risk
    # ANE will fall back to main memory and panic the OS
```
