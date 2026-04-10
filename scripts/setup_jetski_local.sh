#!/usr/bin/env bash
# Sovereign State Protocol — Jetski Browser Automation Setup
# Installs Playwright + Chromium for headless browser control
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

echo "=== JETSKI PROTOCOL SETUP ==="

# Install playwright Python package
if [[ -f "$REPO_ROOT/.venv/bin/pip" ]]; then
  PIP="$REPO_ROOT/.venv/bin/pip"
else
  PIP="pip"
fi

echo "[1/3] Installing playwright..."
$PIP install playwright --quiet

# Install browser binaries
echo "[2/3] Installing Chromium browser binary..."
if [[ -f "$REPO_ROOT/.venv/bin/playwright" ]]; then
  "$REPO_ROOT/.venv/bin/playwright" install chromium
else
  python -m playwright install chromium
fi

# Verify
echo "[3/3] Verifying installation..."
if python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')" 2>/dev/null; then
  echo "Playwright: OK"
else
  echo "WARNING: playwright import failed — check your Python environment"
fi

echo ""
echo "=== JETSKI READY ==="
echo "Identity: Jetski (Browser Sub-Agent)"
echo "Capabilities: Navigate, Click, Read DOM, Screenshot"
echo ""
echo "Usage:"
echo "  from playwright.sync_api import sync_playwright"
echo "  with sync_playwright() as p:"
echo "      browser = p.chromium.launch(headless=True)"
echo "      page = browser.new_page()"
echo "      page.goto('https://...')"
