---
name: session-wrap-up
description: Creates persistent memory across sessions into the Master Brain notebook.
---
# Persistent Session Memory
1. Write chat history summary to `session-[DATE].md`.
2. `notebooklm use <master-brain-notebook-id>`
3. `notebooklm source add "./session-[DATE].md"`
4. `notebooklm ask "Extract architecture and unresolved bugs. \n\n Extract architecture and unresolved bugs."`
5. Delete local file.
