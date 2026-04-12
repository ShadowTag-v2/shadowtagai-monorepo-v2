#!/bin/bash
# Fix IAP Connection Issues
# 1. Installs NumPy for better IAP performance
# 2. Creates the required Firewall Rule for SSH via IAP

echo ">>> 📦 Installing NumPy for IAP optimization..."
/usr/bin/python3 -m pip install --user numpy || echo "NumPy install failed (might already be installed)"

echo ">>> 🛡️  Creating IAP Firewall Rule (allow 35.235.240.0/20)..."
gcloud compute firewall-rules create allow-iap-ssh-ingress \
    --allow tcp:22 \
    --source-ranges 35.235.240.0/20 \
    --description="Allow SSH from IAP" \
    --project=shadowtag-omega-v2 \
    || echo "Firewall rule might already exist."

echo ">>> ✅ Done. Try connecting now."
