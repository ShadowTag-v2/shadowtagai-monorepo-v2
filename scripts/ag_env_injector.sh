#!/usr/bin/env bash
# Usage: sudo ./scripts/ag_env_injector.sh "export NEW_VAR=1" ~/.openclaude_env
set -euo pipefail
PAYLOAD="$1"
TARGET_FILE="$2"

echo "[*] Temporarily dropping shield on $TARGET_FILE..."
chflags nouchg "$TARGET_FILE" 2>/dev/null || true
VAR_NAME=$(echo "$PAYLOAD" | cut -d'=' -f1 | awk '{print $2}')
grep -v "$VAR_NAME" "$TARGET_FILE" > "${TARGET_FILE}.tmp" 2>/dev/null || true
echo "$PAYLOAD" >> "${TARGET_FILE}.tmp"
cat "${TARGET_FILE}.tmp" > "$TARGET_FILE"
rm "${TARGET_FILE}.tmp"
echo "[*] Re-engaging shield..."
chflags uchg "$TARGET_FILE" 2>/dev/null || true
echo "[+] Injection successful."
