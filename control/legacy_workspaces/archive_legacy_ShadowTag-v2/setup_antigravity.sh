#!/bin/bash
# Antigravity Quick Setup Script
# ================================
# Configures Gemini API failover and activates FlyingMonkeys

set -e

echo "🚀 Antigravity Quick Setup"
echo "=========================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env 2>/dev/null || touch .env
fi

# Function to prompt for API keys
setup_gemini_keys() {
    echo ""
    echo "🔑 Gemini API Configuration"
    echo "----------------------------"
    echo ""
    echo "You can configure Gemini API in two ways:"
    echo "  1. Multiple API keys (recommended for quota management)"
    echo "  2. Single API key"
    echo "  3. Vertex AI only (requires GCP_PROJECT_ID)"
    echo ""

    read -p "How many Gemini API keys do you have? (0 for Vertex AI only): " key_count

    if [ "$key_count" -gt 0 ]; then
        keys=()
        for ((i=1; i<=key_count; i++)); do
            read -p "Enter API key #$i: " key
            keys+=("$key")
        done

        # Join keys with commas
        api_keys_str=$(IFS=,; echo "${keys[*]}")

        # Update .env
        if grep -q "GEMINI_API_KEYS=" .env; then
            sed -i.bak "s|GEMINI_API_KEYS=.*|GEMINI_API_KEYS=$api_keys_str|" .env
        else
            echo "GEMINI_API_KEYS=$api_keys_str" >> .env
        fi

        echo "✅ Configured $key_count API keys for rotation"
    else
        echo "⚠️  No API keys configured. Vertex AI fallback will be used."
    fi

    # GCP Project ID
    echo ""
    read -p "Enter GCP Project ID (for Vertex AI fallback, or press Enter to skip): " project_id

    if [ -n "$project_id" ]; then
        if grep -q "GCP_PROJECT_ID=" .env; then
            sed -i.bak "s|GCP_PROJECT_ID=.*|GCP_PROJECT_ID=$project_id|" .env
        else
            echo "GCP_PROJECT_ID=$project_id" >> .env
        fi
        echo "✅ Vertex AI fallback configured"
    fi
}


# Main setup flow
echo "This script will configure:"
echo "  • Gemini API failover (multi-key rotation)"
echo "  • Vertex AI fallback"
echo "  • FlyingMonkeys 650-agent swarm"
echo ""

read -p "Proceed with setup? (y/n): " proceed

if [ "$proceed" != "y" ]; then
    echo "Setup cancelled."
    exit 0
fi

# Run setup
setup_gemini_keys
setup_anthropic_key

# Clean up backup files
rm -f .env.bak

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "  1. Start FlyingMonkeys: ./run_flyingmonkeys_api.sh"
echo "  2. Check status: python3 antigravity_status.py"
echo "  3. View docs: http://localhost:8888/docs"
echo ""
echo "🔍 Test Gemini failover:"
echo "  python3 -c 'from src.aiyou.services.gemini_failover import get_failover_client; print(get_failover_client().health_check())'"
echo ""
