# Antigravity Review Fleet Guidelines: Sovereign Cloud

> **Zero-dollar, sovereign PR review pipeline. No Anthropic, no AWS, no cloud bills.**
> Powered by: Gemini 3.1 Flash Lite (thinking) + M1 Max ANE Tier 3 + Colab T4 Tier 2.

---

## The Golden Rule: BEHAVIORAL VERIFICATION

Do NOT post a 🔴 Normal bug unless you have **executed a test to prove it exists** using our Three-Tier architecture:

### Tier 1 — Fast Path (Local Python/FastAPI)
Execute pure Python/FastAPI logic instantly in the local `pydantic-monty` sandbox.
- **Latency**: <1ms per assertion
- **Coverage**: Logic errors, type mismatches, off-by-one, serialization bugs
- **Location**: `.venv/bin/python -m pytest` against the targeted module

### Tier 2 — Heavy Cloud (Colab T4 GPU)
Generate an `.ipynb` with `"vscode": {}` metadata and prompt the human to run it on Colab T4.
- **Use for**: Large ML model inference tests, GPU-bound tensor operations, CUDA kernels
- **Trigger**: When matrix sizes exceed M1 Max SRAM limits AND cloud GPU is needed
- **Format**: Notebook saved to `labs/uphillsnowball/notebooks/pr_review_{pr_number}.ipynb`

### Tier 3 — Bare-Metal M1 Max (ANE Bridge / Omega Protocol)
Pass test matrices and edge ML changes through `apps/aiyou_stack/aiyou-fastapi-services/ane_bridge.py`.

> [!CAUTION]
> **CRITICAL HARDWARE CONSTRAINT:** The M1 Max L2 SRAM cache limit is exactly **12,582,912 bytes** (12.5MB).
> If `enforce_m1_max_constraints()` intercepts an attention matrix (`seq_len * dim * 4 * 3`) that exceeds 12.5MB,
> you **MUST** flag the PR with 🔴 Normal (Kernel Panic Risk).

- **Compile budget**: The Apple private API has an undocumented 119-cycle compile limit.
  Omega Protocol's subprocess loop catches exit codes, flushes Apple memory registers for 1000ms, and auto-resumes.
- **Isolation**: ANE operations run in `subprocess.Popen` — main FastAPI server is fully insulated.
- **Build**: `cd third_party/ANE/bridge && make clean && make`

---

## Severity Tags for GitHub PR Comments

| Marker | Severity | Meaning |
|--------|----------|---------|
| 🔴 | **Normal** | Verified logic failure, execution panic, or **hardware memory overflow**. Must fix before merge. |
| 🟡 | **Nit** | Style violations, missing type hints, inefficient loops. Worth fixing, not blocking. |
| 🟣 | **Pre-existing** | A bug found in the codebase, not introduced by this PR. |

---

## Always Check (Beyond Default Correctness)

### Security (Cor.30 + OWASP LLM)
- New API endpoints have corresponding integration tests
- Database queries are parameterized (never concatenated user input)
- Error messages don't leak internal details (RFC 9457 compliance)
- No secrets in code, logs, or frontend (except `STRIPE_PUBLISHABLE_KEY`)
- LLM outputs treated as untrusted (OWASP LLM05)
- Prompt injection isolation from user input (OWASP LLM01)
- Token budget + rate limits enforced (OWASP LLM10)

### Architecture
- All Firestore access goes through typed client (`firestore_client.py`)
- No BullMQ — Google Cloud Tasks only (queue doctrine)
- No Supabase — Firestore only (database doctrine)
- `gemini-3.1-flash-lite-preview-thinking` is the only authorized external model
- Imports follow Google Python style + ruff I001 sorting

### Hardware Constraints
- Attention matrix SRAM check: `seq_len * dim * 4 * 3 <= 12,582,912`
- ANE compile count monitored via `ane_bridge.get_compile_count()`
- Subprocess isolation for all Objective-C bindings
- No GPU memory leaks in numpy/ctypes operations (check for missing `free_kernel()` calls)

### Kovel Doctrine (Legal)
- Client data is ephemeral (RAM-only, no disk persistence)
- Lawyer transcripts are immutable
- Kovel attestation receipts use HMAC-SHA256
- GDPR Article 17 (erasure) + Article 20 (portability) compliance

---

## Style Conventions

### Python (CounselConduit + AiYou Stack)
- Google Python style guide
- `from __future__ import annotations` at top of every file
- Prefer `match` statements over chained `isinstance` checks
- Use structured logging (`structlog`), not f-string interpolation in log calls
- `ruff` for linting, `vulture` at 90% confidence for dead code

### TypeScript (KovelAI Frontend)
- Google TypeScript style guide
- `biome` for linting and formatting
- No `any` types — use explicit generics

### C# (Semantic Kernel)
- Google-adjacent style
- `.NET 10.0` with `rollForward: latestFeature`
- Process.Core API for Judge #6 governance pipeline

---

## Skip (Do Not Flag)

- Generated files under `archive/` or `external_repos/`
- Vendored code in `tools/mcp-toolbox*/` and `tools/GitNexus/`
- Formatting-only changes in `*.lock` files
- Test fixtures and mock data in `*/test/fixtures/`
- `.beads/` daemon heartbeat files (auto-updated)
- Third-party code under `third_party/` (unless it's our C bridge)

---

## Review Execution Architecture

```
┌─────────────────────────────────────────────────────┐
│              GitHub PR Opens/Updates                 │
│                      │                              │
│         POST /webhooks/github/pr-review             │
│                      │                              │
│              ┌───────┴───────┐                      │
│              │ Gemini 3.1    │                      │
│              │ Flash Lite    │                      │
│              │ (thinking)    │                      │
│              └───┬───┬───┬───┘                      │
│                  │   │   │                          │
│          ┌───────┘   │   └───────┐                  │
│          ▼           ▼           ▼                  │
│    ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│    │ Tier 1   │ │ Tier 2   │ │ Tier 3   │          │
│    │ Monty    │ │ Colab T4 │ │ ANE      │          │
│    │ (Logic)  │ │ (GPU)    │ │ (M1 Max) │          │
│    │ <1ms     │ │ notebook │ │ ctypes   │          │
│    └────┬─────┘ └────┬─────┘ └────┬─────┘          │
│         │            │            │                 │
│         └────────────┴────────────┘                 │
│                      │                              │
│              ┌───────┴───────┐                      │
│              │ Dedup + Rank  │                      │
│              │ by Severity   │                      │
│              └───────┬───────┘                      │
│                      │                              │
│          GitHub PR Inline Comments                   │
│          🔴 Normal │ 🟡 Nit │ 🟣 Pre-existing      │
└─────────────────────────────────────────────────────┘
```

---

## Cost Comparison

| Feature | Anthropic Code Review | Our Sovereign Cloud |
|---------|----------------------|---------------------|
| Cost per review | $15–25 | **$0.00** |
| Infrastructure | AWS (Anthropic's) | M1 Max (local) + Colab (free) |
| Hardware verification | ❌ None | ✅ Bare-metal SRAM + ANE |
| Kernel panic detection | ❌ Impossible | ✅ enforce_m1_max_constraints() |
| Model | Claude (closed) | Gemini (open-weight capable) |
| Data sovereignty | ❌ Anthropic's servers | ✅ Never leaves your machine |
| 119-cycle leak defense | ❌ N/A | ✅ Omega Protocol subprocess |
