#!/bin/bash

# 1. Define the target file
TODO_FILE="TODO.md"

# 2. Check if TODO.md exists, if not create it
if [ ! -f "$TODO_FILE" ]; then
    echo "# Daily Plan" > "$TODO_FILE"
    echo "" >> "$TODO_FILE"
fi

# 3. Add a header for the harvest
echo "" >> "$TODO_FILE"
echo "### 🚜 Harvested Code Tasks ($(date))" >> "$TODO_FILE"

# 4. Find all TODOs in js/ts/py/go/html/css files, format them as checkboxes, and append
# Adjusted for Mac compatibility and robustness
grep -rE "TODO:|FIXME:" . --include=*.{js,ts,jsx,tsx,py,go,html,css} --exclude-dir={node_modules,dist,build,.git,extracted_repo} \
| sed 's/^\.\///' \
| awk -F: '{print "- [ ] " $3 " (Ref: " $1 ":" $2 ")"}' >> "$TODO_FILE"

echo "✅ Harvest complete! Check your TODO.md"
