#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-shadowtag-omega-v4}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
MODEL="${GEMINI_MODEL:-gemini-3.1-flash-lite-preview}"

echo "[vertex_bootstrap] project=$PROJECT_ID region=$REGION model=$MODEL"

gcloud services enable aiplatform.googleapis.com compute.googleapis.com >/dev/null 2>&1 || true

echo "[vertex_bootstrap] done"
