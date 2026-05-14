# Workflow: Pilot - Decision Integrity Protocol

**Trigger:** "Pilot Mode", "Check this idea", "Pre-Agent Check".

**Goal:** Verify *why* we are doing something before we do it. Avoids efficient execution of bad ideas.

## Phase 1: Diagnostics (NotebookLM Simulation)
1.  **Idea Injection:** User provides a concept or doc.
2.  **The Critique:** Agent acts as "The Critic".
    -   *Prompt:* "Analyze this plan. What are the top 3 assumptions that could fail? What is missing?"
3.  **Gap Analysis:** List the holes.

## Phase 2: Decision
-   **Go/No-Go:**
    -   If holes are critical: **STOP**. Ask user to clarify.
    -   If solid: **PROCEED**.

## Phase 3: Handoff to Beads
-   If PROCEED:
    -   Create a Bead Issue (`bd create "Project Name" --desc "Verified by Pilot"`)
    -   Agent switches to "Passenger/Execution" mode to implement.

// turbo
