#!/bin/bash
set -e

# ONE-CLICK DEPLOYMENT: STAGE 2 (INFERENCE CORE)
# Mission: Deploy vLLM with Gemini Adapter and Judge #6 Sidecar.

# Ensure we are in the script's directory so relative paths work
cd "$(dirname "$0")"

echo "🚀 PNKLN STAGE 2: INITIATING INFERENCE CORE..."

# 1. Credentials
echo "🔑 Getting Cluster Credentials..."
gcloud container clusters get-credentials pnkln-foundation --region us-central1

# 2. Namespace Setup
echo "📦 Creating Namespaces..."
kubectl create namespace gke-inference-system --dry-run=client -o yaml | kubectl apply -f -

# 3. Secret Management (Simulated for Bootstrap)
# In production, use Workload Identity/Secret Manager.
echo "🔐 Checking for Hugging Face Token..."
if ! kubectl get secret hf-token -n gke-inference-system > /dev/null 2>&1; then
    echo "⚠️ Secret 'hf-token' not found."
    echo "Please create it manually:"
    echo "kubectl create secret generic hf-token --from-literal=token=YOUR_HF_TOKEN -n gke-inference-system"
    # Proceeding, but deployment may fail pulling private models
fi

# 4. Deploy vLLM + Judge Sidecar
echo "🧠 Deploying vLLM + Judge #6..."
kubectl apply -f ../k8s/vllm-gemini.yaml

# 5. Validation Gate (SLA Check)
echo "⏱ Waiting for Pods to be Ready..."
kubectl wait --for=condition=ready pod -l app=vllm-gemini -n gke-inference-system --timeout=300s

echo "🔬 Validating Judge Integration..."
# Simple check if sidecar is running
POD_NAME=$(kubectl get pod -l app=vllm-gemini -n gke-inference-system -o jsonpath="{.items[0].metadata.name}")
JUDGE_Container=$(kubectl get pod $POD_NAME -n gke-inference-system -o jsonpath="{.spec.containers[?(@.name=='judge-enforcer')].name}")

if [ "$JUDGE_Container" == "judge-enforcer" ]; then
    echo "✅ GATE PASSED: Judge Sidecar is active."
    echo "🚀 Inference Core is LIVE."
else
    echo "❌ GATE FAILED: Judge Sidecar missing."
    exit 1
fi
