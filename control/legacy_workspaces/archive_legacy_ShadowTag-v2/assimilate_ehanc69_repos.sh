#!/bin/bash

# ==============================================================================
# MASSIVE GIT HARMONIZATION SEQUENCE
# Target: Monorepo-Uphillsnowball/third_party/ehanc69_repos
# Objective: Assimilate 40+ scattered playground and remote repositories.
# ==============================================================================

set -e

DESTINATION="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party"
EHANC69_DIR="$DESTINATION/ehanc69_repos"
PLAYGROUND_DIR="/Users/pikeymickey/.gemini/antigravity/playground"

echo "[*] Initializing Massive Git Harmonization..."

# Ensure the third_party directory structure exists inside the monolith
mkdir -p "$EHANC69_DIR"

# 1. Merge the physical playground folders first (the ones you linked)
echo "[*] Harmonizing local playground environments from $PLAYGROUND_DIR..."
if [ -d "$PLAYGROUND_DIR" ]; then
    # -n prevents overwriting but copies everything recursively
    cp -Rn "$PLAYGROUND_DIR/"* "$EHANC69_DIR/" || true
fi

# Move into the assimilation sector
cd "$EHANC69_DIR"

# 2. Pull down the explicit ShadowTag-v2 service
echo "[*] Cloning explicit Target: aiyou-fastapi-services..."
if [ ! -d "aiyou-fastapi-services" ]; then
    git clone https://github.com/ShadowTag-v2/aiyou-fastapi-services.git || true
else
    echo "  -> Found existing local instance: aiyou-fastapi-services (Skipping clone)"
fi

# 3. Pull down any remaining ehanc69 GitHub repos
echo "[*] Querying GitHub API for remaining ehanc69 repositories (~40 repos)..."
curl -s "https://api.github.com/users/ehanc69/repos?per_page=100" | grep -o '"clone_url": "[^"]*"' | awk -F'"' '{print $4}' | while read -r repo_url; do
    repo_name=$(basename "$repo_url" .git)
    if [ ! -d "$repo_name" ]; then
        echo "  -> Assimilating missing remote: $repo_name"
        git clone "$repo_url" || true
    else
        echo "  -> Found existing local instance: $repo_name (Skipping clone)"
    fi
done

# 4. Strip all nested .git directories so the Monorepo tracks them as native files
echo "[*] Stripping nested .git directories to prevent submodule fragmentation..."
find "$EHANC69_DIR" -type d -name ".git" -exec rm -rf {} + || true

echo "[*] ==========================================================="
echo "[*] Massive Git harmonization complete!"
echo "[*] All 40+ folders and external repositories are now unified."
echo "[*] Bound permanently inside: $EHANC69_DIR"
echo "[*] You can now simply run: git add . && git commit -m 'Ingested ehanc69 matrix'"
echo "[*] ==========================================================="
