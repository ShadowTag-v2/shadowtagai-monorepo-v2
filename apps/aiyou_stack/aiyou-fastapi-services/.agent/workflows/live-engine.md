---
description: 'God Mode: Live Engine Repair Protocol (COR.86)'
---

# LIVE ENGINE REPAIR PROTOCOL

> **MODE**: LIVE FIRE (NO SIMULATION)
> **AUTHORITY**: Directory Access Granted. Accept All Changes.

## INSTRUCTIONS

1.  **ITERATE**: Loop through every open tab and active file.
2.  **REPAIR**:
    - **READ** content.
    - **FIX** all linter errors (imports, formatting, type checks).
    - **REWRITE** hardcoded secrets to `os.getenv()`.
    - **OVERWRITE** the file using `file_writer` (No Diffs).
3.  **RESOURCES**: Use `web_search` or `drive_fetcher` if context is missing.
4.  **VERIFY**: Run NATIVE CURL to check health endpoints.
5.  **LOOP**: Recurse immediately.

## STATUS

IGNITION.
