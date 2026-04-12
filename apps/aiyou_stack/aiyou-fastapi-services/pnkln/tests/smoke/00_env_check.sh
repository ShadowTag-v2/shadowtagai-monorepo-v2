#!/usr/bin/env bash
set -euo pipefail

echo "[pnkln][smoke] Environment check"
python3 --version
pip3 --version
which gcloud || echo "gcloud not found (ok if not using GCP APIs here)"
echo "[pnkln][smoke] OK"
