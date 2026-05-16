---
description: Enforce strict secret management.
globs: ['**/*']
---

# No Secrets in Code

You must NEVER commit secrets (API keys, tokens, passwords) to the codebase.

## Actions

1.  **Detect:** If you see a string that looks like a secret, STOP.
2.  **Move:** Move the secret to `.env`.
3.  **Reference:** Replace the hardcoded secret with `os.environ["SECRET_NAME"]`.
4.  **Ignore:** Ensure `.env` is in `.gitignore`.
