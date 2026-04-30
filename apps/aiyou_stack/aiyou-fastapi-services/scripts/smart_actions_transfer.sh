
#!/bin/bash
# Smart Actions Transfer Script
# Packages n-autoresearch/Kosmos/BioAgents Server and dependencies for transfer to Cloud Workstation

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKET_NAME="smart_actions_packet_${TIMESTAMP}.tar.gz"

echo "📦 Packaging Smart Actions for Transfer..."

# Create manifest
echo "Manifest:
- apps/n-autoresearch/Kosmos/BioAgents-server/src/main.py
- bin/n-autoresearch/Kosmos/BioAgents-server
- src/governance/judge_six
- src/intelligence/tegu_vision
- scripts/verify_smart_actions.py" > transfer_manifest.txt

# Create archive
tar -czf "$PACKET_NAME" \
    apps/n-autoresearch/Kosmos/BioAgents-server/src/main.py \
    bin/n-autoresearch/Kosmos/BioAgents-server \
    src/governance/judge_six \
    src/intelligence/tegu_vision \
    src/provenance \
    src/intelligence/gaas_flight \
    src/intelligence/safety_net \
    scripts/verify_smart_actions.py \
    transfer_manifest.txt

echo "✅ Transfer Packet Created: $PACKET_NAME"
echo "👉 To Upload to Workstation:"
echo "   gcloud workstations start antigravity-cockpit --cluster=antigravity-cluster-v2 --config=antigravity-cockpit-config --region=us-central1"
echo "   gcloud workstations ssh antigravity-cockpit --cluster=antigravity-cluster-v2 --region=us-central1 -- 'mkdir -p ~/smart_actions_drop'"
echo "   gcloud workstations scp $PACKET_NAME antigravity-cockpit:~/smart_actions_drop/ --cluster=antigravity-cluster-v2 --region=us-central1"
