#!/bin/bash
# Run Enterprise Compliance API
# "AI that passes audit" - Wedge 1 against Perplexity

cd "$(dirname "$0")"

echo "🏢 Starting AiYou Enterprise Compliance API..."
echo "   Server: http://localhost:8889"
echo "   Docs:   http://localhost:8889/docs"
echo ""
echo "   Competitive Advantages:"
echo "   - 21-layer governance (vs basic safety)"
echo "   - 97% cheaper execution"
echo "   - 6 regulatory frameworks"
echo "   - Blockchain-verified audit"
echo ""

python3 -m uvicorn api.enterprise_compliance_api:app --host 0.0.0.0 --port 8889 --reload
