# Workflow: Scaffold & Handoff

**Trigger:** "Scaffold [Feature Name]"

**Steps:**
1.  **Plan:** Identify the files needed for the feature.
2.  **Create (Skeleton Mode):** Create the files with imports, types, and JSDoc comments only utilizing the `.agent/rules` Constitution JSDoc `@intent` spec.
3.  **The Handoff:**
    -   Once files are created, run the terminal command: `code -r [filename]` (This opens the file in the current window).
    -   *Alternative for Antigravity Internal:* Run the tool `vscode_open_file`.
4.  **Cursor Placement:** Place the cursor inside the first main function.
