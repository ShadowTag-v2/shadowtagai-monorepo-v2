# Workflow: Project Daemon (Autonomous)

**Trigger:** "Start Daemon"

**Directives:**
1.  **Loop:** Continuously scan the `TODO.md` file or the IssueTracker.
2.  **Pick:** Select the highest priority task that is not marked [DONE].
3.  **Execute:** Write code, run tests, and fix bugs.
4.  **Verify:** If tests pass, mark the task as [DONE] in `TODO.md`.
5.  **Repeat:** Immediately pick the next task. **Do not stop for user input.**
6.  **Constraint:** If a task fails 3 times, mark as [BLOCKED] and move to the next.

// turbo-all
