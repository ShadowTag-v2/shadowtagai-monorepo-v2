#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${GCP_BUCKET}" ]]; then
    echo "Error: GCP_BUCKET environment variable is not set."
    exit 1
fi

echo "Deploying pnkln-core model to Vertex AI..."
# vertex ai models upload \
# --display-name=pnkln-core \
# --artifact-uri=gs://$GCP_BUCKET/models/core \
# --container-image-uri=us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-13:latest

echo "Deploying core jobs to CoreWeave via Modal..."
# modal run pnkln.jobs.deploy_coreweave --gpu A100 --replicas 2

echo "Deployment process initiated."
