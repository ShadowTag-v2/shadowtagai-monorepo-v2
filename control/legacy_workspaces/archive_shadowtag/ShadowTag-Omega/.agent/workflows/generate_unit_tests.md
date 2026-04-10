---
description: Generates strict Unit Tests for Python/FastAPI using strict protocols.
---

# Goal
Create comprehensive unit tests for the selected file, ensuring coverage for success paths, edge cases, and error handling.

# Steps
1. **Analyze**: Identify all public functions, classes, and endpoints in the target file.
2. **Plan**: Outline test cases for:
    - "Happy Path" (Expected success)
    - "Edge Cases" (Invalid inputs, 404s)
    - "Security" (Auth checks, if applicable)
3. **Execute**:
    - Write tests using `pytest` (standard for this project).
    - Rule: Always name the file `tests/test_<filename>.py`.
    - Rule: Use `unittest.mock` or `pytest-mock` for external dependencies.
4. **Verify**:
    - Run `python -m pytest <new_test_file>` immediately.
    - Fix failures iteratively until all pass.
