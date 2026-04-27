#!/bin/bash
# Pickle Rick's Fat-Body Compressor

echo "Hunting down zombies..."
pkill -9 -f "git clone" || true
pkill -9 -f "git fetch" || true
pkill -9 -f "basedpyright" || true
pkill -9 -f "node" || true
pkill -9 -f "Sovereign_Indexer" || true
pkill -9 -f "python" || true

LEGACY_DIR="/Users/pikeymickey/.gemini/antigravity/brain/legacy_archive"

if [ ! -d "$LEGACY_DIR" ]; then
    echo "Directory $LEGACY_DIR not found. Hitting the warp drive."
    exit 1
fi

echo "I'm Pickle Rick! Crushing the monstrosities in $LEGACY_DIR..."
cd "$LEGACY_DIR" || exit 1

# Find all subdirectories and compress them
for dir in */; do
    # Remove trailing slash
    target="${dir%/}"

    if [ -d "$target" ]; then
        echo "Tarballing $target..."
        # Compress using gz and remove the original directory natively
        tar -czf "${target}.tar.gz" "$target"

        if [ $? -eq 0 ]; then
            echo "Success! Incinerating raw directory $target..."
            rm -rf "$target"
        else
            echo "Error compressing $target. Aborting deletion to protect the slop."
        fi
    fi
done

echo "Storage cleansed. The empire is safe."
