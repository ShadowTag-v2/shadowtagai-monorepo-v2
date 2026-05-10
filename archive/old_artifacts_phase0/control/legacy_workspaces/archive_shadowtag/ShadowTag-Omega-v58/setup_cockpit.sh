#!/bin/bash
echo ">>> 🔧 Installing Google Gemini CLI..."
# Requires Node.js (Standard in Workstation images)
npm install -g @google/gemini-cli

echo ">>> ⚙️ Configuring Project Context..."
# This ensures the CLI uses our Vertex Project
export GOOGLE_CLOUD_PROJECT="shadowtag-omega-v2"
export GOOGLE_CLOUD_LOCATION="us-central1"

echo ">>> ✅ COCKPIT READY."
echo ">>> Type 'gemini' to start the Sovereign Shell."
