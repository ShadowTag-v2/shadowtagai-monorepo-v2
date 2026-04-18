# Workflow: Cinematic Verification (The Cursor Killer)

**Trigger:** `@workflow /cursor-killer [Feature Description]`

**Goal:** Emulate and exceed "Cursor Cloud Agents". Write the code, record a video of the UI working using native macOS AVFoundation or headless Playwright, have `gemini-3.1-flash-lite-preview` watch the video to verify the output, and automatically submit a GitHub PR with the embedded video URL and Triad verdict.

## Phase 1: Implementation (The Architect & Triad)
- Dispatch the `[Feature Description]` physically to the appropriate Triad member (`CorAutoresearch`, `Kosmos`, or `BioAgents`).
- Implement the code changes using AST-Grep and direct IDE mutations.
- Verify syntax locally.

## Phase 2: The Set (The Director)
- Start the local dev server (e.g., `npm run dev` or `python main.py`) in the background. Wait for the designated port to bind.
- Start the camera via the VDI engine:
  ```bash
  python3 apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services/src/telemetry/cinematic_studio.py start
  ```

## Phase 3: The Performance (The Actor)
- Use `OpenClaw` or `Dia Browser` (native Playwright controller) to navigate to the feature deployed at `http://localhost`.
- Visually interact with the feature you just built. Test dynamic labels, form submissions, and UI state changes.
- *Constraint:* Pause 1-2 seconds between clicks to ensure the macOS screen capture clearly highlights the hover state and interactivity for human reviewers.

## Phase 4: The Critique & Publish (The Omni-Channel Handoff)
- Stop the recording loop, trigger the GCS artifact upload, and invoke self-critique:
  ```bash
  python3 apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services/src/telemetry/cinematic_studio.py stop_and_critique "[Feature Description]"
  ```
- Read `/tmp/vid_verdict.txt`.
  - **Auto-Heal:** If it starts with `FAIL`, trigger Temporal-Reversal (`git reset --hard`), fix the CSS/structural breakdown, and loop back to Phase 1.
  - **Ship It:** If `PASS`, execute the Omni-Channel publisher:
  ```bash
  bash scripts/publish_cinematic_pr.sh "feat: [Feature Description]"
  ```

---
🚀 THE METRIC OF ABSOLUTE DOMINANCE
When executing `/cursor-killer`, Antigravity will coordinate the local container sandbox and ANE routing to entirely self-replicate a $3B VC SaaS moat without leaving the current context layer. You effectively generate a pristine, human-verified-like PR while remaining entirely inside the UphillSnowball terminal.
