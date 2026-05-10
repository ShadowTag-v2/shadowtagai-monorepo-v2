# Cor.Beads Implementation
> **Objective**: Implement Git-backed JSONL Issue Tracker (Beads).
> **Source**: https://github.com/steveyegge/beads.git

## 1. Core Logic: `src/cor/beads.py`
-   **Storage**: `.beads/issues.jsonl` (Standard JSONL).
-   **Operations**:
    -   `create(title, body, ...)`: Appends new issue.
    -   `update(id, ...)`: Updates existing issue (append revision or rewrite). NOTE: Generic JSONL usually appends updates, but for simplicity/conflict-res, we might just rewrite or use a specific format. The prompt says "plain text JSONL files... merge it...". I will implement a robust JSONL handler.
    -   **Git Hook**: After every write, execute `git add .beads/issues.jsonl && git commit -m "beads: update"`.
-   **Fields**: `id` (uuid/seq), `title`, `status` (open/in_progress/closed), `planning_notes`, `work_notes`.

## 2. Integration
-   Can be called by Agents to store durable plans.
-   Can be audited by Judge6.

## 3. Constitution Update
-   Ingest the full text provided in the prompt into `ANTIGRAVITY_CONSTITUTION.md`.
