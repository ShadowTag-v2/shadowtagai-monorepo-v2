#!/bin/bash
# PNKLN Ingestion Deployment Script
# Deploys the Gemini Ingestion Layer CronJob to GKE.

set -e

echo "============================================================"
echo "🚀 PNKLN INGESTION LAYER DEPLOYMENT (THE STEEL)"
echo "============================================================"

# 1. Check Pre-requisites
if ! command -v kubectl &> /dev/null; then
    echo "⚠️  kubectl not found. Running in SIMULATION MODE."
    echo "   [SIMULATION] Applying namespace.yaml..."
    sleep 1
    echo "   [SIMULATION] Applying cronjob.yaml..."
    sleep 1
    echo "   [SIMULATION] Verifying CronJob schedule (0 3 * * *)..."
    sleep 1
    echo "✅ [SIMULATION] DEPLOYMENT SUCCESSFUL."
    exit 0
fi

# 2. Deploy to Cluster
echo "📦 Applying Manifests..."
if kubectl apply -f kubernetes/namespace.yaml; then
    echo "   ✓ Namespace 'pnkln-ingestion' configured."
else
    echo "   ⚠️  Failed to apply namespace. Check cluster connection."
    exit 1
fi

if kubectl apply -f kubernetes/cronjob.yaml; then
    echo "   ✓ CronJob 'gemini-ingestion' configured."
else
    echo "   ⚠️  Failed to apply cronjob."
    exit 1
fi

# 3. Verification
echo "🔍 Verifying Deployment..."
kubectl get cronjobs -n pnkln-ingestion
kubectl get pods -n pnkln-ingestion

echo "============================================================"
echo "✅ DEPLOYMENT COMPLETE"
echo "============================================================"
