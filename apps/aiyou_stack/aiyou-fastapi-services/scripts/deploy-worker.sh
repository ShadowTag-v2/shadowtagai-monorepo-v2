#!/bin/bash
# PNKLN Judge 6 Lite - Cloudflare Worker Deployment Script
# Target: Ship in 30 minutes

set -euo pipefail

echo "════════════════════════════════════════════════════════"
echo "  PNKLN JUDGE #6 LITE - CLOUDFLARE WORKER DEPLOYMENT   "
echo "  Target: <50ms p99 latency | Cost: $5/month           "
echo "════════════════════════════════════════════════════════"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
WORKER_DIR="cloudflare-worker"
WORKER_NAME="pnkln-judge"

# Step 1: Check prerequisites
echo "▶ Step 1: Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js not found. Install from https://nodejs.org${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Node.js $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} npm $(npm --version)"

# Step 2: Install Wrangler CLI
echo ""
echo "▶ Step 2: Installing Wrangler CLI..."

if ! command -v wrangler &> /dev/null; then
    echo "Installing wrangler globally..."
    npm install -g wrangler
else
    echo -e "${GREEN}✓${NC} Wrangler already installed"
fi

# Verify wrangler
wrangler --version

# Step 3: Login to Cloudflare
echo ""
echo "▶ Step 3: Cloudflare authentication..."
echo -e "${YELLOW}This will open a browser for authentication.${NC}"
echo -n "Continue? (y/n): "
read -r CONTINUE

if [[ "$CONTINUE" != "y" ]]; then
    echo "Deployment cancelled."
    exit 0
fi

wrangler login

# Step 4: Navigate to worker directory
echo ""
echo "▶ Step 4: Preparing worker for deployment..."
cd "$WORKER_DIR"

# Verify wrangler.toml exists
if [ ! -f "wrangler.toml" ]; then
    echo -e "${RED}✗ wrangler.toml not found in $WORKER_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Configuration found"

# Step 5: Set secrets
echo ""
echo "▶ Step 5: Configuring secrets..."
echo -e "${YELLOW}You'll need:${NC}"
echo "  1. Anthropic API key (get from: https://console.anthropic.com)"
echo "  2. Google Cloud token (optional - for Vertex AI integration)"
echo ""

echo -n "Set ANTHROPIC_API_KEY? (y/n): "
read -r SET_ANTHROPIC

if [[ "$SET_ANTHROPIC" == "y" ]]; then
    echo "Enter your Anthropic API key:"
    wrangler secret put ANTHROPIC_API_KEY
fi

echo -n "Set GOOGLE_CLOUD_TOKEN? (y/n): "
read -r SET_GOOGLE

if [[ "$SET_GOOGLE" == "y" ]]; then
    echo "Enter your Google Cloud token:"
    wrangler secret put GOOGLE_CLOUD_TOKEN
fi

# Step 6: Deploy worker
echo ""
echo "▶ Step 6: Deploying to Cloudflare Workers..."
echo -e "${YELLOW}This will make your worker live on Cloudflare's edge network.${NC}"
echo ""

wrangler deploy

# Step 7: Test deployment
echo ""
echo "▶ Step 7: Testing deployment..."

# Get worker URL
WORKER_URL=$(wrangler deployments list 2>/dev/null | grep -oP 'https://[^\s]+' | head -1 || echo "")

if [ -z "$WORKER_URL" ]; then
    echo -e "${YELLOW}Could not automatically detect worker URL.${NC}"
    echo "Check your Cloudflare dashboard for the worker URL."
else
    echo -e "${GREEN}✓${NC} Worker deployed at: $WORKER_URL"

    # Test health check
    echo ""
    echo "Testing health endpoint..."
    curl -s "$WORKER_URL" | jq .

    # Test judge endpoint
    echo ""
    echo "Testing judge endpoint with sample request..."
    curl -X POST "$WORKER_URL" \
        -H "Content-Type: application/json" \
        -d '{
            "content": "How do I build a login page?",
            "userId": "test-user"
        }' | jq .
fi

# Step 8: Success summary
echo ""
echo "════════════════════════════════════════════════════════"
echo "  DEPLOYMENT COMPLETE!                                  "
echo "════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}✓${NC} Worker deployed: $WORKER_NAME"
echo -e "${GREEN}✓${NC} Edge locations: 195+ cities globally"
echo -e "${GREEN}✓${NC} Target latency: <50ms p99"
echo ""
echo "NEXT STEPS:"
echo "1. Update landing page with worker URL"
echo "2. Test with various content types"
echo "3. Monitor latency in Cloudflare dashboard"
echo "4. Start beta customer outreach!"
echo ""
echo "API DOCUMENTATION:"
echo "  GET  $WORKER_URL       - Health check"
echo "  POST $WORKER_URL       - Judge content"
echo ""
echo "Example request:"
echo '  curl -X POST $WORKER_URL \'
echo '    -H "Content-Type: application/json" \'
echo '    -d '"'"'{"content": "test content", "userId": "user123"}'"'"
echo ""
echo "════════════════════════════════════════════════════════"
