#!/bin/bash
# Verify Beads Installation

echo "=== BEADS VERIFICATION ==="

# 1. Check Binary
if [ -x "scripts/bd" ]; then
    echo "✅ 'bd' tool found and executable."
else
    echo "❌ 'bd' tool MISSING or NOT executable."
    exit 1
fi

# 2. Test Create
echo "Testing issue creation..."
./scripts/bd create "Test Issue" --desc "This is a test" --prio 3

# 3. Check File
if [ -f ".beads/issues.jsonl" ]; then
    echo "✅ .beads/issues.jsonl created."
    cat .beads/issues.jsonl | grep "Test Issue"
else
    echo "❌ Issue file not created."
    exit 1
fi

# 4. Check Git Ignore status (Should NOT be ignored usually, but check user preference)
# echo "Checking if tracked by git..."
# git check-ignore .beads/issues.jsonl

echo "=== VERIFICATION COMPLETE ==="
echo "Beads are functional. Ready for memory storage."
