# Omni-Sweep Transfer & Repository Consolidation

This plan tackles the strategic architecture dictated by the Omni-Sweep Thread Transfer Protocol. The core problem is the GitHub 500 error caused by attempting to push a raw 7.09 GiB monolithic commit of 120+ vendored SDKs. The objective is to deploy the ingestion and vendoring daemons while stabilizing the origin repository and maintaining the "Sovereign OS" standard.

## User Review Required

> [!CAUTION]
> **The 7GB Monorepo Bloat Error (The Board's Verdict)**
>
> Commander, pushing a 7GB monolithic `vendored_clones/` folder full of C++, Rust, and Deno binaries stripped of their `.git` folders to GitHub natively will violently break Git's delta compression and RPC limits. Even if we use an SSH remote, a single blob of 161,000 objects totaling 7GB will continuously hit GitHub's ingest buffers, and any future `git clone` by a pipeline will take massive amounts of time, destroying our deployment velocity.
>
> **Steve Jobs Mode Recommendation (IQ 160 Lock):** We must ADD `vendored_clones/` to our `.gitignore`. We deploy the `mass_sdk_vendoring.py` engine so the *local* Antigravity workspace dynamically fetches the code and shreds the fragmented submodules at runtime (assimilating them on disk). The brain remains centralized in your workspace, but we don't stuff 7GB of Chromium/Deno trash into our canonical Git repository tracking.
>
> If you **demand** it be physically pushed to GitHub despite the bloat, we must implement an aggressive chunked SSH push script, breaking the push into 500MB waves. Please advise on this verdict.

> [!IMPORTANT]
> **Missing Intel: The Target URLs**
> The `scripts/mass_sdk_vendoring.py` and `scripts/ingest_internet_doctrines.py` skeletons passed from the previous thread do not contain the actual lists of the 120+ SDKs or the 30+ Military/Cloud doctrines. I need those URLs to finalize the operational scripts. Can you provide them, or should I extrapolate the core Google/Cloud/Rust/Deno architectures?

## Proposed Changes

### Configuration

Update the local git configuration to use SSH, bypassing HTTPS memory buffers.

#### [NEW] `git remote set-url origin git@github.com:ShadowTag-v2/ShadowTag-v2-fastapi-services.git`

### Operational Scripts

Create the Mass Acquisition Matrix and Doctrine Ingestion Daemons based on the previous thread's blueprint, utilizing `gemini-3.1-flash-lite-preview`.

#### [NEW] [scripts/mass_sdk_vendoring.py](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/scripts/mass_sdk_vendoring.py)

Creates the concurrent cloner for assimilation of native source code (`--depth 1` and `rm -rf .git`).

#### [NEW] [scripts/ingest_internet_doctrines.py](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/scripts/ingest_internet_doctrines.py)

Creates the `gemini-3.1-flash-lite-preview` powered asynchronous document extractor.

#### [MODIFY] [.gitignore](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/.gitignore)

Appends `vendored_clones/` to shelter the remote repository from massive binary blobs (Pending Commander Approval).

## Verification Plan

### Automated Tests

1. **Env Verification:** Execute `/live-engine` and `/omega-loop` (`scripts/finish_changes.py`) to mandate CodePMCS scans and Gate 0 compliance on the new Python scripts.
2. **Push Test:** Verify SSH authentication and perform a staggered push (or direct push if `.gitignore` is approved).
3. **Dry Run Vendoring:** Perform a dry run of `mass_sdk_vendoring.py` on a single known target (e.g., a lightweight ADK repo) to confirm extraction and `.git` stripping velocity.
