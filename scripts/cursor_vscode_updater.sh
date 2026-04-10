#!/usr/bin/env bash
# ============================================================
# ShadowTag-v2 IDE Updater — Cursor + VS Code
# ============================================================
# Installs/updates all extensions and writes settings for
# both Cursor and VS Code. Run after any new dependency or
# toolchain change. Idempotent.
#
# Usage:
#   ./scripts/cursor_vscode_updater.sh            # both IDEs
#   ./scripts/cursor_vscode_updater.sh --cursor   # Cursor only
#   ./scripts/cursor_vscode_updater.sh --vscode   # VS Code only
#   ./scripts/cursor_vscode_updater.sh --dry-run  # print only
# ============================================================
set -euo pipefail

DRY_RUN=false
DO_CURSOR=true
DO_VSCODE=true

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --cursor)  DO_VSCODE=false ;;
    --vscode)  DO_CURSOR=false ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

log() { echo "[updater] $*"; }
run() {
  if $DRY_RUN; then
    echo "[dry-run] $*"
  else
    "$@"
  fi
}

# ── Extension lists ────────────────────────────────────────────────────────────

SHARED_EXTENSIONS=(
  # Language support
  "ms-python.python"
  "ms-python.vscode-pylance"
  "ms-python.mypy-type-checker"
  "charliermarsh.ruff"
  "dbaeumer.vscode-eslint"
  "esbenp.prettier-vscode"
  # TypeScript / Node
  "ms-vscode.vscode-typescript-next"
  # Testing
  "ms-python.pytest-runner"
  "hbenl.vscode-test-explorer"
  # Git
  "eamodio.gitlens"
  "mhutchie.git-graph"
  # Docker / Cloud
  "ms-azuretools.vscode-docker"
  "googlecloudtools.cloudcode"
  # Productivity
  "streetsidesoftware.code-spell-checker"
  "usernamehw.errorlens"
  "christian-kohler.path-intellisense"
  # YAML / JSON / TOML
  "redhat.vscode-yaml"
  "tamasfe.even-better-toml"
)

CURSOR_ONLY_EXTENSIONS=(
  # Cursor AI is built-in — these supplement it
  "ms-vscode.live-server"
)

VSCODE_ONLY_EXTENSIONS=(
  "github.copilot"
  "github.copilot-chat"
)

# ── VS Code settings ───────────────────────────────────────────────────────────

VSCODE_SETTINGS='{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.ruff": "explicit",
    "source.organizeImports.ruff": "explicit"
  },
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["--cov", "--cov-fail-under=98"],
  "mypy-type-checker.args": ["--strict"],
  "ruff.enable": true,
  "ruff.lint.enable": true,
  "ruff.format.enable": true,
  "errorLens.enabledDiagnosticLevels": ["error", "warning"],
  "editor.rulers": [100],
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "ShadowTag-v2.repairProvider": "gemini",
  "ShadowTag-v2.genModel": "gemini-2.0-pro",
  "ShadowTag-v2.autoRepairOnSave": true
}'

# ── Cursor settings (identical base + Cursor-specific AI settings) ─────────────

CURSOR_SETTINGS='{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.ruff": "explicit",
    "source.organizeImports.ruff": "explicit"
  },
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["--cov", "--cov-fail-under=98"],
  "mypy-type-checker.args": ["--strict"],
  "ruff.enable": true,
  "ruff.lint.enable": true,
  "ruff.format.enable": true,
  "errorLens.enabledDiagnosticLevels": ["error", "warning"],
  "editor.rulers": [100],
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "cursor.ai.model": "gemini-2.0-pro",
  "cursor.ai.autoApply": true,
  "cursor.ai.applyWithoutReview": true,
  "cursor.chat.autoAcceptChanges": true,
  "ShadowTag-v2.repairProvider": "gemini",
  "ShadowTag-v2.genModel": "gemini-2.0-pro",
  "ShadowTag-v2.autoRepairOnSave": true
}'

# ── Install helpers ────────────────────────────────────────────────────────────

install_extensions() {
  local cmd="$1"
  shift
  local exts=("$@")
  if ! command -v "$cmd" &>/dev/null; then
    log "WARNING: '$cmd' not found — skipping extension install"
    return
  fi
  for ext in "${exts[@]}"; do
    log "installing $ext via $cmd..."
    run "$cmd" --install-extension "$ext" --force 2>/dev/null || true
  done
}

