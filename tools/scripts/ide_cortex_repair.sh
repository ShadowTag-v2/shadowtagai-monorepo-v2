#!/usr/bin/env bash
set -euo pipefail

echo "🚀 [PNKLN SENTINEL] INITIATING FULL IDE & LINTER REPAIR..."

python3 - << 'EOF'
import os
import json

# ==============================================================================
# 1 & 2. FIX TY & RUFF LSP SCHEMAS
# ==============================================================================
print("→ [1] Repairing VS Code Settings (Ruff & Ty schemas)...")
settings_paths = [
    ".vscode/settings.json",
    "pnkln.code-workspace",
    "Monorepo-Uphillsnowball.code-workspace"
]

ruff_bad_keys = ['organizeImports', 'noConsoleLog', 'include', 'ignore', 'fixAll', 'showNotifications', 'configurationPreference', 'showSyntaxErrors', 'exclude', 'lineLength', 'logLevel', 'logFile']
ty_bad_keys = ['pythonPath', 'enable', 'pythonVersion']

for path in settings_paths:
    if not os.path.exists(path):
        continue
        
    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"  ⚠️ Error parsing {path}: {e}")
        continue

    target = data.get('settings', data) if 'code-workspace' in path else data
    changed = False

    # Clean root keys
    for k in list(target.keys()):
        if k.startswith('ruff.') and k.split('ruff.')[1] in ruff_bad_keys:
            del target[k]
            changed = True
            
        if k.startswith('ty.') and k.split('ty.')[1] in ty_bad_keys:
            del target[k]
            changed = True

    # Clean nested objects
    if 'ruff' in target and isinstance(target['ruff'], dict):
        for k in ruff_bad_keys:
            if k in target['ruff']:
                del target['ruff'][k]
                changed = True
                
    if 'ty' in target and isinstance(target['ty'], dict):
        for k in ty_bad_keys:
            if k in target['ty']:
                del target['ty'][k]
                changed = True

    # ==============================================================================
    # 3. SHIELD FSEVENTS FILE WATCHER
    # ==============================================================================
    watcher = target.get('files.watcherExclude', {})
    new_excludes = {
        '**/.venv/**': True,
        '**/node_modules/**': True,
        '**/.lancedb_data/**': True,
        '**/data/lancedb/**': True,
        '**/.git/objects/**': True
    }
    if any(k not in watcher for k in new_excludes):
        watcher.update(new_excludes)
        target['files.watcherExclude'] = watcher
        changed = True

    if changed:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"  ✅ {path} sanitized.")
    else:
        print(f"  ✅ {path} is already clean.")
EOF

# ==============================================================================
# 4. PURGE CORRUPTED VIM STATE (THE CODE 5 CRASH KILLER)
# ==============================================================================
echo -e "\n→ [2] Excising corrupted vscodevim JSON state..."
rm -rf "$HOME/Library/Application Support/Antigravity/User/globalStorage/vscodevim.vim" 2>/dev/null || true
rm -rf "$HOME/Library/Application Support/Antigravity/User/workspaceStorage/"*"/vscodevim.vim" 2>/dev/null || true
rm -rf "$HOME/.antigravity/User/globalStorage/vscodevim.vim" 2>/dev/null || true
echo "  ✅ Vim memory wiped. Extension will rebuild a clean state on next boot."

# ==============================================================================
# 5. FIX GIT ENOENT ERROR
# ==============================================================================
echo -e "\n→ [3] Pruning dead remote Git refs..."
cd product-pitch-site 2>/dev/null && git pack-refs --all --prune 2>/dev/null || true
cd ..
rm -f "product-pitch-site/.git/refs/remotes/origin/master" 2>/dev/null || true
echo "  ✅ Stale Git references pruned."

echo -e "\n🛡️ IDE CORTEX REPAIR COMPLETE. PLEASE RELOAD THE ANTIGRAVITY WINDOW."
