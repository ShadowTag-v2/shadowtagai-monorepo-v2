#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
cd "$ROOT"

echo "Phase 1 & 2: Structural Extraction and Archiving"

# 1. create archive/
mkdir -p archive/backups/aiyou-fastapi-services archive/legacy archive/recovered archive/imports

# Base path for aiyou-fastapi-services
FASTAPI_DIR="apps/aiyou_stack/aiyou-fastapi-services"

# 2. move _PRE_OMEGA_BACKUP_*
if ls "$FASTAPI_DIR"/libs/_PRE_OMEGA_BACKUP_* 1> /dev/null 2>&1; then
    echo "Moving backup fragments..."
    mv "$FASTAPI_DIR"/libs/_PRE_OMEGA_BACKUP_* archive/backups/aiyou-fastapi-services/
fi

# 3. move repos/aiyou-fastapi-services-legacy/
if [ -d "$FASTAPI_DIR/repos/aiyou-fastapi-services-legacy" ]; then
    echo "Moving legacy nested repo..."
    mkdir -p archive/legacy/aiyou-fastapi-services-legacy
    mv "$FASTAPI_DIR"/repos/aiyou-fastapi-services-legacy/* archive/legacy/aiyou-fastapi-services-legacy/ || true
    rm -rf "$FASTAPI_DIR"/repos/aiyou-fastapi-services-legacy
fi

# 4. move ShadowTag-Omega/
if [ -d "$FASTAPI_DIR/ShadowTag-Omega" ]; then
    echo "Moving ShadowTag-Omega..."
    mkdir -p archive/legacy/ShadowTag-Omega
    mv "$FASTAPI_DIR"/ShadowTag-Omega/* archive/legacy/ShadowTag-Omega/ || true
    rm -rf "$FASTAPI_DIR"/ShadowTag-Omega
fi

# 5. move libs/arsenal_recovered/
if [ -d "$FASTAPI_DIR/libs/arsenal_recovered" ]; then
    echo "Moving arsenal_recovered fragments..."
    mkdir -p archive/recovered/arsenal_recovered
    mv "$FASTAPI_DIR"/libs/arsenal_recovered/* archive/recovered/arsenal_recovered/ || true
    rm -rf "$FASTAPI_DIR"/libs/arsenal_recovered
fi

# 6. move apps/aiyou_ecosystem/raw_ingest/
if [ -d "apps/aiyou_ecosystem/raw_ingest" ]; then
    echo "Moving raw_ingest..."
    mkdir -p archive/imports/raw_ingest
    mv apps/aiyou_ecosystem/raw_ingest/* archive/imports/raw_ingest/ || true
    rm -rf apps/aiyou_ecosystem/raw_ingest
fi

echo "Successfully moved all non-canonical artifacts into archive/"