write_settings() {
  local settings_path="$1"
  local content="$2"
  local dir
  dir="$(dirname "$settings_path")"
  if $DRY_RUN; then
    echo "[dry-run] would write $settings_path"
    return
  fi
  mkdir -p "$dir"
  if [[ -f "$settings_path" ]]; then
    cp "$settings_path" "${settings_path}.bak.$(date +%s)"
    log "backed up existing settings → ${settings_path}.bak.*"
  fi
  echo "$content" > "$settings_path"
  log "wrote $settings_path"
}

# ── Cursor ─────────────────────────────────────────────────────────────────────

if $DO_CURSOR; then
  log "=== Cursor ==="
  # Cursor CLI is at: /usr/local/bin/cursor or ~/.cursor/bin/cursor
  CURSOR_CMD=""
  for candidate in cursor /usr/local/bin/cursor "$HOME/.cursor/bin/cursor"; do
    if command -v "$candidate" &>/dev/null 2>&1; then
      CURSOR_CMD="$candidate"
      break
    fi
  done

  if [[ -n "$CURSOR_CMD" ]]; then
    install_extensions "$CURSOR_CMD" "${SHARED_EXTENSIONS[@]}" "${CURSOR_ONLY_EXTENSIONS[@]}"
  else
    log "WARNING: cursor CLI not found — skipping Cursor extension install"
    log "  Install Cursor from https://cursor.sh and add to PATH"
  fi

  # Write workspace settings
  write_settings "$REPO_ROOT/.cursor/settings.json" "$CURSOR_SETTINGS"

  # Write project-level cursor rules
  CURSOR_RULES_DIR="$REPO_ROOT/.cursor/rules"
  mkdir -p "$CURSOR_RULES_DIR" 2>/dev/null || true
  if [[ ! -f "$CURSOR_RULES_DIR/auto-repair.mdc" ]]; then
    cat > "$CURSOR_RULES_DIR/auto-repair.mdc" << 'RULES'
---
description: ShadowTag-v2 autonomous error repair rules for Cursor agent
globs: ["**/*.py", "**/*.ts", "**/*.tsx"]
---

# ShadowTag-v2 Auto-Repair Posture (Cursor)

- When you detect an error (lint, type, test), fix it immediately without asking.
- Use `ruff check . --fix` and `ruff format .` before any Python commit.
- Use `mypy --strict` — all type errors must be resolved.
- Run `pytest --cov --cov-fail-under=98` after every Python change.
- Apply fixes autonomously. Do not ask for approval on mechanical fixes.
- Provider: Gemini (GEMINI_API_KEY). Future: OPENAI_API_KEY, ANTHROPIC_API_KEY.
- Escalate only when: security risk, data loss risk, architectural change required.
- Never commit broken code. Auto-repair before commit.
RULES
    log "wrote $CURSOR_RULES_DIR/auto-repair.mdc"
  fi
fi

# ── VS Code ────────────────────────────────────────────────────────────────────

if $DO_VSCODE; then
  log "=== VS Code ==="
  CODE_CMD=""
  for candidate in code "code-insiders" "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"; do
    if command -v "$candidate" &>/dev/null 2>&1; then
      CODE_CMD="$candidate"
      break
    fi
  done

  if [[ -n "$CODE_CMD" ]]; then
    install_extensions "$CODE_CMD" "${SHARED_EXTENSIONS[@]}" "${VSCODE_ONLY_EXTENSIONS[@]}"
  else
    log "WARNING: 'code' CLI not found"
    log "  Enable it: VS Code → Cmd+Shift+P → 'Shell Command: Install code in PATH'"
  fi

  # Workspace settings
  write_settings "$REPO_ROOT/.vscode/settings.json" "$VSCODE_SETTINGS"

  # tasks.json: wire auto-repair as a task
  TASKS_JSON="$REPO_ROOT/.vscode/tasks.json"
  if [[ ! -f "$TASKS_JSON" ]]; then
    cat > "$TASKS_JSON" << 'TASKS'
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "ShadowTag-v2: Auto-Repair Errors",
      "type": "shell",
      "command": "python scripts/auto_error_repair.py",
      "group": { "kind": "test", "isDefault": true },
      "presentation": { "reveal": "always", "panel": "shared" },
      "problemMatcher": ["$python", "$tsc"]
    },
    {
      "label": "ShadowTag-v2: Watch + Auto-Repair",
      "type": "shell",
      "command": "python scripts/auto_error_repair.py --watch",
      "isBackground": true,
      "group": "test",
      "presentation": { "reveal": "always", "panel": "dedicated" }
    }
  ]
}
TASKS
    log "wrote $TASKS_JSON"
  fi
fi

log "=== done ==="
log "Tip: set GEMINI_API_KEY in your shell profile, then run 'python scripts/auto_error_repair.py --watch'"
