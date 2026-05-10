#!/bin/bash

echo "Starting cleanup in root directory: $(pwd)"
echo "------------------------------------------------"

# 1. Delete the duplicate files (explicitly protecting the root files)
echo "Looking for duplicate files..."

find . -type f \
  \( -path "*/.vscode/settings.json" -o -path "*/.agent/rules/snyk_rules.md" \) \
  -not -path "./.vscode/settings.json" \
  -not -path "./.agent/rules/snyk_rules.md" \
  -exec echo "Deleted file: {}" \; -delete

# 2. Clean up the empty folders left behind (explicitly protecting root folders)
echo "Sweeping up empty .vscode and .agent directories..."

# Clean up empty rules directories
find . -type d -path "*/.agent/rules" -not -path "./.agent/rules" -empty -exec echo "Deleted empty folder: {}" \; -delete

# Clean up empty .agent directories
find . -type d -path "*/.agent" -not -path "./.agent" -empty -exec echo "Deleted empty folder: {}" \; -delete

# Clean up empty .vscode directories
find . -type d -path "*/.vscode" -not -path "./.vscode" -empty -exec echo "Deleted empty folder: {}" \; -delete

echo "------------------------------------------------"
echo "Cleanup complete! Your workspace is tidy."
