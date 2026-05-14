#!/bin/bash
# ==========================================
# 🛰️ SOVEREIGN CYCLE: AUTO-MAINTENANCE
# ==========================================

echo "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░"
echo "   🛡️  INITIATING STASIS PROTOCOL"
echo "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░"

# 1. AUTHENTICATION HEARTBEAT
# ---------------------------
# We try to list projects. If it fails, your token is dead.
echo "📡 PINGING GOOGLE CLOUD..."
gcloud projects list --limit=1 >/dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "⚠️  SIGNAL LOST. RE-AUTHENTICATING..."
    # --update-adc ensures your Python libraries (BigQuery/Vertex) also get the new key
    gcloud auth login --update-adc
else
    echo "🔋 SIGNAL STABLE."
fi

# 2. GIT DRIFT CORRECTION
# -----------------------
# This solves the "push never works" issue by reconciling history first.
echo "🔄 SYNCHRONIZING DOCTRINE..."

# Stage everything (save state)
git add .

# Commit with a timestamp (so you never lose work if you kill the terminal)
git commit -m "stasis: auto-save $(date "+%Y-%m-%d %H:%M")" >/dev/null 2>&1

# Rebase: Put your changes ON TOP of whatever is on the server.
# This prevents the "rejected" errors.
git pull origin main --rebase

# Push: Update the remote Sovereign record.
git push origin main

# 3. LAUNCH MISSION
# -----------------
echo "🚀 LAUNCHING PNKLN PROTOCOL..."

# Ensure environment is active
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the mission
python pnkln_mission_start.py
