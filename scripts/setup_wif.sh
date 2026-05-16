#!/bin/bash
set -e
PROJECT="shadowtag-omega-v4"
echo "Configuring Enterprise Workload Identity Federation (ADC) for $PROJECT..."
gcloud iam service-accounts create antigravity-stitch-bot --description="Claude 4.6 Autonomous Orchestrator" --project=$PROJECT || true
gcloud projects add-iam-policy-binding $PROJECT \
    --member="serviceAccount:antigravity-stitch-bot@$PROJECT.iam.gserviceaccount.com" \
    --role="roles/jules.mcpInvoker" || true
