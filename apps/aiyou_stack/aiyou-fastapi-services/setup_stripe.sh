#!/bin/bash
set -e

echo '🚀 Setting up Stripe integration...'

# Install dependencies
echo '📦 Installing Stripe SDK...'
pip3 install stripe python-dotenv fastapi

# Create directories
mkdir -p scripts api/routes public database

echo '✅ Setup complete! Next steps:'
echo '1. Get Stripe API keys from https://dashboard.stripe.com'
echo '2. Add to .env: STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY'
echo '3. Run: python3 scripts/setup_stripe_products.py'
echo '4. Add price IDs to .env'
echo '5. Start server and test /public/pricing.html'
