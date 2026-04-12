#!/bin/bash
# deploy-workers.sh - Deploy Cloudflare Workers with zero downtime

set -euo pipefail

echo "════════════════════════════════════════════════════════"
echo "  PNKLN JUDGE #6 LITE - CLOUDFLARE WORKERS DEPLOYMENT  "
echo "  Target: <50ms p99 | Cost: \$5/month base              "
echo "════════════════════════════════════════════════════════"

# Configuration
WORKER_DIR="workers/judge6-lite"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "${PROJECT_ROOT}/${WORKER_DIR}"

# Step 1: Check prerequisites
echo ""
echo "▶ PHASE 1: PREREQUISITES CHECK"
echo "───────────────────────────────"

# Check wrangler
echo -n "  Checking wrangler CLI... "
if command -v wrangler &>/dev/null; then
    WRANGLER_VERSION=$(wrangler --version 2>/dev/null || echo "unknown")
    echo "✓ ${WRANGLER_VERSION}"
else
    echo "✗ Not found"
    echo "  Installing wrangler..."
    npm install -g wrangler
fi

# Check TypeScript
echo -n "  Checking TypeScript... "
if command -v tsc &>/dev/null; then
    echo "✓"
else
    echo "Installing TypeScript..."
    npm install -D typescript
fi

# Step 2: Install dependencies
echo ""
echo "▶ PHASE 2: DEPENDENCIES"
echo "────────────────────────"

if [ ! -f "package.json" ]; then
    echo "  Creating package.json..."
    cat > package.json << 'EOF'
{
  "name": "pnkln-judge6-lite",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "wrangler dev",
    "deploy": "wrangler deploy",
    "deploy:staging": "wrangler deploy --env staging",
    "deploy:production": "wrangler deploy --env production"
  },
  "devDependencies": {
    "@cloudflare/workers-types": "^4.20241112.0",
    "typescript": "^5.0.0",
    "wrangler": "^3.0.0"
  }
}
EOF
fi

npm install

# Step 3: TypeScript configuration
echo ""
echo "▶ PHASE 3: TYPESCRIPT SETUP"
echo "────────────────────────────"

if [ ! -f "tsconfig.json" ]; then
    echo "  Creating tsconfig.json..."
    cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2021",
    "module": "ESNext",
    "lib": ["ES2021"],
    "types": ["@cloudflare/workers-types"],
    "moduleResolution": "node",
    "esModuleInterop": true,
    "strict": true,
    "skipLibCheck": true,
    "noEmit": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
EOF
fi

# Step 4: Configure secrets
echo ""
echo "▶ PHASE 4: SECRETS CONFIGURATION"
echo "─────────────────────────────────"

echo "  Checking for GOOGLE_CLOUD_TOKEN secret..."
if ! wrangler secret list 2>/dev/null | grep -q "GOOGLE_CLOUD_TOKEN"; then
    echo "  ⚠️  GOOGLE_CLOUD_TOKEN not set"
    echo ""
    echo "  To set the secret, run:"
    echo "    wrangler secret put GOOGLE_CLOUD_TOKEN"
    echo ""
    echo "  Get your token with:"
    echo "    gcloud auth print-access-token"
    echo ""
else
    echo "  ✓ GOOGLE_CLOUD_TOKEN configured"
fi

# Step 5: Create KV namespace if needed
echo ""
echo "▶ PHASE 5: KV NAMESPACE"
echo "────────────────────────"

KV_EXISTS=$(wrangler kv:namespace list 2>/dev/null | grep -c "JUDGE_KV" || true)
if [ "$KV_EXISTS" -eq 0 ]; then
    echo "  Creating KV namespace..."
    KV_ID=$(wrangler kv:namespace create "JUDGE_KV" 2>&1 | grep -oP 'id = "\K[^"]+' || true)

    if [ -n "$KV_ID" ]; then
        echo "  ✓ Created KV namespace: ${KV_ID}"
        echo ""
        echo "  ⚠️  Update wrangler.toml with this ID:"
        echo "    kv_namespaces = ["
        echo "      { binding = \"JUDGE_KV\", id = \"${KV_ID}\" }"
        echo "    ]"
    fi
else
    echo "  ✓ KV namespace exists"
fi

# Step 6: Deploy
echo ""
echo "▶ PHASE 6: DEPLOYMENT"
echo "──────────────────────"

ENV="${1:-staging}"

echo "  Deploying to ${ENV}..."
if [ "$ENV" = "production" ]; then
    wrangler deploy --env production
else
    wrangler deploy --env staging
fi

# Step 7: Verify deployment
echo ""
echo "▶ PHASE 7: VERIFICATION"
echo "────────────────────────"

WORKER_URL=$(wrangler whoami 2>/dev/null | grep -oP 'https://[^\s]+' || echo "")
if [ -z "$WORKER_URL" ]; then
    WORKER_URL="https://pnkln-judge6-lite-${ENV}.workers.dev"
fi

echo "  Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${WORKER_URL}/health" 2>/dev/null || echo "000")

if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo "  ✓ Health check passed"
else
    echo "  ⚠️  Health check returned ${HEALTH_RESPONSE}"
    echo "      URL: ${WORKER_URL}/health"
fi

# Done
echo ""
echo "════════════════════════════════════════════════════════"
echo "  DEPLOYMENT COMPLETE                                  "
echo "────────────────────────────────────────────────────────"
echo "  Worker URL: ${WORKER_URL}"
echo "  Environment: ${ENV}"
echo ""
echo "  Test with:"
echo "    curl -X POST ${WORKER_URL} \\"
echo "      -H 'Content-Type: application/json' \\"
echo "      -d '{\"content\": \"Hello world\", \"user_id\": \"test123\"}'"
echo "════════════════════════════════════════════════════════"
