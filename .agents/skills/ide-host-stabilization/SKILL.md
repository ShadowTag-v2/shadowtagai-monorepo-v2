---
name: ide-host-stabilization
description: Procedure for recovering from IDE Extension Host crashes, resolving MCP server drops, stopping FSEvents leaks, and fixing workspace JSON corruption.
---
# IDE Host Stabilization

## When to use this skill
When the IDE logs `Events were dropped by the FSEvents client`, Extension Host exits with code 5, or MCP servers fail to bind ports.

## 1. The Watcher Doctrine (FSEvents)
When the IDE logs `Events were dropped by the FSEvents client`, the monorepo is too large. You MUST configure `files.watcherExclude` in `.vscode/settings.json` and `.code-workspace` files to aggressively ignore `**/node_modules/**`, `**/.venv*/**`, `**/.mypy_cache/**`, `**/.pixi/**`, `**/clones/**`, `**/clone-base/**`, `**/external_repos/**`, `**/external_sdks/**`, `**/deep-archive/**`, `**/archive/**`, `**/.git/objects/**`.

## 2. Workspace JSON Integrity
If `.code-workspace` fails to parse, use a Python script to strip `//` comments and trailing commas before parsing with `json.loads()`:
```python
import json, re
with open("pnkln.code-workspace", "r") as f:
    content = f.read()
content = re.sub(r"//.*", "", content)
content = re.sub(r",(\s*[\]}])", r"\1", content)
data = json.loads(content)
with open("pnkln.code-workspace", "w") as f:
    json.dump(data, f, indent=2)
```

## 3. Config Pollution (Linter Drift)
If the LSP complains about `organizeImports`, `noConsoleLog`, `include`, or `ignore`, JavaScript configuration has leaked into the Python settings. Delete these keys from `ruff.toml`, `pyproject.toml`, or workspace settings.

## 4. Freeze Extension Fetch Loops
If `open-vsx.org` is unreachable, the IDE crashes trying to auto-update. Set `"extensions.autoUpdate": false` and `"extensions.autoCheckUpdates": false` in workspace settings.

## 5. Toxic Extension & Zombie Eradication
Uninstall extensions causing V8 crashes or 50%+ CPU lockups (e.g., ES7 Snippets, LiveServer). Run `pkill` to kill ghost MCP processes blocking port binding.

## 6. Missing Agent State
If logs show `Failed to stat .../knowledge/_views/metadata.json`, create:
```bash
mkdir -p /Users/pikeymickey/.gemini/antigravity/knowledge/_views/
echo '{}' > /Users/pikeymickey/.gemini/antigravity/knowledge/_views/metadata.json
```
