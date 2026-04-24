#!/usr/bin/env bash
set -euo pipefail

echo "[ruff] linting Python..."
ruff check . --fix

echo "[ruff] formatting Python..."
ruff format .

echo "[ruff] complete"
