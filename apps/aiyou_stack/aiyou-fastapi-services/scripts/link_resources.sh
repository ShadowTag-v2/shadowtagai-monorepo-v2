#!/bin/bash
# Link Google Drive Resources to Workspace (Total Recall)
# Target: knowledge/drive_resources

set -e

mkdir -p knowledge/drive_resources

# Detailed paths from User + Discovered Stash
STASH_ROOT="/Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/tools/legacy/_root_stash/Legacy_Root_Backup_1768377113"
DEEP_PATH="$STASH_ROOT/Legacy_Archives/deleted_users_drive/ShadowTag-v2-fastapi-services/ShadowTag-v2-fastapi-services/CONSOLIDATED_SCRIPTS/Users_Deleted Users_pikeymickey_ShadowTag-v2-fastapi-services_external_repos_claude-scientific-skills"
SNOWBALL_DEEP_PATH="$STASH_ROOT/Legacy_Archives/deleted_users_drive/ShadowTag-v2-fastapi-services/ShadowTag-v2-fastapi-services/uphillsnowball_sovereign"

# Exhaustive list of paths requested by user
PATHS=(
    "$STASH_ROOT"
    "/Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/tools/legacy/external_repos/ehanc69/ShadowTag-v2-fastapi-services"
    "/Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/tools/legacy/external_repos/ehanc69/ShadowTag-v2-fastapi-services/src"
    "/Users/pikeymickey/Library/CloudStorage/GoogleDrive-ehanc6901@gmail.com/My Drive/ShadowTag-v2_Phase_Docs/Ai Resources.1"
    "/Users/pikeymickey/Library/CloudStorage/GoogleDrive-ehanc6901@gmail.com/My Drive/ShadowTag-v2_Phase_Docs/AI Resources.3"
    "/Users/pikeymickey/Library/CloudStorage/GoogleDrive-ehanc6901@gmail.com/My Drive/ShadowTag-v2_Phase_Docs/AiResources2"
    "/Users/pikeymickey/Documents/Documents"
    "/Users/pikeymickey/Documents/Claude Code/Code/Claude Demo/ShadowTag-v2-fastapi-services/erik-hancock-llm-memory/scripts"
    "/Users/pikeymickey/Documents/GitHub/chrome-devtools-mcp"
    "/Users/pikeymickey/Documents/GitHub/aider_ollama"
    "/Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2"
)

echo "🔗 Linking Intelligence Assets..."

for src in "${PATHS[@]}"; do
    if [ -d "$src" ]; then
        dirname=$(basename "$src")
        # Handle spaces in filenames safely
        target="knowledge/drive_resources/${dirname// /_}"

        echo "   -> Linking '$dirname' to '$target'"
        ln -sfn "$src" "$target"
    else
        echo "⚠️  Warning (Expected): Source path not found: $src"
    fi
done

# Link Scientific Skills explicitly if found (Deep Stash)
if [ -d "$DEEP_PATH" ]; then
    echo "   -> Linking 'claude-scientific-skills' (Deep Stash)"
    ln -sfn "$DEEP_PATH" "knowledge/drive_resources/claude-scientific-skills"
fi

# Link Uphill Snowball explicitly if found (Deep Stash)
if [ -d "$SNOWBALL_DEEP_PATH" ]; then
    echo "   -> Linking 'uphillsnowball' (Retail GUI) from Deep Stash"
    ln -sfn "$SNOWBALL_DEEP_PATH" "knowledge/drive_resources/uphillsnowball"
fi

echo "✅ Resources linked in knowledge/drive_resources/"

# Java Alignment (OpenJDK 17 for GCloud/Bazel combatibility)
export JAVA_HOME="/opt/homebrew/Cellar/openjdk@17/17.0.18/libexec/openjdk.jdk/Contents/Home"
echo "☕️ Java Environment aligned to: $(java -version 2>&1 | head -n 1)"
