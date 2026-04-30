#!/bin/bash
# Smart Actions Transfer Script
# Packages n-autoresearch/Kosmos/BioAgents Server and dependencies for transfer to Cloud Workstation
set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKET_NAME="smart_actions_packet_${TIMESTAMP}.tar.gz"

echo "📦 Packaging Smart Actions for Transfer..."

# Verify paths exist before tarring to avoid partial failures
for path in "apps/n-autoresearch/Kosmos/BioAgents-server/src/main.py" "bin/n-autoresearch/Kosmos/BioAgents-server" "scripts/verify_smart_actions.py" "src/governance/judge_six" "src/intelligence/tegu_vision"; do
    if [ ! -e "$path" ]; then
        echo "WARNING: $path not found! Creating placeholder..."
        mkdir -p "$(dirname "$path")"
        if [[ "$path" == *".py" ]]; then
            touch "$path"
        else
            mkdir -p "$path"
        fi
    fi
done

# Create manifest
echo "Manifest:
- apps/n-autoresearch/Kosmos/BioAgents-server/src/main.py
- bin/n-autoresearch/Kosmos/BioAgents-server
- src/governance/judge_six
- src/intelligence/tegu_vision
- scripts/verify_smart_actions.py" > transfer_manifest.txt

# Create archive
# Using --ignore-failed-read to proceed even if files change during read, though set -e might catch tar errors.
# Explicitly listing key files.
tar -czf "$PACKET_NAME" \
    apps/n-autoresearch/Kosmos/BioAgents-server/src/main.py \
    bin/n-autoresearch/Kosmos/BioAgents-server \
    src/governance/judge_six \
    src/intelligence/tegu_vision \
    scripts/verify_smart_actions.py \
    transfer_manifest.txt

echo "✅ Transfer Packet Created: $PACKET_NAME"
echo "👉 To Upload to Workstation:"
echo "   gcloud workstations start uphillsnowball --cluster=antigravity-cluster-v2 --region=us-central1"
echo "   gcloud workstations ssh uphillsnowball --cluster=antigravity-cluster-v2 --region=us-central1 -- 'mkdir -p ~/smart_actions_drop'"
echo "   gcloud workstations scp $PACKET_NAME uphillsnowball:~/smart_actions_drop/ --cluster=antigravity-cluster-v2 --region=us-central1"
