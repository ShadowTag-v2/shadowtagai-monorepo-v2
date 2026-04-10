#!/bin/bash
# setup_workstation.sh
# RUN THIS INSIDE THE WORKSTATION (After SSH)

echo ">>> 📦 Installing Chrome Remote Desktop & XFCE..."
sudo apt-get update
sudo apt-get install --assume-yes wget task-xfce-desktop dbus-x11
wget https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb
sudo dpkg --install chrome-remote-desktop_current_amd64.deb
sudo apt-get install --assume-yes --fix-broken

echo ">>> ⚙️  Configuring Session..."
sudo bash -c 'echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" > /etc/chrome-remote-desktop-session'

echo ">>> 🚀 Activating Remote Desktop..."
# NOTE: This code expires. If it fails, ask for a new one.
DISPLAY= /opt/google/chrome-remote-desktop/start-host \
  --code="4/0ASc3gC16cxRzDJ6tlg7a1gykiJDWiIoMr-mcA-RNSvewvFMPAYVJyNB0F0L6yT7spiToFA" \
  --redirect-url="https://remotedesktop.google.com/_/oauthredirect" \
  --name=$(hostname)
