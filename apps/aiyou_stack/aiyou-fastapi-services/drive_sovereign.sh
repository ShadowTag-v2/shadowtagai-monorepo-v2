#!/bin/bash
set -e

echo "🚀 [OMEGA PROTOCOL] INITIATING SOVEREIGN AUTOMATION SEQUENCE..."

# 1. GENERATE GENOME
echo ">>> [1/5] SCRIBING GENOME (incorporate_sovereign.sh)..."
bash incorporate_sovereign.sh

# 2. VALIDATE CORE
echo ">>> [2/5] VALIDATING CORE (sovereign_manifesto.py)..."
cd uphillsnowball_sovereign
python3 sovereign_manifesto.py
cd ..

# 3. SMOKE TEST GEMINI CLI
echo ">>> [3/5] VERIFYING GEMINI (CLI)..."
# In a real environment we would check for 'gemini' binary.
# Here we check the placeholder/shim availability in the repo.
if [ -f "uphillsnowball_sovereign/bin/gemini" ]; then
    echo "    ✅ Gemini CLI shim detected."
else
    echo "    ⚠️ Gemini CLI missing."
fi

# 4. SMOKE TEST WHITEBOARD
echo ">>> [4/5] EXECUTING SMART ACTION (n-autoresearch/Kosmos/BioAgents Whiteboard)..."
cd uphillsnowball_sovereign
chmod +x bin/whiteboard
bin/whiteboard "Smoke Test: Is the Sovereign Automation Sequence functional?"
cd ..

# 5. DEPLOY INFRASTRUCTURE
echo ">>> [5/5] DEPLOYING WORKSTATION (God Mode)..."
echo "    Target: Infra/Workstation (Strebel Doctrine)"
# We check for a flag since this is expensive/long-running
if [ "$1" == "--deploy" ]; then
    echo "    🚀 DEPLOYING NOW (This may take 20+ minutes)..."
    cd uphillsnowball_sovereign/infra/workstation
    bash deploy_workstation.sh
else
    echo "    ⏸️  DEPLOYMENT SKIPPED. Use './drive_sovereign.sh --deploy' to launch."
fi

echo "✅ SOVEREIGN AUTOMATION COMPLETE."
