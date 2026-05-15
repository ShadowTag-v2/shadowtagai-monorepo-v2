#!/bin/bash
# Install Chrome Remote Desktop and XFCE4
# Derived from configure-chrome-desktop.yml

set -e

echo "Installing Desktop Environment (XFCE4)..."
sudo apt-get update
sudo apt-get install -y xfce4 xfce4-goodies

echo "Downloading Chrome Remote Desktop..."
wget https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb -O /tmp/chrome-remote-desktop_current_amd64.deb

echo "Installing Chrome Remote Desktop..."
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y /tmp/chrome-remote-desktop_current_amd64.deb

echo "Configuring Session..."
sudo bash -c 'echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" > /etc/chrome-remote-desktop-session'

echo "Starting Service..."
sudo /etc/init.d/chrome-remote-desktop start

echo "Setup Complete. Please configuring the device via https://remotedesktop.google.com/headless"
