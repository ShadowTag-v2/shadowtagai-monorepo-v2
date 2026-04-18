# DOCTRINE: BEADS (Cor.Beads)
# The External Memory & Issue Tracker for Sovereign Agents.

## PHILOSOPHY
"Beads" (`bd`) is the external memory for agents. It provides Durable, Searchable, Git-Tracked institutional memory.

## CORE WORKFLOW
1.  **Discovery:** Agent finds a bug? Run `bd create "Fix login bug"`.
2.  **Planning:** Agent plans a feature? Run `bd create` with detailed plan in description.
3.  **Execution:** Agent claims issue (`bd claim <id>`), commits changes, tracks progress.
4.  **Verification:** Test fail? Reopen issue (`bd reopen <id>`), add notes, RCA, revised plan.
5.  **Closure:** Work complete? Close with notes (`bd close <id>`).

## DATA STRUCTURE (`.beads/issues.jsonl`)
-   **ID:** Unique identifier (e.g., `bd-1`).
-   **Title:** Concise summary.
-   **Description:** Detailed plan, context, or bug report.
-   **Status:** `open`, `in_progress`, `closed`.
-   **Notes:** Append-only log of decisions, RCA, verification results.
-   **Labels:** `bug`, `feature`, `task`.
-   **Dependencies:** `blocked_by`, `blocks`, `parent_of`, `child_of`.

## COMMANDS (Simulated)
-   `bd create <title> --desc <description>`
-   `bd list --json`
-   `bd show <id>`
-   `bd update <id> --status <status>`
-   `bd note <id> <text>`

## RULE
If you discover work, **DO NOT** put it in a markdown list. **DO** create a Beads issue.
