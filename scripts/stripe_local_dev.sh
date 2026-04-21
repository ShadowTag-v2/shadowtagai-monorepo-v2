#!/usr/bin/env bash
# Stripe Webhook Local Development Setup
# Forwards Stripe webhooks to local CounselConduit server
#
# Prerequisites:
#   brew install stripe/stripe-cli/stripe
#   stripe login
#
# Usage:
#   ./scripts/stripe_local_dev.sh [port]

set -euo pipefail

PORT="${1:-8000}"
ENDPOINT="http://localhost:${PORT}/webhooks/stripe"

echo "🔗 Forwarding Stripe webhooks to ${ENDPOINT}"
echo "📌 Events: checkout.session.completed, customer.subscription.updated,"
echo "   account.updated, invoice.paid, customer.subscription.deleted"
echo ""

stripe listen \
  --forward-to "${ENDPOINT}" \
  --events checkout.session.completed,customer.subscription.updated,account.updated,invoice.paid,customer.subscription.deleted \
  --log-level info
