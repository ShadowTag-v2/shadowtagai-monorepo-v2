#!/bin/bash
# Memory Seeding Preparation Script
# Creates a branch and commits "bad code" to trigger the Seed PR protocol.

BRANCH_NAME="feat/training-legacy-traps"

# 1. Create and Switch to Branch
git checkout -b $BRANCH_NAME || git checkout $BRANCH_NAME

# 2. Stage the Trap File
git add src/legacy-traps.ts

# 3. Commit with a message that invites review
git commit -m "feat: add legacy processing utilities (needs review)"

echo "✅ Local branch '$BRANCH_NAME' prepared."
echo "👉 ACTION REQUIRED: Run 'git push origin $BRANCH_NAME' and open a Pull Request."
