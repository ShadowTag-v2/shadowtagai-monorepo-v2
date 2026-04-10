# Workflow: Scaffold & Handoff

**Trigger:** "Scaffold [Feature Name]"

**Steps:**

1.  **Plan:** Identify the files needed for the feature.
2.  **Create (Skeleton Mode):** Create the files with imports, types, and JSDoc comments only. (Follow the Skeleton Protocol).
3.  **The Handoff:**
    - Once files are created, run the terminal command: `code -r [filename]` (This opens the file in the current window).
    - _Alternative for Antigravity Internal:_ Run the tool `vscode_open_file`.
4.  **Cursor Placement:** (Optional) If possible, place the cursor inside the first main function.

// turbo-all
