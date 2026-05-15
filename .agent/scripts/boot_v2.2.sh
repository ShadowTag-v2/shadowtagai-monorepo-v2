#!/bin/bash
echo " Booting Antigravity Singularity Engine v2.2..."
mkdir -p .git/hooks
cat << 'HOOK' > .git/hooks/post-commit
git tag -f latest-stable >/dev/null 2>&1 || true
HOOK
chmod +x .git/hooks/post-commit
echo "✅ Temporal-Reversal Git State-Machine Initialized."
