# pnkln Workspace Rules (README_WORKSPACE.md)

This document is the plain English architectural ledger for Antigravity, defining exactly what is live, what is quarantined, and the separation between product and lab.

## The Root Guard
You must execute `scripts/pnkln_root_guard.sh` before performing any repository-wide action. If the guard fails, stop immediately. Do not create, move, or edit files.

## The Active Domains (Live)
There are only three active domains in this repository for development. All code you write must land in one of these three roots:

1. **Product (`apps/counselconduit`)**
   - **Environment:** Google Cloud Native (Cloud Run, Firebase, Vertex AI).
   - **Purpose:** Production-grade commercial MVP for the liability shield product.
   - **Rules:** Code here must be highly performant, type-checked, and scrubbed of any experimental Apple Silicon local-only dependencies.

2. **Lab (`labs/uphillsnowball`)**
   - **Environment:** Local Apple Silicon (Mac Studio/M-series).
   - **Purpose:** Fast prototyping, R&D, and local memory engines using LanceDB / MLX.
   - **Rules:** You may experiment freely here. However, experimental code must NEVER bleed into `counselconduit` until formalized and promoted.

3. **Shared Interop (`shared/`)**
   - **Environment:** Agnostic.
   - **Purpose:** The bridge layer between the Lab and the Product.
   - **Rules:** Use `shared/artifacts/` to export scrubbed fixtures and traces from the Product, and replay them in the Lab.

## The Quarantine Zones (Dead / Excluded)
The following zones contain legacy drift, recovered archives, or unstructured data. **You are strictly forbidden from executing code, editing files, or using these directories as a source of truth:**

- `archive/` (all backups and legacy repos)
- `external_memory/` and `repos/`
- Anything containing `*legacy*`
- Nested pnkln-stack-fastapi-services legacy ingest folders (`raw_ingest`, `drive_ingest`, `external_repos`, etc.)

If you find yourself reading from or configuring tools against the quarantine zones, stop immediately and reset your context.
