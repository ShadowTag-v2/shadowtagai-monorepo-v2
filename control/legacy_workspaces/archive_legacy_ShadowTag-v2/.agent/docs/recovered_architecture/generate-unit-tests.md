---
description: Unit Test Generation Workflow
---

# Unit Test Generation Workflow

Trigger: When the user invokes this workflow. Instructions:

1. Analyze all Python files in the current active context.
2. For every file (e.g., utils.py), create a corresponding test file (e.g., test_utils.py).
3. Use the pytest framework.
4. Ensure every function has at least one positive test case and one edge case.
