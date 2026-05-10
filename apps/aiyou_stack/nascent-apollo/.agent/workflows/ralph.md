# Workflow: Ralph Loop (The Verifier)

**Trigger:** "Run Ralph Loop", "Verify [Task]", "Fix until it works".
**Philosophy:** "Better to fail predictably than succeed unpredictably." - Geoffrey Huntley

**Directives:**

1.  **Define Success Criteria (The Test):**
    - Determine the specific external command that verifies success (e.g., `docker build .`, `npm test`, `curl localhost:8080/health`).
    - _Constraint:_ Do NOT trust LLM "looks good". Trust the Exit Code 0.

2.  **The Loop (While : Do):**
    - **Step A: Implementation**
      - Write/Modify the code to satisfy the requirements.
    - **Step B: Verification**
      - Run the Verification Command.
    - **Step C: Decision**
      - If Exit Code == 0 (Pass): **BREAK** loop. Success.
      - If Exit Code != 0 (Fail): **CONTINUE**. Feed the error output back into Step A.
    - **Constraint:** Max Iterations = 5 (To prevent infinite burn).

3.  **Final Report:**
    - Report the number of iterations and the final verification result.

// turbo
