#!/bin/bash
# INTEGRATE BEADS TEMPLATES
SOURCE_DIR="external_repos/agentic/beads-templates"
TARGET_DIR=".beads/templates"

if [ -d "$SOURCE_DIR" ]; then
    echo "✅ Found Beads Templates. Copying..."
    mkdir -p "$TARGET_DIR"
    cp -r "$SOURCE_DIR/"* "$TARGET_DIR/"
    echo "📋 Templates installed to $TARGET_DIR"
    ls -l "$TARGET_DIR"
else
    echo "⏳ Beads Templates repo not found yet."
fi
