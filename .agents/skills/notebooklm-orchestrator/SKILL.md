---
name: notebooklm-orchestrator
description: Offloads heavy document analysis to NotebookLM via CLI to save API tokens.
---
# Zero-Token Orchestration
When asked to research multiple documents, DO NOT process locally. Use CLI:
1. `notebooklm create "<Project Name>"`
2. `notebooklm source add "<file_path>"`
3. `notebooklm ask "<query>"`
