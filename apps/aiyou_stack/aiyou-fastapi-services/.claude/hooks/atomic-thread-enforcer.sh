#!/bin/bash
# Atomic Thread Enforcer Hook
# Validates that thread files contain required OPORD sections

set -e

FILE="$1"

if [[ -z "$FILE" ]]; then
    echo "Usage: $0 <thread-file.md>"
    exit 1
fi

if [[ ! -f "$FILE" ]]; then
    echo "ERROR: File not found: $FILE"
    exit 1
fi

# Required sections for OPORD format
REQUIRED_SECTIONS=(
    "thread_id:"
    "## 1. SITUATION"
    "## 2. MISSION"
    "## 3. EXECUTION"
    "## 4. SERVICE & SUPPORT"
    "## 5. COMMAND & SIGNAL"
    "### d. Brakes"
    "Handoff JSON"
)

ERRORS=0

for section in "${REQUIRED_SECTIONS[@]}"; do
    if ! grep -q "$section" "$FILE"; then
        echo "MISSING: $section"
        ((ERRORS++))
    fi
done

# Check for kill conditions
if ! grep -q "\[ \] If.*STOP" "$FILE"; then
    echo "WARNING: No kill conditions defined in Brakes section"
fi

# Check for handoff JSON structure
if ! grep -q '"thread_id":' "$FILE"; then
    echo "WARNING: Handoff JSON may be malformed"
fi

# Check TLP checklist
if ! grep -q "TLP (Troop Leading Procedures)" "$FILE"; then
    echo "MISSING: TLP checklist"
    ((ERRORS++))
fi

if [[ $ERRORS -gt 0 ]]; then
    echo ""
    echo "VALIDATION FAILED: $ERRORS required sections missing"
    exit 1
fi

echo "VALIDATED: $FILE contains all required OPORD sections"
exit 0
