# Phase 14: Asset Ingestion & Thread Recovery

I will systematically ingest the requested repositories, apply the Airbnb JavaScript style guide, and recover the "Cor.Claude Transfer Thread" state to ensure total alignment with the Sovereign OS V7 vision.

## User Review Required

> [!IMPORTANT]
> Some repositories in the provided list may require specific authentication or are already present in `/Users/pikeymickey/Documents/GitHub`. I will prioritized symbolic linking for existing assets to save disk space and bandwidth.

> [!WARNING]
> Applying the `airbnb/javascript` style guide across multiple repositories may trigger significant linting changes. I will focus on the core `apps/` and `src/` directories first.

# Sovereign Silicon Bridge Integration Plan

Provide a brief description of the problem, any background context, and what the change accomplishes. The Sovereign Silicon Bridge (`maderix/ANE`) allows direct LLM compute on Apple's Neural Engine. We will integrate this custom architecture into UphillSnowball to enable cost-free, air-gapped PMCS code evaluations and tests.

## User Review Required
>
> [!IMPORTANT]
> ANE currently runs single-layer Transformer training in Objective-C. To serve full LLMs for UphillSnowball, we must compile a full Llama/Mistral forward pass in MIL (Model Intermediate Language) or use a local HTTP stub (C++) referencing the ANE backend. We need your approval on the architectural hand-off (Local HTTP Server vs. Python FFI).

### ANE Project Scope & Expectations

As noted in the ANE repository:

* **Proof of Concept:** This is a research project utilizing reverse-engineered `_ANEClient` and `_ANECompiler` private APIs, not a production framework.
* **Current State:** Training works but utilization is low (~2-3% of peak). Many operations fall back to CPU.
* **UphillSnowball Vision:** While currently limited, the ultimate vision for this integration is allowing the user to log directly into UphillSnowball running locally on the ANE, while the agent (Antigravity/Swarm) "simply watches" or assists passively without incurring any cloud costs or exposing data to external APIs.
* **Disclaimer:** Apple's private APIs have no stability guarantee. No Apple proprietary code is included.

## Proposed Changes

### 1. UphillSnowball Configuration (`apps/uphillsnowball/uphillsnowball/config.yaml`)

We will add an `ane_local` mode that overrides the Gemini cloud API for scanning and remediation operations.

#### [MODIFY] config.yaml

We will add:

```yaml
  # Sovereign Silicon Bridge (Local ANE)
  enable_ane_bridge: true
  ane_bridge_url: "http://localhost:8081/v1/chat/completions"
```

### 2. ANE Local Inference Server (`libs/ANE/server/`)

We will create a lightweight C++ HTTP bridge (similar to the Midas microservice) around the Objective-C ANE core.

#### [NEW] main.cpp (ANE HTTP Bridge)

A new server listening on port `8081` that wraps `train_large.m` mechanics to perform forward-pass inference.

### 3. Python Service Dispatcher (`apps/uphillsnowball/uphillsnowball/uphillsnowball.py`)

Modify the UphillSnowball scanner to route requests conditionally to the ANE Local Server.

## Verification Plan

### Automated Tests

* Run `curl -X POST http://localhost:8081` against the ANE bridge to verify inference capabilities.
* Execute UphillSnowball PMCS with `enable_ane_bridge: true` and verify no network requests route to `generativelanguage.googleapis.com`.

---

# [Previous Goal Description]

## Proposed Changes

### [Asset Management]

#### [NEW] [ingest_assets.sh](file:///Users/pikeymickey/.gemini/antigravity/playground/cosmic-crab/scripts/ingest_assets.sh)

A script to automate the cloning of missing repositories and the symbolic linking of existing ones from the "Deleted Users" recovery path if applicable.

#### [NEW] [apply_airbnb_style.sh](file:///Users/pikeymickey/.gemini/antigravity/playground/cosmic-crab/scripts/apply_airbnb_style.sh)

A script to install and configure `eslint-config-airbnb` and related plugins across the target web projects.

### [Sovereign State Recovery]

#### [MODIFY] [task.md](file:///Users/pikeymickey/.gemini/antigravity/brain/5221bc1c-bb1a-4069-b419-0e083757f0a1/task.md)

Update with Phase 14 tasks for asset ingestion and linting.

## Verification Plan

### Automated Tests

* Run `ls -L` to verify symbolic links.
* Run `npm run lint` or `eslint` to verify Airbnb style guide application.
* Verify repo health with `git status` in a subset of new clones.

### Manual Verification

* Review the `shadowtag-web` landing page to ensure no breakage after style application.
* Confirm the presence of core "Memory Beads" (JSONL) in the `.beads` directory.
