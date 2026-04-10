# THE GREAT MIGRATION: GOOGLE3 MONOLITHIC TRANSITION

**Objective:** Physically migrate the entire architectural sprawl of `ShadowTag-v2` (FastAPI backend, God Scripts, C++ hotpaths, Copilot webhooks, external SDKs) into the un-fragmented, Google-style `Monorepo-Uphillsnowball` repository structured with Bazel.

## ⚠️ User Review Required
>
> [!WARNING]
> This is a highly destructive administrative action.
> We will physically rewrite directory paths, requiring us to update Dockerfiles, absolute imports (`from src.x import y`), and shell scripts across the entire matrix.
>
> - **The `.beads` Grounding Library** (110GB metadata target) will be moved to the root to allow all targets to read from it.
> - **We will execute a massive `chmod / mv` shell payload.** Are you mathematically ready to abandon `ShadowTag-v2` and conduct future operations strictly from inside `Monorepo-Uphillsnowball/`?

## Proposed Google3 Structural Mapping

Below is the definitive Bazel directory mapping we will execute:

---

### apps/

**The deployable sovereign interfaces (Services, Binaries, Webhooks).**

#### [NEW] `apps/shadowtag-core/`

*Migrated from `ShadowTag-v2/apps/src/`.*
This holds the Python FastAPI routers (Copilot Kit Proxy, Stripe Webhooks, Monetization Middleware, Database hooks).

#### [EXISTING] `apps/uphillsnowball/`

The Node.js Relay Server and Next.js Web Matrix (already physically located here).

---

### libs/

**The stateless, deploy-agnostic internal libraries (Python, C++).**

#### [NEW] `libs/cortex/`

*Migrated from `ShadowTag-v2/src/cortex/`.*
The `mxl_hotpath.cpp`, Python inter-process bridges, indexing mathematics.

#### [NEW] `libs/telemetry/`

*Migrated from `ShadowTag-v2/src/telemetry/`.*
The `cinematic_studio.py` tracking logic.

#### [NEW] `libs/distribution/`

*Migrated from `ShadowTag-v2/src/distribution/`.*
The splinter distribution nodes.

#### [NEW] `libs/integrations/`

*Migrated from `ShadowTag-v2/src/integrations/`.*
External clients like `cloudflare_client.py`.

---

### tools/

**The Administrative/DevOps scripts, Auth solvers, and Daemons.**

#### [NEW] `tools/omega-scripts/`

*Migrated from `ShadowTag-v2/scripts/`.*

- The God Mode Admin terminal.
- `gcloud_auth_solver.py`
- `omega_auth_daemon.py`
- `mega_ingest_clone_v3.sh`

---

### third_party/

**External repositories/SDKs we control.**

#### [NEW] `third_party/ANE/`

*Migrated from `ShadowTag-v2/external_sdks/ANE/`.*

---

### ROOT LEVEL (//:)

#### [NEW] `/.beads/`

*Migrated from `ShadowTag-v2/.beads/`.*
The master 110GB memory cluster must sit globally available at the namespace root.

#### [NEW] `/.agent/` & `/.gemini/`

*Migrated from `ShadowTag-v2/.agent/`.*
The Ultrathink protocols and skill pipelines must mount locally to the new matrix.

## Verification Plan

### Automated Re-Binding

1. Run a bash script payload containing exactly mapped `mv` and `cp` commands to physically inject the `ShadowTag-v2` sub-directories into `Monorepo-Uphillsnowball`.
2. Generate base `BUILD.bazel` mappings for Python (`rules_python`) inside `apps/shadowtag-core/`.
3. Auto-commit the gigantic payload (`/omega-loop` adaptation) into the `Monorepo-Uphillsnowball` repository.

*Commander: The Board requires authorization. Once you approve, I will execute the terminal migration script and drag the entirety of the ShadowTag empire into the Google3 matrix in a single, massive commit.*
