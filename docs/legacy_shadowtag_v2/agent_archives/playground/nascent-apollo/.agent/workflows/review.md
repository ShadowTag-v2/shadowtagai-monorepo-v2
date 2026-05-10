# Workflow: Code Review

**Trigger:** "Review this", "Check my work".

**Steps:**
1.  **Git Diff:** Run `git diff main` (or target branch).
2.  **Security Scan:** Check for API keys, SQLi, PII.
3.  **Performance Check:** N+1 queries, unnecessary re-renders.
4.  **Style Check:** Compare against `.agent/rules`.
5.  **Output:**
    -   Markdown list of "Blocking Issues" and "Nitpicks".
    -   Ask: "Apply fixes for Blocking Issues?"

// turbo
