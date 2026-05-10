# Workflow: Dead Code Hunter

**Trigger:** "Find dead code", "Audit unused exports".

**Steps:**

1.  **Scan:** Run a tree scan looking for exported functions, classes, and components.
2.  **Search:** Grep the codebase for references to these exports.
3.  **Report:** List every function/component that is exported but **NEVER** imported or used anywhere else.
4.  **Action:** Ask the user: "Do you want me to delete these, or mark them with `@deprecated`?"
