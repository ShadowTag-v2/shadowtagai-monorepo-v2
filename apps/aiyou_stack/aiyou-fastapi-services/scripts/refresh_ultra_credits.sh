#!/bin/bash
set -e

# ==============================================================================
# 🔄 ULTRA SUBSCRIPTION KEEP-ALIVE
# ==============================================================================
# Automates the "Burn Check" sequence to ensure the Ultra AI subscription 
# remains active and credentials are fresh.
# ==============================================================================

echo ">>> 🔥 STARTING ULTRA REFRESH CYCLE..."
timestamp=$(date +"%T")

# 0. SETUP PATHS (Directory Agnostic)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
KEY_FILE="$PROJECT_ROOT/secrets/robot_key.json"

if [ -f "$KEY_FILE" ]; then
    echo "[$timestamp] 🤖 HEADLESS MODE DETECTED. Activating Service Account..."
    
    # Activate Service Account (No Browser!)
    gcloud auth activate-service-account --key-file=$KEY_FILE
    
    # Set ADC to this key
    export GOOGLE_APPLICATION_CREDENTIALS=$KEY_FILE
    # Note: We also set it in gcloud config to persist for this shell session implications
    gcloud config set account $(jq -r .client_email $KEY_FILE)
    gcloud auth application-default set-quota-project $PROJECT_ID
    
    echo ">>> ✅ REFRESH COMPLETE (ROBOT). System is autonomous."
    exit 0
fi

# FALLBACK: INTERACTIVE MODE
echo "[$timestamp] ⚠️  No Robot Key found. Checking current session..."

# 0.5 CHECK EXISTING AUTH (Smart Skip)
if gcloud auth print-access-token >/dev/null 2>&1; then
    echo "[$timestamp] ✅ Valid Credentials Detected. Skipping Browser Login."
else
    echo "[$timestamp] 🔴 Credentials Invalid. Triggering Browser Login..."
    
    # 1. Revoke stale ADC (Force clean slate)
    echo "[$timestamp] 1. Revoking Application Default Credentials..."
    gcloud auth application-default revoke --quiet || true
    
    # 2. Login ADC (Triggers browser flow if token invalid, otherwise refreshes)
    echo "[$timestamp] 2. Refreshing Application Default Credentials..."
    gcloud auth application-default login --disable-quota-project
    
    # 3. Update ADC with User Credentials (The "Ultra" Link)
    echo "[$timestamp] 4. Updating ADC with User Context..."
    gcloud auth login --update-adc
fi

# 3. Set Quota Project (The "Burn" Target)
PROJECT_ID="shadowtag-omega-v2"
echo "[$timestamp] 3. Locking Quota Project to: $PROJECT_ID"
gcloud auth application-default set-quota-project $PROJECT_ID

echo ">>> ✅ REFRESH COMPLETE. Credits should be burning."
