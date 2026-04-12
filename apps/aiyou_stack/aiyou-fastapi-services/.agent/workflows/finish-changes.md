---
description: Finishes changes in open files by linting, formatting, staging, and committing them.
---

# Finish Changes Protocol

This workflow automates the "Scan, Polish, Save" sequence for all modified files in the repository.

1.  **Scan**: Identifies all modified and likely untracked files.
2.  **Polish**: Runs formatters (Black, Isort, Prettier).
3.  **Save**: Stages and commits changes with a timestamp.

**To Execute:**

```bash
# This script is directory-agnostic.
./scripts/scan_and_finish.sh
```
