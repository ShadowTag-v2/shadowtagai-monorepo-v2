#!/bin/bash
echo "Scanning src/ and apps/ for TACSOP-5 violations..."

# Rule 1: Absolute prohibition of 'any' types
ANY_COUNT=$(grep -rn "any" src/ apps/ --include=\*.ts --include=\*.tsx 2>/dev/null | wc -l)
if [ "$ANY_COUNT" -gt 0 ]; then
    echo "❌ VIOLATION: Found $ANY_COUNT instances of 'any'. Strict typing required."
else
    echo "✅ Rule 1 (Strict Typing): PASSED"
fi

# Rule 2: No rogue console.logs
LOG_COUNT=$(grep -rn "console.log" src/ apps/ --include=\*.ts --include=\*.tsx 2>/dev/null | wc -l)
if [ "$LOG_COUNT" -gt 0 ]; then
    echo "❌ VIOLATION: Found $LOG_COUNT instances of 'console.log'. Use structured KAIROS telemetry."
else
    echo "✅ Rule 2 (Telemetry Discipline): PASSED"
fi
