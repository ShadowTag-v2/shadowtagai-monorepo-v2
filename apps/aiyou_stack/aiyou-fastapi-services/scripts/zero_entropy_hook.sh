#!/bin/bash
# .git/hooks/pre-commit
# PROTOCOL: ZERO_ENTROPY

echo ">>> 🛡️  COR.CLAUDE_CODE_6 SECURITY PROTOCOL INITIATED..."

# 1. Check for Hardcoded Keys (The "Stupid" Check)
if grep -rE "sk_live_|sk_test_" ./app; then
    echo "❌ CRITICAL: LEAK DETECTED. DO NOT COMMIT KEYS."
    exit 1
fi

# 2. Enforce "Strict Act-As" Naming Convention
# All secure functions must start with 'secure_'
grep -r "function" ./app/api | while read -r line ; do
   if [[ "$line" != *"secure_"* ]]; then
      echo "⚠️  WARNING: Function violates Strict Act-As naming."
   fi
done

echo "✅ ZERO ENTROPY ACHIEVED. COMMITTING..."
