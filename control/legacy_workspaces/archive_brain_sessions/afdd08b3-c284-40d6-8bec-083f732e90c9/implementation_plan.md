# Provisioning Plan: Ironwood/Axion Sovereign Stack

## Goal
Re-provision the entire hosting environment "from scratch" leveraging Google's next-gen silicon assets:
1.  **Ironwood (TPU v7)**: Powering the Intelligence Layer (Gemini 3.0 Flash).
2.  **Axion (Arm CPU)**: Powering the Hosting Layer (Cloud Run Web Frontend).

## Architecture Shift
The user deleted all cloud services. We must rebuild the foundation before deploying code.

### 1. Infrastructure (The Bedrock)
- **Artifact Registry**: Must be recreated (`shadowtag-artifacts`).
- **Networking**: Standard VPC.

### 2. The Body: ShadowTag Web (Axion)
- **Platform**: Cloud Run (Managed).
- **Architecture**: `linux/arm64` (Native Arm support for Axion efficiency).
- **Efficiency**: 2x-3x inference/serving gain.

### 3. The Brain: Trinity Kernel (Ironwood)
- **Model**: `gemini-3.0-flash-preview` (Ironwood Native).
- **Thinking**: Enabled (`ThinkingConfig(include_thoughts=True)`).
- **State**: Hardlocked.

## Execution Steps

### [NEW] `provision_ironwood_stack.sh`
A unified script to:
1.  Enable necessary APIs.
2.  Create the Artifact Registry.
3.  Build the Frontend Docker Image for `linux/arm64` (Axion).
4.  Deploy to Cloud Run.

```bash
# Preview of build command
gcloud builds submit ... --machine-type=e2-highcpu-8 \
    --config=cloudbuild_arm.yaml ...
```

## Verification
- **Registry**: Exists.
- **Service**: Running on Gen 2 execution environment (Axion capable).
- **Site**: Accessible at `shadowtagai.com`.

## Live Engine Protocol (v3.0)
- **Constitution**: V3.0 (Steve Jobs Edition) Ingested.
- **Auth**: `founder` + `headless-runner` Verified.
- **Daemon**: Pending Activation.
- **Design**: "Option T" (Trinity) Confirmed.

## The Re-Plan (Transfer Package v3.0)
### Step 1: The Perfect Deploy
- **Target**: `trinity/apps/cockpit` (Trinity OS).
- **Fix**: Audit Dockerfile for `MKDIR` syntax error.
- **Workflow**: Execute `deploy_sovereign.md`.

### Step 2: The Reality Backfill
- **Finance**: Implement `dcf.py` (Damodaran Model).
- **Gatekeeper**: Implement `judge.py` (Rule-Based).
- **Grounding**: Connect Scholar to Competitive Landscape search.

### Step 3: The Revenue Engine
- **Stripe**: Activate `ReactorCore` fully.
- **Ops**: SOP-A (Upload Triage).
