# THE GREAT MIGRATION: Thread Mining Report
**Status:** DRAFTED (Awaiting Board Approval)
**Target:** `ShadowTag-v2` -> `Monorepo-Uphillsnowball`

## A1. Existing Code Found (Target Assets for Extraction)
* **God Mode Admin**: `ShadowTag-v2/scripts/god_mode_admin.py` (Purpose: Interactive admin loop, auto-sync, jobs. Destined for `tools/omega-scripts/`)
* **Auth Solvers**: `ShadowTag-v2/scripts/gcloud_auth_solver.py`, `omega_auth_daemon.py` (Purpose: GCP/Service Account token refreshing. Destined for `tools/omega-scripts/`)
* **FastAPI Backend Core**: `ShadowTag-v2/apps/src/` (Purpose: Stripe hooks, Copilot proxy. Destined for `apps/shadowtag-core/`)
* **Cortex / Hotpaths**: `ShadowTag-v2/src/cortex/mxl_hotpath.cpp` (Purpose: C++ ML routing. Destined for `libs/cortex/`)
* **Telemetry**: `ShadowTag-v2/src/telemetry/cinematic_studio.py` (Purpose: Logic tracking. Destined for `libs/telemetry/`)
* **Distribution nodes**: `ShadowTag-v2/src/distribution/` (Destined for `libs/distribution/`)
* **Integrations**: `ShadowTag-v2/src/integrations/cloudflare_client.py` (Destined for `libs/integrations/`)
* **Apple Neural Engine (ANE) SDK**: `ShadowTag-v2/external_sdks/ANE/` (Destined for `third_party/ANE/`)
* **The Grounding Library**: `ShadowTag-v2/.beads/` (110GB metadata target. Destined for `/.beads/` at root)
* **Agent Context**: `ShadowTag-v2/.agent/` & `ShadowTag-v2/.gemini/` (Destined for `/.agent/` & `/.gemini/` at root)

## A2. Missing / Implied Code (To Be Built/Linked Post-Migration)
* **`BUILD.bazel` Mappings**: The physical code will move, but Bazel requires `BUILD.bazel` files in `apps/shadowtag-core/`, `libs/cortex/`, etc., to compile the Python and C++ rules correctly so they don't break on `bazel test //...`.
* **CI/CD Hygiene**: The user provided a PRISM setup (`Makefile` bootstrap loop, `.pre-commit-config.yaml`). This must be laid over the monorepo root to guarantee local vs. CI parity.
* **Namespace Refactoring**: When we move `ShadowTag-v2/apps/src/api/...` to `Monorepo/apps/shadowtag-core/...`, every internal absolute import `from src.api...` will catastrophically break. A recursive AST regex sweep must rewrite the imports to `from apps.shadowtag_core...`
* **Docker Contexts**: Dockerfiles building `ShadowTag-v2/apps/` will lose their `COPY` paths. Path contexts must be bumped to the monorepo root.

## A3. Unaddressed Suggestions / Optionals
* **God Mode AsyncPG Dependency**: "It currently warns asyncpg is missing; install for full capability: pip install asyncpg." -> **Decision**: Inject `asyncpg` into the new `pyproject.toml` or `requirements.txt` environment bootstrapping.
* **Auto-Format Hooks**: "Would you like me to layer in auto-format (black/isort) hooks and a lint-before-commit rule next?" -> **Decision**: We will enforce Biome & Ruff universally via the `.pre-commit-config.yaml` to enforce the Pinkln Doctrine locally.

## A4. Conflicts & Unknowns
* **110GB .beads Library**: Moving 110GB via `git mv` or standard shell `mv` could take immense I/O time or crash standard terminal buffers. **Assumption**: We will use a symlink for the 110GB directory initially or a raw filesystem block-move (`mv` on same APFS volume is instant), avoiding a 110GB `git add` unless explicitly requested, as GitHub blocks files > 100MB and repos over 2GB.
* **Database State**: `transcript_to_contract.py` runs with an in-memory DB. This state will wipe on process kill.

---

# IMPLEMENTATION PLAN -> PR BATCH

**PR-001: The Makefile Bootstrap & Git Hook CI Pipeline**
* **Files**: `Makefile`, `.pre-commit-config.yaml`, `pyproject.toml` (or equivalent dev deps).
* **Summary**: Injects the PRISM CI stack at the Monorepo root to protect the branch *before* the massive code ingestion begins. Includes Ruff & Biome configurations.

**PR-002: Infrastructure & Tools Migration (`tools/` & `third_party/`)**
* **Files**: `tools/omega-scripts/god_mode_admin.py`, `tools/omega-scripts/gcloud_auth_solver.py`, `third_party/ANE/`.
* **Summary**: Physically moves and commits the administrative control loop and ANE SDKs to the new Monorepo topology. Upgrades dependencies (`asyncpg`) and maps paths.

**PR-003: Core Libraries Extraction (`libs/`)**
* **Files**: `libs/cortex/`, `libs/telemetry/`, `libs/integrations/`.
* **Summary**: Moves the stateless C++ and Python engines. Updates local include headers and creates base `BUILD.bazel` files for Bazel graph recognition.

**PR-004: FastAPI Application Layer & `.beads` Attachment (`apps/`)**
* **Files**: `apps/shadowtag-core/`, application Dockerfiles, `/.beads/` symlinking.
* **Summary**: The heaviest lift. Moves the API routers, systematically runs an AST script to rewrite `from src...` import paths to `from apps.shadowtag_core...`, and fixes containerization relative paths.
