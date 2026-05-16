#!/bin/bash
# SHADOWTAG OMEGA LAUNCHER (FINAL)
# Directives: No GPU, Force SRGB, Skia Rendering, ZSH default

# Set Environment Variables for the Session
export GOOGLE_CLOUD_PROJECT="shadowtag-omega-v2"
export CLOUDSDK_CORE_PROJECT="shadowtag-omega-v2"
export PATH="$HOME/aiyou-stack/ShadowTag-v2/depot_tools:$PATH"

# Launch Antigravity with Hardware Acceleration KILLED
open -a "Antigravity" --args \
  --disable-gpu \
  --disable-software-rasterizer \
  --disable-gpu-compositing \
  --disable-gpu-rasterization \
  --disable-accelerated-2d-canvas \
  --disable-accelerated-video-decode \
  --force-color-profile=srgb \
  /Users/pikeymickey/aiyou-stack/ShadowTag-v2
