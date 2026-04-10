# Cor.Uphillsnowball.4: The Local Swarm Ascension

The previous milestones successfully laid the foundation: we cracked open the Apple Neural Engine (ANE) for local zero-cost embedding/training, eliminated AlloyDB costs in favor of PostgreSQL, built the Serverless Cloud Run backend, and forged the "Cursor Killer" autonomous testing loop.

Now, we unleash these tools. The next milestone is deploying the local fine-tuning swarms on your idle M-series chips to autonomously develop the ShadowTag AG-UI frontend on localhost.

## User Review Required

> [!CAUTION]
> Initiating the Local Swarm Ascension will engage the `SandboxDaemon` and `CinematicStudio` in a continuous loop. The autonomous agents will generate code, run the dev server, record the UI via ffmpeg, critique it using the ANE-backed God Mode embeddings + Gemini 2.5 Pro Vision, and auto-submit PRs via `publish_cinematic_pr.sh`.
> Ensure you are comfortable with heavy local compute usage (M-Series Neural Engine) during this phase.

## Proposed Changes

We will execute the autonomous development of the frontend (`frontend/app/GlassBoxDashboard.tsx` and peripheral UI elements) using the newly minted Cor.Omega v2.0 protocol.

### 1. Swarm Dispatcher Initiation

- **[NEW]** `scripts/swarm_dispatcher.py`
  - A script that loops through the PRD/Design requirements for the AG-UI, chunks them into tasks, and submits them to the `god_mode_admin.py` (which now has ANE offloading).

### 2. Autonomous UI Generation

- The God Mode engine will generate the `.tsx` components and CSS adhering to Anthropic/Google ADK design systems (using our `design-md` and `ui-ux-pro-max` skills).
- **Target:** `frontend/` directory structure.

### 3. BullMQ → Cloud Tasks Reconciliation

- As part of the Gideon OS / Boardroom architecture shift, we are fully deprecating BullMQ in favor of **Google Cloud Tasks + Pub/Sub** to achieve the "Cloud Run ONLY" mandate.
- This migration ensures compliance with the new Doctrine Doc v2 and reduces projected message queue costs.

### 4. The Cursor Killer Loop Execution

- For each generated component, the `SandboxDaemon` will spin up Vite/Next.js locally.
- The `CinematicStudio` will capture the X11/Mac screen interaction.
- The local ANE instances evaluating the multi-modal outcomes will issue a PASS/FAIL.
- If PASS: `publish_cinematic_pr.sh` is triggered.

## Verification Plan

### Automated Tests

- The build will be continuously monitored by the Cor.Judge 6.1 Serverless Sentinel.
- Cinematic Studio video artifacts will be attached to each PR for auditing.
- `finish_changes.py` (/omega-loop) will run between each swarm batch to ensure workspace hygiene.

### Manual Verification

- The User (The Board) will periodically review the generated PRs on GitHub and merge them if the Cinematic Studio videos prove the UI meets the Steve Jobs Mode aesthetic criteria.

# Phase 4: The Glass House Protocol & DOW CRSMC '25

With the local ANE swarm initialized, we must elevate the architecture into a "Military-Grade" Autonomous Defense System. The Sentinel will operate on a highly specialized Triad loop (Architect, Builder, Critic) utilizing ATP 5-19 (Composite Risk Management) as the core anchor for the 17-Layer DOW CRSMC '25 defense shield.

## Proposed Changes

### 1. The Autonomous Triad (Kosmos Swarm)

- **Architect (Gemini 3 Pro + Kosmos)**: Engages in deep Swarm research, mapping the repository and planning operations. It explicitly operates with high "Thinking" loops to identify optimal paths.
- **Builder (Gemini 3 Flash)**: Sandboxed worker. It receives the *approved* blueprint from the Architect and drafts the artifact or transaction script without direct file system write access.
- **Critic (DOW CRSMC '25 Sentinel)**: The ultimate safety officer. It enforces the 17-Layer DOW CRSMC matrix before *any* code touches the file system.

### 2. ATP 5-19 Core Enforcement

- **Implementation**: We will codify ATP 5-19 (Army Techniques Publication 5-19) into the Critic's logic in `src/governance/dow_crsmc_sentinel.py`. Every proposed action by the Builder will be assessed across Probability, Severity, and Risk Level.
- **Controls**: The Critic will mandate specific mitigations (e.g., EU 26 compliance blocks, Sandbox isolation, Identity-Aware Proxy verification) before green-lighting execution.

### 3. Glass House Telemetry

- **Omni-Channel Relay Update**: We will upgrade `src/relay_server.py` to capture `AGENT_THOUGHT_CHUNK` and stream the Architect's "Chain of Thought" explicitly to the React frontend UI.
- **Continuous Grounding**: As the Kosmos Swarm operates, it will automatically connect data streams through the GCP mesh to enforce the "Internal Affairs Bureau" anomaly detection model.
