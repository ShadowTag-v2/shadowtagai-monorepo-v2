#!/bin/bash
# PNKLN Judge 6 - Landing Page Deployment Script
# Deploy to Cloudflare Pages

set -euo pipefail

echo "════════════════════════════════════════════════════════"
echo "  PNKLN JUDGE - LANDING PAGE DEPLOYMENT                "
echo "  Target: Cloudflare Pages                             "
echo "════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

LANDING_DIR="landing-page"
PROJECT_NAME="pnkln-judge-landing"

echo "▶ Step 1: Checking prerequisites..."

if ! command -v wrangler &> /dev/null; then
    echo "Installing wrangler..."
    npm install -g wrangler
fi

echo -e "${GREEN}✓${NC} Wrangler ready"

echo ""
echo "▶ Step 2: Deploying to Cloudflare Pages..."
cd "$LANDING_DIR"

wrangler pages deploy . --project-name="$PROJECT_NAME"

echo ""
echo "════════════════════════════════════════════════════════"
echo "  LANDING PAGE DEPLOYED!                               "
echo "════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}✓${NC} Your landing page is live!"
echo ""
echo "NEXT STEPS:"
echo "1. Update the form submission endpoint in index.html"
echo "2. Add analytics (Google Analytics, Plausible, etc.)"
echo "3. Set up email capture (HubSpot, Mailchimp, etc.)"
echo "4. Launch on Product Hunt!"
echo ""
