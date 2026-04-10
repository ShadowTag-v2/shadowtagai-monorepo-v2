# Thread Code Inventory & SOP Extraction

**Agent:** 1 — Thread Miner
**Target:** `shadowtag-omega-v4`

## Code Snippets & Scripts

1. **`god_mode_push.py`**: Python script using `PyGithub` to authenticate via JWT/PEM and execute repository payload transfers.
2. **`batch_push.py`**: Script to parse unpushed `git log` hashes and execute iterative `git push origin <hash>:main` to bypass 500 HTTP server limits.
3. **`lfs_push.py`**: Python wrapper to explicitly bind remote credentials and execute `git lfs push --all origin` prior to pushing tree data.
4. **`design_police_linter.py`**: Deep regex scanner targeting hardcoded Hex colors, RGB values, and raw pixel dimensions inside `[ts, tx, js, jsx, css, html]` files.
5. **`.git/hooks/pre-commit`**: Shell script serving as Gate 0 execution for the Design Police Linter.

## Configs & Infrastructure

1. **`.vscode/settings.json`**: Editor states transitioning from Pylance blockages to `Jedi` bypasses, and definitively back to specific `.venv` Pylance analysis extra paths.
2. **`biome.json`**: Linter configurations ignoring `.venv` and `bazel-*` environments.
3. **`WORKSPACE`**: Baseline Bazel root anchor.

## Extracted SOP Patterns & Logic

- **COR.30 Vibe Coding**: 30 OWASP-flavored rules spanning Session Auth, Secrets, CORS, RLS, and Webhook Signatures.
- **The Omega Loop**: Standard cleanup workflow (format/lint/commit).
- **God Mode Operations**: Explicit directive for the agent to assume maximum autonomy without requesting read/write permission.
- **Sequential-Thinking vs Memory MCP**: Structural distinction where Memory=State/Persistence and Sequential-Thinking=Process/Logic.
- **A2UI Specification**: Deep JSONL schemas driving the UI rendering loops.

## Tooling Clones

- <https://github.com/tw93/Mole.git> (Mac optimization)
- <https://github.com/modelcontextprotocol/servers.git> (10 Core MCP definitions)
- <https://github.com/googleworkspace/cli.git> (Official workspace commands)
- <https://github.com/github/gitignore.git> (Baseline definitions)
