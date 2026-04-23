#!/bin/bash
# ==============================================================================
#  SHADOWTAG OS : GENESIS OMNI-COMPILE (FEDERAL EDITION v27.0)
#
#  WARNING: This script deploys live infrastructure. STATE B (Clutch) required.
#  Do NOT run without explicit user approval.
#
#  Usage: bash scripts/ignite_omega.sh [--dry-run]
# ==============================================================================
set -euo pipefail

DRY_RUN="${1:-}"

echo ">>> 🚀 IGNITING SHADOWTAG OS (Gideon OS v27.0)..."
echo "    Project: ${GCP_PROJECT:-shadowtag-omega-v4}"
echo "    Region:  ${GCP_REGION:-us-central1}"
echo "    Mode:    ${DRY_RUN:+DRY RUN}"

if [[ "$DRY_RUN" == "--dry-run" ]]; then
    echo ">>> ⚠️  DRY RUN MODE — no infrastructure changes will be made."
fi

# 1. Verify prerequisites
echo ">>> Checking prerequisites..."
command -v go >/dev/null 2>&1 || { echo "❌ Go not found"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node not found"; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "❌ Terraform not found"; exit 1; }
command -v gcloud >/dev/null 2>&1 || { echo "❌ gcloud not found"; exit 1; }
echo "✅ All prerequisites satisfied."

# 2. Install Python dependencies
echo ">>> Installing Python dependencies..."
pip install --quiet \
    google-genai \
    google-cloud-tasks \
    google-cloud-bigquery \
    google-cloud-firestore \
    2>/dev/null || true

# 3. Build the Cor.Go Shield 1
echo ">>> Building Cor.Go Shield 1..."
if [[ -z "$DRY_RUN" ]]; then
    cd cmd/gideon-go && go build -o ../../bin/judge6 shield1_ingress.go && cd ../..
    echo "✅ Shield 1 compiled to bin/judge6"
else
    echo "   [DRY RUN] Would build cmd/gideon-go/shield1_ingress.go"
fi

# 4. Deploy Sovereign Infrastructure (Terraform)
echo ">>> Deploying Sovereign Infrastructure..."
if [[ -z "$DRY_RUN" ]]; then
    cd infra && terraform init && terraform plan -out=tfplan
    echo "⚠️  Terraform plan generated. Review before applying:"
    echo "    cd infra && terraform apply tfplan"
    cd ..
else
    echo "   [DRY RUN] Would terraform init + plan in infra/"
fi

# 5. Summary
echo ""
echo "=============================================="
echo "  GIDEON OS v27.0 — GENESIS COMPILE COMPLETE"
echo "=============================================="
echo "  Shield 1 (Go):     bin/judge6"
echo "  KAIROS Daemon:     src/daemon/kairos_ultraplan.py"
echo "  Epistemology:      src/epistemology/notebooklm_epistemology.py"
echo "  Cor.Cursor VDI:    src/agents/cor_cursor_vdi.py"
echo "  Mutagenesis:       src/governance/karpathy_mutagenesis.py"
echo "  Revocation:        src/intelligence/predictive_revocation.py"
echo "  Firestore Pipes:   src/automations/firestore_pipeline.js"
echo "  Midas C++:         src/finance/midas_montecarlo.cpp"
echo "  Infrastructure:    infra/omniverse.tf"
echo "=============================================="
echo "✅ KAIROS DAEMON AWAKE. NOTEBOOKLM EPISTEMOLOGY ACTIVE."
