# Workflow: Generate Unit Tests

**Trigger:** "Generate tests", "Write tests for file".

**Steps:**

1.  **Analyze:** Read target file(s). Identify public functions and edge cases.
2.  **Check Existing:** Look for existing `*.test.ts` or `__tests__`. Add to them if found; create if not.
3.  **Write Code:**
    - Use standard library (Jest/Vitest/Pytest).
    - Mock external calls/DB.
    - **Constraint:** Ensure compilation.
4.  **Verify:**
    - Run the specific test command.
    - If failure, fix _test code_ (max 2 retries).
5.  **Report:** Summary of pass/fail.

// turbo
