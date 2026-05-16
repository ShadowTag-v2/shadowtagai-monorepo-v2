# Workflow: Cinematic Verification (The Cursor Killer)

**Trigger:** `@workflow /cursor-killer [Feature Description]`

**Goal:** Emulate and exceed "Cursor Cloud Agents". Write the code, record a video of the UI working, have Gemini 2.5 Pro watch the video to verify, and submit a GitHub PR with the video attached.

## Phase 0: Doctrinal Rehearsal (The ROC Drill - J.1)

"Amateurs discuss strategy. Professionals rehearse execution." We NEVER execute a critical operation without a Digital ROC Drill:

- **The Back-brief**: State intent back to User.
- **The Rock Drill (Simulation)**: Walk logic flow. Identify friction.
- **PCC/PCI**: Pre-Combat Checks (Keys, Repo, Rollback).
- **LD**: Cross Line of Departure only when complete.
- **Context**: Founder Erik is the Commander. The Board is the Battle Staff. We rehearse before we breach.

## Phase 1: Implementation (The Architect)

- Implement the `[Feature Description]` requested.
- Verify syntax locally.

## Phase 2: The Set (The Director)

- Start the local dev server (e.g., `npm run dev` or `python main.py`) in the background. Wait for the port to bind.
- Start the camera: `python3 src/telemetry/cinematic_studio.py start`

## Phase 3: The Performance (The Actor)

- Use native browser automation or `Dia Browser` to physically navigate to `http://localhost:3000` (or whichever port is active).
- Visually interact with the feature you just built (click the new buttons, fill out the new forms).
- _Constraint:_ Pause 1-2 seconds between clicks so the video is readable by human reviewers.

## Phase 4: The Critique & Publish

- Stop recording and trigger self-critique: `python3 src/telemetry/cinematic_studio.py stop_and_critique "[Feature Description]"`
- Read `/tmp/vid_verdict.txt`.
  - **Auto-Heal:** If it starts with `FAIL`, trigger Temporal-Reversal (`git reset --hard`), fix the CSS/logic, and loop back to Phase 1.
  - **Ship It:** If `PASS`, execute the publisher: `bash scripts/publish_cinematic_pr.sh "feat: [Feature Description]"`
