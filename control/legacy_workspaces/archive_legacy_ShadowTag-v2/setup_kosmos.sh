#!/bin/bash
echo "🔥 Initiating Nuclear Purge..."
pkill -9 -f "cloudcode" || true
pkill -9 -f "geminicodeassist" || true
pkill -9 -f "a2a-server" || true
rm -rf ~/.antigravity/extensions/google.geminicodeassist*
rm -rf ~/Library/Application\ Support/cloud-code
rm -rf ~/Library/Application\ Support/google-vscode-extension

echo "🗑️ Incinerating Obsolete Linear Drones..."
rm -rf /Users/pikeymickey/.gemini/extensions/pickle-rick
rm -rf /Users/pikeymickey/aiyou-stack/ShadowTag-v2/scripts/omega-ralph

echo "👻 Silencing Vim Extension Unhandled Rejection..."
mkdir -p ~/Library/Application\ Support/Antigravity/User/globalStorage/vscodevim.vim/
touch ~/Library/Application\ Support/Antigravity/User/globalStorage/vscodevim.vim/.registers

echo "🌌 Forging Kosmos World Model (arXiv:2511.02824)..."
mkdir -p /Users/pikeymickey/aiyou-stack/swarm-engine
cd /Users/pikeymickey/aiyou-stack/swarm-engine

if [ ! -d "Kosmos" ]; then
  git clone https://github.com/jimmc414/Kosmos.git
fi
cd Kosmos
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt || true

echo "✅ GHOSTS PURGED. KOSMOS SWARM INSTANTIATED."
