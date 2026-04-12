#!/bin/bash
# ============================================================================
# PNKLN CORE STACK - FILE SEARCH CORPUS INITIALIZATION
# ============================================================================
# Purpose: Initialize Vertex AI RAG corpora for all 30 verticals
# Usage: ./setup_file_search.sh --project PROJECT_ID --region REGION
# ============================================================================

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ID="${PROJECT_ID:-pnkln-core-gke}"
REGION="${REGION:-us-central1}"
BUCKET_PREFIX="pnkln-policy-corpus"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================================
# FUNCTIONS
# ============================================================================

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Initialize Vertex AI File Search RAG corpora for Pnkln Core Stack

OPTIONS:
    --project PROJECT_ID    GCP project ID (default: pnkln-core-gke)
    --region REGION         GCP region (default: us-central1)
    --help                  Show this help message

EXAMPLES:
    $0 --project my-project --region us-central1
    PROJECT_ID=my-project REGION=us-west1 $0
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --project)
            PROJECT_ID="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# ============================================================================
# PREREQUISITES CHECK
# ============================================================================

log_info "Checking prerequisites..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    log_error "gcloud CLI not found. Please install: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    log_error "python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check authentication
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    log_error "No active gcloud authentication. Run: gcloud auth login"
    exit 1
fi

log_info "Setting project to: $PROJECT_ID"
gcloud config set project "$PROJECT_ID"

# ============================================================================
# INSTALL PYTHON DEPENDENCIES
# ============================================================================

log_info "Installing Python dependencies..."

python3 -m pip install --quiet --upgrade \
    google-cloud-aiplatform \
    google-cloud-storage \
    google-auth

# ============================================================================
# VERTICALS CONFIGURATION
# ============================================================================

declare -A VERTICALS=(
    ["defense"]="ITAR,CMMC,NISPOM"
    ["healthcare"]="HIPAA,FDA_21_CFR_Part_11,HITECH"
    ["finance"]="FINRA,SOX,GDPR,PCI_DSS"
    ["insurance"]="State_Insurance_Regs,NAIC,SOX"
    ["pharmaceuticals"]="FDA_GxP,EMA,21_CFR_Part_11"
    ["biotechnology"]="FDA,CLIA,CAP"
    ["energy"]="NERC_CIP,FERC,EPA"
    ["telecommunications"]="FCC,CALEA,CPNI"
    ["aviation"]="FAA_Part_121,EASA,TSA"
    ["maritime"]="IMO,SOLAS,MARPOL"
    ["manufacturing"]="ISO_9001,OSHA,EPA"
    ["automotive"]="IATF_16949,ISO_26262,NHTSA"
    ["retail"]="PCI_DSS,CPSC,FTC"
    ["education"]="FERPA,COPPA,HIPAA"
    ["government"]="FedRAMP,FISMA,NIST_800_53"
    ["legal"]="ABA_Model_Rules,State_Bar_Regs,GDPR"
    ["real_estate"]="RESPA,TILA,Fair_Housing"
    ["hospitality"]="PCI_DSS,ADA,OSHA"
    ["media"]="FCC,COPPA,DMCA"
    ["agriculture"]="USDA,EPA,FDA"
    ["construction"]="OSHA,EPA,Building_Codes"
    ["logistics"]="DOT,FMCSA,TSA"
    ["chemicals"]="EPA,OSHA,REACH"
    ["mining"]="MSHA,EPA,OSHA"
    ["technology"]="GDPR,CCPA,SOC_2"
    ["cybersecurity"]="NIST_CSF,ISO_27001,SOC_2"
    ["consulting"]="SOC_2,ISO_9001,GDPR"
    ["nonprofit"]="IRS_501c3,State_Charity_Regs,GDPR"
    ["gaming"]="Gaming_Commission,AML,KYC"
    ["cannabis"]="State_Cannabis_Regs,FinCEN,IRS_280E"
)

# ============================================================================
# CREATE RAG CORPORA
# ============================================================================

log_info "Creating RAG corpora for ${#VERTICALS[@]} verticals..."

PYTHON_SCRIPT=$(cat <<'PYTHON_EOF'
import sys
from google.cloud import aiplatform
from vertexai.preview import rag
import json

def create_corpus(project_id, region, vertical, regulations):
    """Create a RAG corpus for a vertical"""
    try:
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=region)

        # Create corpus
        corpus_name = f"pnkln_{vertical}_policies"

        # Check if corpus already exists
        try:
            existing_corpora = rag.list_corpora()
            for corpus in existing_corpora:
                if corpus.display_name == corpus_name:
                    print(f"✓ Corpus already exists: {corpus_name}")
                    return corpus.name
        except Exception:
            pass

        # Create new corpus
        corpus = rag.create_corpus(
            display_name=corpus_name,
            description=f"Regulatory + org policies for {vertical}: {regulations}"
        )

        print(f"✓ Created corpus: {corpus_name}")
        return corpus.name

    except Exception as e:
        print(f"✗ Failed to create corpus for {vertical}: {str(e)}", file=sys.stderr)
        return None

if __name__ == "__main__":
    project_id = sys.argv[1]
    region = sys.argv[2]
    vertical = sys.argv[3]
    regulations = sys.argv[4]

    corpus_name = create_corpus(project_id, region, vertical, regulations)

    if corpus_name:
        sys.exit(0)
    else:
        sys.exit(1)
PYTHON_EOF
)

CREATED=0
FAILED=0

for vertical in "${!VERTICALS[@]}"; do
    regulations="${VERTICALS[$vertical]}"

    log_info "Processing vertical: $vertical (regulations: $regulations)"

    if echo "$PYTHON_SCRIPT" | python3 - "$PROJECT_ID" "$REGION" "$vertical" "$regulations"; then
        ((CREATED++))
    else
        ((FAILED++))
        log_warn "Failed to create corpus for: $vertical"
    fi
done

# ============================================================================
# SUMMARY
# ============================================================================

cat <<EOF

═══════════════════════════════════════════════════════════════
FILE SEARCH SETUP COMPLETE
═══════════════════════════════════════════════════════════════

Project:  $PROJECT_ID
Region:   $REGION

Results:
  ✓ Created:  $CREATED corpora
  ✗ Failed:   $FAILED corpora

Next Steps:

1. Upload policy documents to GCS buckets:
   gsutil cp your-policy.pdf gs://${BUCKET_PREFIX}-{vertical}/regulatory/

2. Import files into RAG corpora:
   Use the corpus_import.py script:
   python3 scripts/corpus_import.py --vertical defense --path gs://${BUCKET_PREFIX}-defense/regulatory/

3. Configure GKE workloads to use File Search:
   See: k8s-manifests/deployment-example.yaml

4. Monitor performance:
   gcloud monitoring dashboards list --project=$PROJECT_ID

═══════════════════════════════════════════════════════════════
EOF

exit 0
