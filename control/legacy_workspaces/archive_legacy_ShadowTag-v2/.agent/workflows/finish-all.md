# Workflow: Batch Finish Open Files

**Trigger:** "Finish all open files" or "Batch complete".

**Goal:** Iterate through all currently open editors, identify incomplete code (TODOs, empty functions), implement the logic, and save.

## Step 1: Context Gathering

1.  **Get Open Files:** Retrieve the list of all currently open text documents in the editor.
2.  **Filter:** Exclude files that are:
    - In `node_modules`
    - Read-only
    - Not source code (e.g., logs, binaries).

## Step 2: The Loop (File by File)

For each file in the list:

1.  **Analyze:** Read the file content. Look for:
    - `// TODO` or `# TODO` comments.
    - Empty function bodies.
    - "Ghost text" patterns (incomplete logic).
2.  **Generate:**
    - Implement the missing logic _in place_.
    - **Constraint:** Do not change existing working code. Only fill gaps.
3.  **Apply:**
    - Overwrite the file content with the complete version.
    - **Important:** Do NOT use a Diff/Plan. Apply the edit directly (`edit_file`).
4.  **Save:** Trigger a save (`cmd+s` equivalent).
5.  **Close:** (Optional) Close the file after finishing to keep the workspace clean.

## Step 3: Final Report

- List the files modified.
- Report any errors (e.g., "Could not understand intent in `utils.ts`").
