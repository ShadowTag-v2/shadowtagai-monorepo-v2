#!/bin/bash
# File: scripts/setup_file_search.sh
# Purpose: Initialize RAG corpora for all 30 verticals
# Usage: ./scripts/setup_file_search.sh [--vertical VERTICAL_NAME]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-pnkln-core-gke}"
REGION="${GCP_REGION:-us-central1}"
BUCKET="${GCP_STORAGE_BUCKET:-gs://pnkln-policy-corpus}"

echo -e "${GREEN}=== Pnkln File Search Setup ===${NC}"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Bucket: $BUCKET"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is required but not installed${NC}"
    exit 1
fi

# Check if gcloud is available
if ! command -v gcloud &> /dev/null; then
    echo -e "${YELLOW}Warning: gcloud CLI not found. Skipping auth check.${NC}"
else
    # Verify authentication
    echo -e "${YELLOW}Checking GCP authentication...${NC}"
    if ! gcloud auth application-default print-access-token &> /dev/null; then
        echo -e "${RED}Error: Not authenticated with GCP${NC}"
        echo "Run: gcloud auth application-default login"
        exit 1
    fi
    echo -e "${GREEN}✓ Authenticated${NC}"
fi

# Parse arguments
SPECIFIC_VERTICAL=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --vertical)
            SPECIFIC_VERTICAL="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--vertical VERTICAL_NAME]"
            exit 1
            ;;
    esac
done

# Verticals configuration
# Format: "vertical_name:regulations"
VERTICALS=(
    "defense:ITAR,CMMC,DFARS"
    "healthcare:HIPAA,FDA,HITECH"
    "finance:FINRA,SOX,GDPR,PCI-DSS"
    "insurance:STATE_REGS,NAIC,GDPR"
    "pharma:FDA,GxP,21CFR11"
    "energy:NERC_CIP,FERC,EPA"
    "manufacturing:ISO9001,OSHA,EPA"
    "retail:PCI-DSS,GDPR,CCPA"
    "telecom:FCC,CALEA,CPNI"
    "government:FISMA,FedRAMP,NIST"
    "education:FERPA,COPPA,GDPR"
    "legal:ABA,GDPR,STATE_BAR"
    "media:COPPA,GDPR,DMCA"
    "transportation:DOT,FAA,TSA"
    "hospitality:PCI-DSS,ADA,OSHA"
    "real_estate:RESPA,TILA,FCRA"
    "agriculture:USDA,EPA,OSHA"
    "mining:MSHA,EPA,OSHA"
    "construction:OSHA,EPA,LOCAL_BUILDING"
    "biotech:FDA,NIH,CDC"
    "chemical:EPA,OSHA,REACH"
    "automotive:NHTSA,EPA,DOT"
    "aerospace:FAA,ITAR,NASA"
    "maritime:USCG,IMO,SOLAS"
    "gaming:STATE_GAMING,AML,KYC"
    "nonprofit:IRS_501C3,STATE_CHARITY,FUNDRAISING"
    "sports:NCAA,WADA,ADA"
    "environmental:EPA,NEPA,ESA"
    "logistics:DOT,TSA,CTPAT"
    "research:NIH,NSF,IRB"
)

# Create corpus setup script
setup_corpus() {
    local vertical=$1
    local regs=$2

    echo -e "${YELLOW}Setting up corpus: pnkln_${vertical}_policies${NC}"

    python3 - <<EOF
import asyncio
import sys
from pnkln_file_search.corpus.manager import CorpusManager
from pnkln_file_search.config.verticals import get_vertical_config

async def setup():
    try:
        manager = CorpusManager()
        await manager.initialize()

        # Get vertical config
        vertical_config = get_vertical_config("${vertical}")

        # Create corpus
        corpus_name = await manager.create_corpus(vertical_config)

        # Import files if they exist in GCS
        # NOTE: You'll need to upload policy PDFs to GCS first
        import_paths = ["${BUCKET}/${vertical}/*.pdf"]

        try:
            await manager.import_files(
                corpus_name,
                import_paths,
            )
            print(f"✓ Imported files for ${vertical}")
        except Exception as e:
            print(f"! No files found for ${vertical} (upload PDFs to ${BUCKET}/${vertical}/)")
            print(f"  Corpus created but empty: {corpus_name}")

        return True
    except Exception as e:
        print(f"✗ Failed to setup ${vertical}: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = asyncio.run(setup())
    sys.exit(0 if success else 1)
EOF

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Corpus setup complete: pnkln_${vertical}_policies${NC}"
    else
        echo -e "${RED}✗ Corpus setup failed: pnkln_${vertical}_policies${NC}"
        return 1
    fi
}

# Setup corpora
FAILED_COUNT=0
SUCCESS_COUNT=0

if [ -n "$SPECIFIC_VERTICAL" ]; then
    echo -e "${YELLOW}Setting up single vertical: $SPECIFIC_VERTICAL${NC}"

    # Find matching vertical config
    FOUND=false
    for vertical_config in "${VERTICALS[@]}"; do
        IFS=':' read -r vertical regs <<< "$vertical_config"
        if [ "$vertical" = "$SPECIFIC_VERTICAL" ]; then
            FOUND=true
            setup_corpus "$vertical" "$regs"
            if [ $? -eq 0 ]; then
                SUCCESS_COUNT=1
            else
                FAILED_COUNT=1
            fi
            break
        fi
    done

    if [ "$FOUND" = false ]; then
        echo -e "${RED}Error: Unknown vertical '$SPECIFIC_VERTICAL'${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Setting up all 30 verticals...${NC}"
    echo ""

    for vertical_config in "${VERTICALS[@]}"; do
        IFS=':' read -r vertical regs <<< "$vertical_config"

        if setup_corpus "$vertical" "$regs"; then
            ((SUCCESS_COUNT++))
        else
            ((FAILED_COUNT++))
        fi

        echo ""
    done
fi

# Summary
echo ""
echo -e "${GREEN}=== Setup Summary ===${NC}"
echo -e "Success: ${GREEN}$SUCCESS_COUNT${NC}"
echo -e "Failed:  ${RED}$FAILED_COUNT${NC}"
echo ""

if [ $FAILED_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ All corpora initialized successfully${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠ Some corpora failed to initialize${NC}"
    exit 1
fi
