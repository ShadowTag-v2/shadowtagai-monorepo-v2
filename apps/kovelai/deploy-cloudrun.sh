#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════
# KovelAI — Cloud Run Deployment Script
#
# Deploys both services to Cloud Run on shadowtag-omega-v4.
# Handles: Artifact Registry, Secret Manager, Cloud Run.
# TLS/HTTPS is automatic (Google-managed certs).
# No nginx, no docker-compose, no local Docker.
#
# Usage:
#   chmod +x deploy-cloudrun.sh
#   ./deploy-cloudrun.sh
#
# Prerequisites:
#   - gcloud CLI installed & authenticated
#   - Project: shadowtag-omega-v4
# ════════════════════════════════════════════════════════════

set -euo pipefail

PROJECT_ID="shadowtag-omega-v4"
REGION="us-central1"
REPO_NAME="kovelai"
IMAGE_NAME="secure-proxy"
TAG="latest"
IMAGE_URI="us-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${TAG}"

echo "═══════════════════════════════════════════"
echo "  KovelAI Cloud Run Deployment"
echo "  Project: ${PROJECT_ID}"
echo "  Region:  ${REGION}"
echo "═══════════════════════════════════════════"

# ── Step 0: Set project ────────────────────────
echo ""
echo "► Setting active project..."
gcloud config set project "${PROJECT_ID}"

# ── Step 1: Create Artifact Registry (if needed) ──
echo ""
echo "► Ensuring Artifact Registry repo exists..."
gcloud artifacts repositories describe "${REPO_NAME}" \
  --location="${REGION}" 2>/dev/null || \
gcloud artifacts repositories create "${REPO_NAME}" \
  --repository-format=docker \
  --location="${REGION}" \
  --description="KovelAI Docker images"

# ── Step 2: Create secrets in Secret Manager ───
echo ""
echo "► Ensuring secrets exist in Secret Manager..."
for SECRET_NAME in kovelai-stripe-key kovelai-stripe-webhook kovelai-kms-secret kovelai-gemini-key; do
  gcloud secrets describe "${SECRET_NAME}" 2>/dev/null || \
  echo "⚠️  Secret '${SECRET_NAME}' not found. Create it with:"
  echo "   echo -n 'YOUR_VALUE' | gcloud secrets create ${SECRET_NAME} --data-file=-"
done

# ── Step 3: Build with Cloud Build (server-side) ──
echo ""
echo "► Building image with Cloud Build (no local Docker needed)..."
gcloud builds submit \
  --tag="${IMAGE_URI}" \
  --timeout=600 \
  --machine-type=E2_HIGHCPU_8

# ── Step 4: Deploy kovelai-api ─────────────────
echo ""
echo "► Deploying kovelai-api to Cloud Run..."
gcloud run deploy kovelai-api \
  --image="${IMAGE_URI}" \
  --region="${REGION}" \
  --platform=managed \
  --port=8080 \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=5 \
  --timeout=120 \
  --concurrency=80 \
  --cpu-throttling \
  --no-allow-unauthenticated \
  --set-env-vars="SERVICE_NAME=kovelai-api,PORT=8080" \
  --command="uvicorn" \
  --args="api.main:app,--host,0.0.0.0,--port,8080,--workers,2" \
  --set-secrets="STRIPE_SECRET_KEY=kovelai-stripe-key:latest,STRIPE_WEBHOOK_SECRET=kovelai-stripe-webhook:latest,KOVEL_KMS_SECRET=kovelai-kms-secret:latest,GOOGLE_API_KEY=kovelai-gemini-key:latest"

# ── Step 5: Deploy kovelai-agent ───────────────
echo ""
echo "► Deploying kovelai-agent to Cloud Run..."
gcloud run deploy kovelai-agent \
  --image="${IMAGE_URI}" \
  --region="${REGION}" \
  --platform=managed \
  --port=8000 \
  --memory=384Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=3 \
  --timeout=300 \
  --concurrency=40 \
  --cpu-throttling \
  --no-allow-unauthenticated \
  --set-env-vars="SERVICE_NAME=kovelai-agent,KOVELAI_PORT=8000" \
  --command="uvicorn" \
  --args="agent.kovelai_agent:app,--host,0.0.0.0,--port,8000,--workers,1" \
  --set-secrets="GOOGLE_API_KEY=kovelai-gemini-key:latest,KOVEL_KMS_SECRET=kovelai-kms-secret:latest"

# ── Step 6: Print URLs ────────────────────────
echo ""
echo "═══════════════════════════════════════════"
echo "  ✅ Deployment Complete"
echo "═══════════════════════════════════════════"
echo ""
API_URL=$(gcloud run services describe kovelai-api --region="${REGION}" --format='value(status.url)')
AGENT_URL=$(gcloud run services describe kovelai-agent --region="${REGION}" --format='value(status.url)')
echo "  API:   ${API_URL}"
echo "  Agent: ${AGENT_URL}"
echo "  Health: ${API_URL}/api/v1/health"
echo ""
echo "  TLS:   ✅ Automatic (Google-managed)"
echo "  Auth:  IAM-gated (use gcloud run services add-iam-policy-binding to add invokers)"
echo ""
echo "  To map custom domain:"
echo "    gcloud beta run domain-mappings create --service kovelai-api --domain api.kovelai.com --region ${REGION}"
echo ""
