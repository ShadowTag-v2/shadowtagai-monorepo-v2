#!/usr/bin/env bash
# Sovereign State Protocol — Unified Local Launcher
# Frontend: http://localhost:3000  |  Backend: http://localhost:8080
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

echo "=== IGNITE SOVEREIGN STATE ==="
echo "Repo: $REPO_ROOT"

# Verify we're on the right repo
CURRENT_TAG=$(git describe --tags --exact-match 2>/dev/null || echo "untagged")
echo "Current state: $CURRENT_TAG"

# Kill anything already on these ports
lsof -ti :3000 | xargs kill -9 2>/dev/null || true
lsof -ti :8080 | xargs kill -9 2>/dev/null || true
sleep 1

# Backend (FastAPI)
BACKEND_DIR=""
for candidate in "apps/aiyou_stack/aiyou-fastapi-services" "apps/counselconduit/backend" "apps/aiyou_stack/Pipeline"; do
  if [[ -f "$REPO_ROOT/$candidate/main.py" || -f "$REPO_ROOT/$candidate/app/main.py" ]]; then
    BACKEND_DIR="$REPO_ROOT/$candidate"
    break
  fi
done

if [[ -n "$BACKEND_DIR" ]]; then
  echo "[Backend] Starting FastAPI at $BACKEND_DIR on :8080..."
  cd "$BACKEND_DIR"
  if [[ -f "$REPO_ROOT/.venv/bin/uvicorn" ]]; then
    "$REPO_ROOT/.venv/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8080 --reload &
  else
    uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload &
  fi
  BACKEND_PID=$!
  echo "[Backend] PID: $BACKEND_PID"
  cd "$REPO_ROOT"
else
  echo "[Backend] No main.py found — skipping backend launch."
fi

# Frontend (Next.js)
FRONTEND_DIR=""
for candidate in "apps/counselconduit" "apps/counselconduit/frontend" "apps/aiyou_stack/nascent-apollo"; do
  if [[ -f "$REPO_ROOT/$candidate/package.json" ]]; then
    FRONTEND_DIR="$REPO_ROOT/$candidate"
    break
  fi
done

if [[ -n "$FRONTEND_DIR" ]]; then
  echo "[Frontend] Starting Next.js at $FRONTEND_DIR on :3000..."
  cd "$FRONTEND_DIR"
  npm run dev &
  FRONTEND_PID=$!
  echo "[Frontend] PID: $FRONTEND_PID"
  cd "$REPO_ROOT"
else
  echo "[Frontend] No package.json found — skipping frontend launch."
fi

echo ""
echo "=== SOVEREIGN STATE LIVE ==="
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8080"
echo ""
echo "To stop: ./scripts/finish_changes.sh"
echo "To reset: git reset --hard SOVEREIGN_GOLD_MASTER && git clean -fd"

# Keep script alive so Ctrl+C kills children
wait
