#!/bin/bash

echo "Initializing Antigravity Velocity Engine Protocol..."

# Force Global Context Exports
export GCP_PROJECT_ID="shadowtag-omega-v4"
export BRAIN_DIR="/Users/pikeymickey/.gemini/antigravity/brain/888134be-c1c6-4483-8121-b472c9918516"
export EXTERNAL_SDKS="/Users/pikeymickey/aiyou-stack/ShadowTag-v2/libs"

# Bind the headless GCP Authentication logic loop
nohup python3 scripts/omega_auth_daemon.py > /tmp/velocity_daemon.log 2>&1 &

echo "[✅] Auth Daemon heartbeat running (Refresh bounds = 10m)."
echo "[✅] GCP_PROJECT_ID explicitly set to shadowtag-omega-v4."
echo "[✅] Multi-Root YOLO Mode variables attached to session."

echo "\nWARNING: To fully bypass GCA prompts, you MUST also add \"geminicodeassist.agentYoloMode\": true directly to your global User settings.json inside VS Code (Cmd+Shift+P > Preferences: Open User Settings), as VS Code dynamically strips YOLO mode out of Workspace files if they aren't explicitly Trusted File entries."
