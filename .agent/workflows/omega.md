# Workflow: Omega Loop (v4)

**Trigger:** "@workflow /omega [Goal]"

**The Loop:**
1.  **Scan:** Read the workspace state, `git status`, and the [Goal].
2.  **Research (Parallel):**
    -   *Browser:* Search documentation for unknown libs.
    -   *Local:* Grep existing patterns in `src/`.
3.  **Plan:** Generate a discrete step-by-step Execution Plan.
4.  **Execute (The "Iron Hand"):**
    -   **If File Missing:** Create Skeleton -> Open File -> Trigger GCA.
    -   **If Bug:** Write Test -> Fail -> Fix -> Pass.
    -   **If Blocked:** Run `sudo` fix or browse for solution.
5.  **Verify:** Run full test suite.
6.  **Commit:** `git commit -am "Omega: [Action Completed]"`
7.  **Iterate:** If [Goal] is not 100% complete, repeat loop.
