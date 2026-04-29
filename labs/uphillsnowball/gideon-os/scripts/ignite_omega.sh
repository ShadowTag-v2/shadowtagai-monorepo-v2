#!/bin/bash
# ==============================================================================
#  SHADOWTAG OS : GENESIS OMNI-COMPILE (FEDERAL EDITION v_FINAL)
# ==============================================================================
# Block 14 of the Ex Toto Omni-Compile (Gideon OS Architecture)
# The Master Bootstrapper. Boots all subsystems.
# ==============================================================================
set -euo pipefail

echo ">>> 🚀 IGNITING SHADOWTAG OS (Gideon OS Architecture)..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo ">>> [1/8] Deploying Sovereign Infrastructure..."
if [[ -d "$REPO_ROOT/infra" ]] && command -v terraform &>/dev/null; then
    cd "$REPO_ROOT/infra" && terraform init && terraform plan && cd "$REPO_ROOT"
    echo "   [+] Terraform plan generated (apply requires manual approval)."
else
    echo "   [!] Terraform not found or infra/ missing. Skipping."
fi

echo ">>> [2/8] Pathway LLM-App Real-Time Sync..."
echo "   [!] Pathway requires manual start: python src/epistemology/pathway_ingest.py &"

echo ">>> [3/8] AntiGravity Port 3025 Browser Connector..."
echo "   [!] CDP Bridge requires manual start: node src/senses/browser_extension/service_worker_binary.js &"

echo ">>> [4/8] Federal Go Control Plane (Judge 6 Ingress)..."
if command -v go &>/dev/null; then
    cd "$REPO_ROOT" && go build -o Cor.Claude_Code_6 cmd/gideon-go/shield1_ingress.go 2>/dev/null || echo "   [!] Go build requires cloud.google.com/go/pubsub dependency."
else
    echo "   [!] Go not found. Skipping Cor.Go compilation."
fi

echo ">>> [5/8] C++ Midas Hot Path..."
echo "   [!] Midas requires Cloud Build: gcloud builds submit --tag gcr.io/shadowtag/midas-cpp src/finance/"

echo ">>> [6/8] COR.KAIROS Daemon (Python)..."
echo "   [!] COR.KAIROS requires manual start: python src/daemon/kairos_supervisor.py &"

echo ">>> [7/8] Cor.Yay Bridge (Pub/Sub to WebSocket Relay)..."
echo "   [!] Cor.Yay requires manual start: node src/workstation/cor_yay_bridge.js &"

echo ">>> [8/8] Tauri / Rust Cockpit..."
if command -v cargo &>/dev/null; then
    echo "   [+] Cargo available. Run: cd src-tauri && cargo tauri dev"
else
    echo "   [!] Cargo/Rust not found. Install via rustup."
fi

echo ""
echo "✅ GENESIS OMNI-COMPILE COMPLETE."
echo "   All subsystems enumerated. Manual start required for daemons."
echo "   Run individual services with the commands above."
