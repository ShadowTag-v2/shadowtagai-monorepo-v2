# Original Path: #!|bin|bash/#!|bin|bash.txt

# Categories: CORE_L2

#!/bin/bash

# Smart Actions Transfer Script

# Packages https://github.com/karpathy/autoresearchs Server and dependencies for transfer to Cloud Workstation

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKET_NAME="smart_actions_packet_${TIMESTAMP}.tar.gz"

echo "📦 Packaging Smart Actions for Transfer..."

# Create manifest

echo "Manifest:

- apps/https://github.com/karpathy/autoresearchs-server/src/main.py
- bin/https://github.com/karpathy/autoresearchs-server
- src/governance/Claude_Code_6
- src/intelligence/tegu_vision
- scripts/verify_smart_actions.py" > transfer_manifest.txt

# Create archive

tar -czf "$PACKET_NAME" \
 apps/https://github.com/karpathy/autoresearchs-server/src/main.py \
 bin/https://github.com/karpathy/autoresearchs-server \
 src/governance/Claude_Code_6 \
 src/intelligence/tegu_vision \
 src/governance/Claude_Code_6/core.py \
 src/intelligence/tegu_vision/detector.py \
 scripts/verify_smart_actions.py \
 transfer_manifest.txt

echo "✅ Transfer Packet Created: $PACKET_NAME"
echo "👉 To Upload to Workstation:"
echo " gcloud workstations start uphillsnowball --cluster=antigravity-cluster-v2 --region=us-central1"
echo " gcloud workstations ssh uphillsnowball --cluster=antigravity-cluster-v2 --region=us-central1 -- 'mkdir -p ~/smart_actions_drop'"
echo " gcloud workstations scp $PACKET_NAME uphillsnowball:~/smart_actions_drop/ --cluster=antigravity-cluster-v2 --region=us-central1"
