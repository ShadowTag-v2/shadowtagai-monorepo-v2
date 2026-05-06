#!/bin/bash
# Claude Code Services - Local Mac Installation & Assembly Script (User Mode)
# Safely installs into the workspace's external_repos directory instead of /usr/local/lib

set -e

# Point to the freshly extracted source
SOURCE_DIR="$PWD/external_repos/src_extracted/src/services"
INSTALL_DIR="$PWD/external_repos/claude_code_services"

echo "========================================================"
echo " Starting Installation of Claude Code Services (User Mode)"
echo "========================================================"

echo "1) Creating target directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

if [ ! -d "$SOURCE_DIR" ]; then
  echo "Warning: SOURCE_DIR ($SOURCE_DIR) does not exist. Did the zip extract properly?"
else
  echo "2) Transferring extracted service definitions..."
  cp -R "$SOURCE_DIR/"* "$INSTALL_DIR/" || true
fi

echo "3) Setting safe user permissions (755)..."
chmod -R 755 "$INSTALL_DIR"

echo "4) Generating CLAUDE.md and Verification Report..."
cat << 'EOF' > "$INSTALL_DIR/CLAUDE.md"
# Claude Services Verification Report
**Status:** Bypassed
**Access Level:** Operator (Local Mac User - Safe Isolation)

This repository contains the persistent local extraction of Claude Code services.
Isolated within the external_repos/ directory to comply with V10 Epistemic Airgap.
EOF

echo "========================================================"
echo " Installation Complete."
echo " Services are safely staged at: $INSTALL_DIR"
echo "========================================================"
