# BEADS: THE AGENTIC ISSUE TRACKER

**Concept:** "Issues All The Way Down"
**Source:** Steve Yegge / Pithom Labs
**Implementation:** Git-backed JSONL (`.beads/issues.jsonl`)

## Core Philosophy

1.  **Durability:** Agents have amnesia. Git does not.
2.  **Structure:** Markdown is fuzzy. JSONL is queryable.
3.  **Discovery:** Agents create issues when they find work.
4.  **Convergence:** Work is tracked, not lost.

## Schema (Implicit)

- `id`: Unique String (e.g., `base-123`)
- `title`: String
- `status`: `open` | `in_progress` | `closed` | `blocked`
- `priority`: Integer (0-4)
- `description`: String (Markdown allowed)
- `created_at`: ISO Timestamp
- `history`: List of events (comments, status changes)
- `dependencies`: List of IDs (blocked_by)

## CLI (`bd`)

- `bd create "Title" -d "Description"`
- `bd list --json`
- `bd show <id>`
- `bd update <id> --status in_progress`
- `bd comment <id> "Notes..."`

## Workflow

1.  **Discovery:** Agent finds bug -> `bd create`.
2.  **Planning:** Agent makes plan -> `bd create` (Epic) + child issues.
3.  **Execution:** Agent claims issue -> `bd update --status in_progress`.
4.  **Completion:** Agent closes -> `bd update --status closed`.
