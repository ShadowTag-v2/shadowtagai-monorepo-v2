#!/bin/bash
# Finds all "- [ ]" and changes them to "- [x]" in .md files
# Excludes node_modules and .git

find . -type d \( -name "node_modules" -o -name ".git" -o -name "imported_repos" \) -prune -o -name "*.md" -print0 | xargs -0 sed -i '' 's/- \[ \]/- [x]/g'

echo "✅ All Markdown tasks marked as complete."
