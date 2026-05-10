#!/bin/bash
CACHE_DIR="$HOME/.cache/cros-ide/cipd"
TARGET_BIN="$CACHE_DIR/cipd"
REAL_BIN="$CACHE_DIR/cipd.real"

echo ">>> Engaging Immutable Shield..."

mkdir -p "$CACHE_DIR"

# Unlock any previous flags
if [ -f "$TARGET_BIN" ]; then
    sudo chflags nouchg "$TARGET_BIN" 2>/dev/null
fi

# Backup real binary if exists
if [ -f "$TARGET_BIN" ] && [ ! -L "$TARGET_BIN" ] && [ ! -f "$REAL_BIN" ]; then
    mv "$TARGET_BIN" "$REAL_BIN"
fi

# Create interceptor
cat << 'EOF' > "$TARGET_BIN"
#!/bin/bash
if [[ "$@" == *"crosfleet"* ]]; then
    echo ">>> [SHIELD] Blocked crosfleet install."
    exit 0
fi
exec "$HOME/.cache/cros-ide/cipd/cipd.real" "$@"
EOF

chmod +x "$TARGET_BIN"
sudo chflags uchg "$TARGET_BIN"

echo ">>> Shield Active."
