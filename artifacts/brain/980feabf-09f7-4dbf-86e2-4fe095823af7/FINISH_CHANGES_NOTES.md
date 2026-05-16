# Egress Script (`finish_changes.py`) Methodology and Fixes

## Context

During the execution of `scripts/finish_changes.py`, the `pre-commit` hook for `pytest-coverage` repeatedly failed in the `ShadowTag-v2` repository. This repository is structured as a monorepo containing internal applications, internal libraries (`libs/`), and external submodules downloaded for ingestion or tooling.

The issues encountered and their corresponding fixes are documented below. While these specific fixes were applied to the `ShadowTag-v2` repository configuration files, the methodology and underlying principles are applicable to any Python-based monorepo running automated testing in isolated environments.

## Issues and Resolutions

### 1. Pre-commit Isolated Environment Dependency Failures (ModuleNotFoundError)

*   **Symptom:** `pytest` failed inside the `pre-commit` sandbox with `ModuleNotFoundError: No module named 'passlib'` (and later `sqlalchemy`).
*   **Root Cause:** The `pre-commit` tool creates isolated virtual environments for its hooks. If the hook's `language` is set to `python` and it doesn't explicitly install the project's dependencies, it cannot access installed libraries like `passlib` or `sqlalchemy`, even if they exist in the host machine's Python environment.
*   **Methodology/Fix:**
    *   Change the hook's `language` to `system` in `.pre-commit-config.yaml`.
    *   Set the `entry` point to use the system's Python interpreter: `entry: env PYTHONPATH=. python3 -m pytest`.
    *   *Why this works:* This bypasses `pre-commit`'s isolated environment generation and executes the command directly in the host environment where all project dependencies are already installed.

### 2. Monorepo Namespace Collisions (ImportPathMismatchError)

*   **Symptom:** `pytest` failed with `ImportPathMismatchError` citing duplicate module names (e.g., `conftest.py` existing in both `tests/` and `libs/tests/`).
*   **Root Cause:** When `pytest` collects tests across multiple directories that are not explicitly defined as Python packages (missing `__init__.py`), it uses the file's base name as the module name. If two folders have a `conftest.py`, pytest attempts to load two modules named `conftest`, causing a collision.
*   **Methodology/Fix:**
    *   Initialize the directories as distinct Python packages by creating empty `__init__.py` files (e.g., `libs/__init__.py` and `libs/tests/__init__.py`).
    *   Initially, passing `--import-mode=importlib` to the pytest args was attempted, but this caused issues with downstream setups. Properly defining package structures natively prevents the collision at the source.

### 3. Pytest Over-scanning Submodules / Third-Party Repos

*   **Symptom:** `pytest` attempted to run a `test_agent.py` script located deep within an external repository clone (`libs/external/A2UI/...`), which threw an unexpected `SystemExit: 1` and crashed the test suite. It also tried to execute a `setup.py` that tripped on pytest CLI arguments.
*   **Root Cause:** By default, `pytest` scans all directories downwards looking for files matching `test_*.py` or `*_test.py`. In a monorepo containing cloned external tools or submodules, this leads to pytest blindly executing third-party tests that may have conflicting requirements, environments, or exit calls.
*   **Methodology/Fix:**
    *   Strictly define testing boundaries in `pytest.ini`.
    *   Set `testpaths`: Explicitly list the directories containing *your* tests (e.g., `apps`, `libs/tests`, `tests`). Do *not* list root folders that contain unvetted code (like the root `libs/` if it contains `libs/external/`).
    *   Set `norecursedirs`: Aggressively blacklist irrelevant directories, especially `node_modules`, `external_repos`, `libs/external`, `venv`, etc.

### 4. Flaky `end-of-file-fixer` Modifying Index Mid-Commit

*   **Symptom:** `git commit` fails because unstaged files are detected immediately after staging, specifically `.pids/flyingmonkeys.pid` and `.nx/` cache files.
*   **Root Cause:** The `end-of-file-fixer` hook automatically modifies files to ensure they end with a newline. Because these `.pid` and cache files are frequently updated by other background processes, adding them to the index (`git add -A`) triggers the fixer, which modifies them and immediately renders the index out-of-sync.
*   **Methodology/Fix:**
    *   Force remove dynamic/volatile files from the git index: `git rm -rf --cached .pids/flyingmonkeys.pid`.
    *   Ensure `.gitignore` properly covers volatile directories (`.pids/`, `.nx/`) so they aren't staged in the first place during massive `git add -A` sweeps in the egress script.

## Future Updates to `scripts/finish_changes.py`

When updating `finish_changes.py` for broad usage across multiple repositories, consider adding the following autonomous checks:

1.  **Dependency Alignment:** Before running `pre-commit`, the script could ensure `requirements.txt` is fully pip-installed into the active environment, warning the user if dependencies are missing.
2.  **Gitignore Audit:** The script could check if frequent offenders like `.pids`, `.nx`, `node_modules` are in `.gitignore` and offer to append them to prevent index desync during `git add -A`.
3.  **Safe Pytest Boundaries:** If `pytest` is detected, the script could warn if `pytest.ini` lacks `testpaths` or `norecursedirs`, recommending strict boundaries to prevent over-scanning.
