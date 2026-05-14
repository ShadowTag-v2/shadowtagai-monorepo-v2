#!/usr/bin/env bash
set -euo pipefail

echo "🔄 pnkln Self-Update Daemon Starting..."

# 1. Pull latest thread context (Antigravity memory + Google Drive via API)
echo "→ Scanning thread + Drive for new rules..."
# Antigravity native memory dump
antigravity export-memory --format=json > /tmp/thread-dump.json

# 2. Regenerate master rules with new content
node -e '
  const fs = require("fs");
  const dump = JSON.parse(fs.readFileSync("/tmp/thread-dump.json"));
  let rules = fs.readFileSync(".antigravity/rules/cor-antigravity.mdc", "utf8");
  
  // Append new thread insights while preserving Judge-6 gate
  const newSection = `\n\n## Thread Update ${new Date().toISOString()}\n${dump.summary || "No new rules"}\n`;
  rules = rules.replace(/(## Final Install.*)/s, newSection + "$1");
  
  fs.writeFileSync(".antigravity/rules/cor-antigravity.mdc", rules);
  console.log("Rules regenerated with latest thread data");
'

# 3. Re-apply Judge-6 cinematic gate (never weaken)
chmod +x scripts/judge6.sh
echo "Judge-6 cinematic enforcement re-locked."

# 4. Restart Antigravity workspace
antigravity restart-workspace

echo "✅ pnkln Control Plane Updated — Judge-6 remains fully armed."
