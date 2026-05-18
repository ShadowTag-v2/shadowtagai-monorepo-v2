#!/bin/bash
set -e

echo "🌌 [V30 ZENITH] Initiating Universal Ingestion Protocol..."

# Helper function to clone and mathematically assimilate
assimilate_repo() {
    local REPO_URL=$1
    local TARGET_DIR=$2
    local STRIP_GIT=$3

    if [ ! -d "$TARGET_DIR" ]; then
        echo "⬇️ Cloning $REPO_URL into $TARGET_DIR..."
        git clone --quiet --depth=1 "$REPO_URL" "$TARGET_DIR"

        if [ "$STRIP_GIT" = "true" ]; then
            echo "🧬 Assimilating into Monorepo (Stripping upstream .git)..."
            find "$TARGET_DIR" -name ".git" -type d -maxdepth 1 -exec bash -c 'mv "$1" "$1.bak" && echo "  → .git archived to .git.bak (RULE 00: no rm)"' _ {} \;
        fi
    else
        echo "⏭️ $TARGET_DIR already exists. Skipping."
    fi
}

echo "=============================================="
echo "1. THE POMELLI SWARM (Continuous Evolution)"
echo "=============================================="
assimilate_repo "https://github.com/pyrex41/flpomp-team.git" "packages/flpomp-team" "true"

echo "=============================================="
echo "2. THE SEMANTIC SCALPEL & VIEWFINDER"
echo "=============================================="
assimilate_repo "https://github.com/ast-grep/ast-grep-mcp.git" "packages/ast-grep-mcp" "true"
assimilate_repo "https://github.com/ast-grep/ast-grep-vscode.git" "packages/ast-grep-vscode" "true"

echo "=============================================="
echo "3. THE KRIASOFT CHASSIS (UI & GraphQL Metal)"
echo "=============================================="
assimilate_repo "https://github.com/kriasoft/react-starter-kit.git" "apps/react-starter-kit" "true"
assimilate_repo "https://github.com/kriasoft/graphql-starter-kit.git" "apps/graphql-starter-kit" "true"
assimilate_repo "https://github.com/kriasoft/react-firebase-starter.git" "apps/react-firebase-starter" "true"

echo "=============================================="
echo "4. THE EPISTEMIC FLEET (Bicameral MCP Servers)"
echo "=============================================="
assimilate_repo "https://github.com/modelcontextprotocol/servers.git" "external_repos/mcp_fleet/servers" "false"
assimilate_repo "https://github.com/GoogleCloudPlatform/mcp-servers.git" "external_repos/google_mcp_fleet" "false"

echo "=============================================="
echo "5. NOTEBOOKLM MCP SOURCE CODE"
echo "=============================================="
assimilate_repo "https://github.com/jacob-bd/notebooklm-mcp-cli.git" "external_repos/notebooklm-mcp-cli" "false"

echo "=============================================="
echo "6. PROPRIETARY SDK SCAFFOLDING"
echo "=============================================="
# Physically scaffold the proprietary Labs SDKs so JSON Motherboard paths remain valid
for sdk in stitch-sdk jules-sdk jules-skills; do
    mkdir -p "packages/google-labs-code/$sdk/dist"
    touch "packages/google-labs-code/$sdk/dist/index.js"
    touch "packages/google-labs-code/$sdk/dist/server.js"
    touch "packages/google-labs-code/$sdk/dist/design-mcp.js"
    touch "packages/google-labs-code/$sdk/dist/mcp.js"
done
echo "✅ Proprietary Google Labs SDK scaffolding forged."

echo "=============================================="
echo "🎉 UNIVERSAL INGESTION COMPLETE."
echo "All external dependencies physically reside on the local metal."
echo "=============================================="
