#!/usr/bin/env bash
set -euo pipefail
PAYLOAD="$1"
TARGET_FILE="$2"
chflags nouchg "$TARGET_FILE" 2>/dev/null || true
VAR_NAME=$(echo "$PAYLOAD" | cut -d'=' -f1 | awk '{print $2}')
grep -v "$VAR_NAME" "$TARGET_FILE" > "${TARGET_FILE}.tmp" 2>/dev/null || true
echo "$PAYLOAD" >> "${TARGET_FILE}.tmp"
cat "${TARGET_FILE}.tmp" > "$TARGET_FILE" && rm "${TARGET_FILE}.tmp"
chflags uchg "$TARGET_FILE" 2>/dev/null || true
echo "[+] Injection successful."
