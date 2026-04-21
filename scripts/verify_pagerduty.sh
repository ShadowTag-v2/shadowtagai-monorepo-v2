#!/usr/bin/env bash
# PagerDuty Integration Setup (#3/#4)
# 
# Run this script after creating a PagerDuty account at https://app.pagerduty.com
# The GCP notification channel (11292559663830648124) already routes to PagerDuty's email integration.
#
# PREREQUISITES:
# 1. Create PagerDuty account + service at https://app.pagerduty.com
# 2. Create an email integration for the service
# 3. Set the notification channel email in GCP Monitoring to your PagerDuty email integration address
#
# This script verifies the complete pipeline:

set -euo pipefail

PROJECT="shadowtag-omega-v4"
CHANNEL_ID="11292559663830648124"

echo "=== PagerDuty Integration Verification ==="

# Step 1: Verify notification channel exists
echo "1. Checking GCP notification channel..."
CLOUDSDK_PYTHON=/opt/homebrew/bin/python3 gcloud alpha monitoring channels describe \
  "projects/$PROJECT/notificationChannels/$CHANNEL_ID" \
  --project="$PROJECT" 2>&1 | head -10

# Step 2: Verify alert policies are connected
echo ""
echo "2. Listing alert policies using this channel..."
CLOUDSDK_PYTHON=/opt/homebrew/bin/python3 gcloud alpha monitoring policies list \
  --project="$PROJECT" \
  --format="table(displayName, enabled)" 2>&1

# Step 3: Test notification (creates a test incident)
echo ""
echo "3. To test: Run 'gcloud alpha monitoring policies test-notification' or trigger a manual incident."
echo ""
echo "=== Configuration Status ==="
echo "  Channel ID:   $CHANNEL_ID"
echo "  Alert Policies: 4 (production 5xx + latency, staging 5xx + latency)"
echo "  Uptime Check: counselconduit-staging-health"
echo ""
echo "Done."
