# Workflow: Batch Finish Open Files

**Trigger:** "Finish all open files" or "Batch complete".

**Goal:** Iterate through all currently open editors, identify incomplete code (TODOs, empty functions), implement the logic, and save.

## Step 1: Context Gathering
Retrieve the list of all currently open text documents in the editor. Exclude `node_modules`.

## Step 2: The Loop (File by File)
1.  **Analyze:** Find `// TODO` or `# TODO` comments.
2.  **Generate:** Implement missing logic *in place*. Do not change working code.
3.  **Apply:** Overwrite file content via `multi_replace_file_content` or `replace_file_content`.
4.  **Save/Close:** Move to next file.
