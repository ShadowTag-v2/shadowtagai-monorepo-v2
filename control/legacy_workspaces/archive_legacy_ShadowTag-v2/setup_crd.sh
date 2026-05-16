#!/bin/bash
# Chrome Remote Desktop Setup Command
# Generated: $(date)
# NOTE: The code below expires quickly. Run immediately.

DISPLAY= /opt/google/chrome-remote-desktop/start-host \
  --code="4/0ASc3gC16cxRzDJ6tlg7a1gykiJDWiIoMr-mcA-RNSvewvFMPAYVJyNB0F0L6yT7spiToFA" \
  --redirect-url="https://remotedesktop.google.com/_/oauthredirect" \
  --name=$(hostname)
