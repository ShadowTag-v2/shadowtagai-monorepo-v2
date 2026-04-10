# The Omega "Yarn" Protocol v2.0
**Objective**: Maximum Code Integrity via Recursive Voting & Serverless Fan-Out.

## Roles
*   **The User**: Provides Raw Prompt.
*   **Antigravity (The Brain)**:
    *   Refines User Prompt into "Voteable Motion".
    *   Provides "Whiteboard Resources" (Context, Files).
    *   Applies "Standard Proposed Changes" (Refinement: Security, Perf, Style) between rounds.
    *   Executes Final Commit ("God Mode" Direct Write if >95% confidence).
*   **The n-autoresearch/Kosmos/BioAgents (The Swarm)**: Vote on the motion (Pass/Fail/Refine).
*   **Judge 6 (The Safety)**: Validates safety/security at each gate (NIST 800-53).

## The 3-Iteration Loop (The "Yarn")

### Iteration 1: The Raw Motion (Intent)
1.  **Input**: User Raw Prompt.
2.  **Antigravity Action**: Refine into a structured "Motion" (Technical Spec).
3.  **n-autoresearch/Kosmos/BioAgents Vote (Round 1)**: "Do we understand? Is this solvable?"
4.  **Judge 6**: Initial Risk Assessment.

### Iteration 2: The Draft & Refinement (Engineering)
1.  **Input**: The n-autoresearch/Kosmos/BioAgents' initial solution.
2.  **Antigravity Action**: Apply "Standard Proposed Changes" (Linting, Best Practices, Optimization).
3.  **n-autoresearch/Kosmos/BioAgents Vote (Round 2)**: "Is this refined code correct?"
4.  **Judge 6**: Safety Scan (Pass/Fail).

### Iteration 3: The Final Polish (Ratification)
1.  **Input**: The Refined Code.
2.  **Antigravity Action**: Final Polish (Docs, comments, minor tweaks).
3.  **n-autoresearch/Kosmos/BioAgents Vote (Round 3)**: Final Ratification.
4.  **Judge 6**: Final Certification.

## Execution Architecture ("Dina & Martin" Pattern)
*   **Orchestrator**: Cloud Scheduler (Nightly/Triggered).
*   **Fan-Out**: Pub/Sub topic per "Task" to decouple logic from scale.
*   **Workers**: Cloud Functions (or n-autoresearch/Kosmos/BioAgents Agents) process individual messages.
*   **Persistence**: Firestore (State) + BigQuery (Audit/Logs).
*   **Visibility**: Data Studio (Looker) dashboard for Auditor/Admin.
*   **Identity**: IAP (Identity Aware Proxy) + App Engine/Cloud Run for internal tools.

## God Mode (Direct Write)
*   **Condition**: If Round 3 passes Judge 6 with >95% confidence.
*   **Action**: Antigravity writes code directly to disk (bypassing IDE preview).
*   **Mechanism**: `judge_6.verify() -> direct_write()`.
