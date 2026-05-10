#!/bin/bash
# setup_workstation.sh
# RUN THIS INSIDE THE WORKSTATION (After SSH)
set -euo pipefail

echo ">>> 📦 Installing Chrome Remote Desktop & XFCE..."
sudo apt-get update
sudo apt-get install --assume-yes wget task-xfce-desktop dbus-x11
wget https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb
sudo dpkg --install chrome-remote-desktop_current_amd64.deb || sudo apt-get install --assume-yes --fix-broken

echo ">>> ⚙️  Configuring Session..."
sudo bash -c 'echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" > /etc/chrome-remote-desktop-session'

echo ">>> 🚀 Activating Remote Desktop..."
echo "Please visit https://remotedesktop.google.com/headless, authenticate, and copy the code (formatted as '4/...')."
read -r -p "Paste the code here: " AUTH_CODE

if [ -z "$AUTH_CODE" ]; then
    echo "❌ No code provided. Exiting."
    exit 1
fi

DISPLAY= /opt/google/chrome-remote-desktop/start-host \
  --code="$AUTH_CODE" \
  --redirect-url="https://remotedesktop.google.com/_/oauthredirect" \
  --name="$(hostname)"
