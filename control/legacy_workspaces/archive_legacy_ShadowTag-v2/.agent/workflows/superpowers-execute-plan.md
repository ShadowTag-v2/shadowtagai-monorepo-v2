# Workflow: Superpowers Execute Plan

**Trigger:** `/superpowers:execute-plan`

**Goal:** Execute the code with Judge 6 Governance.

**Steps:**

1.  **Load:** Read the plan from Beads.
2.  **Generate:** Write the code files (e.g., `src/api/health.py`).
3.  **Judge:** Pass code through `JudgeSix.vet()`.
    - If Fails: Abort and notify.
    - If Passes: Write to disk.
4.  **Log:** Update Beads with "Action Completed".
