#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
VENV="${ROOT}/.venv"
PY="${VENV}/bin/python"

cd "${ROOT}"

echo "[1/6] Verifying canonical root..."
if [ "$(pwd -P)" != "$(cd "${ROOT}" && pwd -P)" ]; then
  echo "ERROR: Not in canonical monorepo root."
  exit 1
fi

echo "[2/6] Rebuilding venv if needed..."
if [ ! -x "${PY}" ]; then
  if command -v uv >/dev/null 2>&1; then
    uv venv "${VENV}"
  else
    python3 -m venv "${VENV}"
  fi
fi

echo "[3/6] Syncing dependencies..."
if [ -f "pyproject.toml" ]; then
  if command -v uv >/dev/null 2>&1; then
    uv sync
  else
    "${PY}" -m pip install -U pip
    if [ -f "requirements.txt" ]; then
      "${PY}" -m pip install -r requirements.txt
    fi
  fi
fi

echo "[4/6] Validating interpreter..."
"${PY}" --version
"${PY}" -c "import sys; print(sys.executable)"

echo "[5/6] Clearing stale Python extension state hints..."
echo "Now do this in VS Code:"
echo "  - Open: ${ROOT}/Monorepo-Uphillsnowball.code-workspace"
echo "  - Run: Developer: Reload Window"
echo "  - Run: Python: Select Interpreter"
echo "  - Choose: ${PY}"

echo "[6/6] Done."
