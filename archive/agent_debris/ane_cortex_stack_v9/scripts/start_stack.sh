#!/usr/bin/env bash
set -euo pipefail
docker compose up -d
echo "Start API with:"
echo "  uvicorn service.app.main:app --reload --port 8090"
