# Stage 3 Repo-Drift Audit Report

## 1. Stale Naming Drift (`pnkln` / `pnkln` -> `pnkln`)
- **Status:** **HEAVILY DRIFTED**
- **Findings:** Discovered **2,834** files containing deprecated legacy naming prefixes.
- **Context:** Large portions of the drift are centralized in the `apps/pnkln_stack` architecture and legacy markdown documentation imported during the monorepo merge.

## 2. Stale Model Drift (`gemini-3.1-family`, `gemini-3.1-family` vs `gemini-3.1-family`)
- **Status:** **DRIFTED**
- **Findings:** Discovered **612** files containing hardcoded legacy model definitions (`gemini-3.1-family`, `gemini-3.1-family`, etc.).
- **Context:** Violates the single model policy (`gemini-3.1-family` configuration surface). Hardcoded model definitions in edge layers must be swapped to dynamic references against the canonical truth.

## 3. Duplicate Roots & Alternate Control Planes
- **Status:** **DRIFTED**
- **Findings:** 
  - Found **44** total `.code-workspace` files.
  - Crucially, `Monorepo-Uphillsnowball.code-workspace` is actively competing with the canonical `pnkln.code-workspace` at the repository root.
  - 42 nested `.code-workspace` definitions discovered inside `libs/`, `reference/`, and `apps/` creating parallel operator entrypoints.

## 4. Surviving Runtime Pack Operationalization
- **Next Steps:** The core surviving runtime pack requires active wiring:
  - `green_loop.py`
  - `drive_ingest_daemon.py`
  - `retriever_eval.py`
  - `ocr_summary_ingest.py`
  - `csp_collector`
  - `feature_flags`
  - pricing & valuation wiring

## Final Verdict
**DRIFT DETECTED IN ALL CATEGORIES.** The codebase is currently running in a highly fragmented state. A series of aggressive, programmatic find-and-replace sweeps and file deletion protocol implementations are strictly required before Stage 4 Hardening can commence.
