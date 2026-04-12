#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[*] ShadowTagAI Dev Bootstrap"
echo "Repo: $REPO_ROOT"

detect_editor() {
  if [ "${CURSOR:-}" != "" ]; then
    echo "cursor"
  elif [ "${VSCODE_GIT_IPC_HANDLE:-}" != "" ]; then
    echo "vscode"
  else
    echo "unknown"
  fi
}

ensure_node() {
  if ! command -v node >/dev/null 2>&1; then
    echo "[-] node not found. Install Node 20+ first."; exit 1
  fi
}

ensure_python() {
  if ! command -v python3 >/dev/null 2>&1; then
    echo "[-] python3 not found. Install Python 3.11+ first."; exit 1
  fi
}

ensure_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "[!] docker not found. GKE simulations will be skipped."
  fi
}

# setup_antigravity_proxy function removed as mitmproxy is no longer used

setup_backend() {
  echo "[*] Setting up FastAPI backend..."
  cd "$REPO_ROOT"
  if [ ! -d ".venv" ]; then
      python3 -m venv .venv
  fi
  source .venv/bin/activate
  pip install --upgrade pip
  if [ -f "requirements.txt" ]; then
      pip install -r requirements.txt
  fi
}

setup_frontend() {
  echo "[*] Setting up Next.js frontend..."
  if [ ! -d "$REPO_ROOT/frontend" ]; then
      echo "[-] frontend directory not found. Skipping."
      return
  fi
  cd "$REPO_ROOT/frontend"
  if command -v pnpm >/dev/null 2>&1; then
    pnpm install
  else
    npm install
  fi
}

run_dev() {
  echo "[*] Starting backend + frontend dev servers..."
  cd "$REPO_ROOT"
  source .venv/bin/activate
  uvicorn app.main:app --reload --port 8000 &
  BACK_PID=$!

  if [ -d "$REPO_ROOT/frontend" ]; then
      cd "$REPO_ROOT/frontend"
      npm run dev -- --port 3000 &
      FRONT_PID=$!
      echo "[*] Backend PID: $BACK_PID, Frontend PID: $FRONT_PID"
  else
      echo "[*] Backend PID: $BACK_PID (Frontend skipped)"
  fi

  wait $BACK_PID
}

case "${1:-}" in
  setup-all)
    ensure_node
    ensure_python
    ensure_docker
    # setup_antigravity_proxy call removed    setup_backend
    setup_frontend
    ;;
  run-dev)
    run_dev
    ;;
  *)
    echo "Usage: $0 {setup-all|run-dev}"
    ;;
esac
