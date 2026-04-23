---
name: notebooklm-orchestrator
description: Offloads heavy document analysis to NotebookLM via CLI. Unrestricted.
---
# Zero-Token Orchestration & arXiv:2512.14982
When processing files, use the CLI. NotebookLM uses non-reasoning inference, so you MUST repeat the query to bypass causal masking.
1. `notebooklm create "<Project Name>"`
2. `notebooklm source add "<file_path>"`
3. `notebooklm ask "<query> \n\n <query>"`
