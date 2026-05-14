#!/bin/bash

# SHADOWTAG OMEGA: KOSMOS HARVESTER
# Purpose: Clone external sovereign entities (Monkeys) into the perimeter.

BASE_DIR="external_repos"
mkdir -p "$BASE_DIR/agentic"
mkdir -p "$BASE_DIR/infrastructure"
mkdir -p "$BASE_DIR/reference"
mkdir -p "$BASE_DIR/knowledge"

# Helper function to clone or pull
harvest() {
    CATEGORY=$1
    REPO_URL=$2
    DIR_NAME=$(basename "$REPO_URL" .git)
    TARGET_PATH="$BASE_DIR/$CATEGORY/$DIR_NAME"

    if [ -d "$TARGET_PATH" ]; then
        echo "🔄 [UPDATING] $DIR_NAME..."
        (cd "$TARGET_PATH" && git pull --quiet)
    else
        echo "⬇️ [CLONING] $DIR_NAME..."
        git clone --quiet "$REPO_URL" "$TARGET_PATH"
    fi
}

echo "=== 1. HARVESTING AGENTIC INTELLIGENCE (The Brains) ==="
harvest "agentic" "https://github.com/mikekelly/claude-sneakpeek.git"
harvest "agentic" "https://github.com/ysz/recursive-llm.git"
harvest "agentic" "https://github.com/alexzhang13/rlm.git"
harvest "agentic" "https://github.com/anthropics/knowledge-work-plugins.git"
harvest "agentic" "https://github.com/Toowiredd/claude-skills-automation.git"
harvest "agentic" "https://github.com/GantisStorm/essentials-claude-code.git"
harvest "agentic" "https://github.com/matthew-lim-matthew-lim/claude-code-system-prompt.git"
harvest "agentic" "https://github.com/psbots/clauADA.git"
harvest "agentic" "https://github.com/jujumilk3/leaked-system-prompts.git"
harvest "agentic" "https://github.com/Piebald-AI/claude-code-system-prompts.git"
harvest "agentic" "https://github.com/shawn-maybush/google_style_guide_agent_skills.git"
harvest "agentic" "https://github.com/vudovn/antigravity-kit.git"
harvest "agentic" "https://github.com/steveyegge/beads.git"
harvest "agentic" "https://github.com/miqcie/grepai-beads-helpers.git"
harvest "agentic" "https://github.com/JPM1118/Threadwork.git"
harvest "agentic" "https://github.com/akng8/beads-templates.git"
harvest "agentic" "https://github.com/asgeirtj/system_prompts_leaks.git"

echo "=== 2. HARVESTING JETSKI CAPABILITIES (The Browser) ==="
harvest "agentic" "https://github.com/nanobrowser/nanobrowser.git"
harvest "agentic" "https://github.com/browser-use/browser-use.git"
harvest "agentic" "https://github.com/Skyvern-AI/skyvern.git"
harvest "agentic" "https://github.com/apify/crawlee.git"
harvest "agentic" "https://github.com/microsoft/playwright-python.git"
harvest "agentic" "https://github.com/microsoft/playwright-mcp.git"

echo "=== 3. HARVESTING INFRASTRUCTURE (The Backbone) ==="
harvest "infrastructure" "https://github.com/terraform-google-modules/terraform-google-github-actions-runners.git"
harvest "infrastructure" "https://github.com/GoogleCloudPlatform/terraform-google-cloud-run.git"
harvest "infrastructure" "https://github.com/GoogleCloudPlatform/buildpacks.git"
harvest "infrastructure" "https://github.com/GoogleCloudPlatform/cloud-run-pubsub-pull.git"
harvest "infrastructure" "https://github.com/GoogleCloudPlatform/cluster-toolkit.git"
harvest "infrastructure" "https://github.com/GoogleCloudPlatform/magic-modules.git"
harvest "infrastructure" "https://github.com/google-github-actions/deploy-cloudrun.git"
harvest "infrastructure" "https://github.com/GoogleCloudPlatform/terraform-google-three-tier-web-app.git"

echo "=== 4. HARVESTING REFERENCE KNOWLEDGE (The Library) ==="
harvest "reference" "https://github.com/expo/expo.git"
harvest "reference" "https://github.com/ionic-team/ionic-framework.git"
harvest "reference" "https://github.com/quarkusio/quarkus.git"
harvest "reference" "https://github.com/redisson/redisson.git"
harvest "reference" "https://github.com/apache/incubator-kie-kogito-examples.git"
harvest "reference" "https://github.com/google/styleguide.git"
harvest "reference" "https://github.com/GoogleCloudPlatform/cloud-code-samples.git"
harvest "reference" "https://github.com/GoogleCloudPlatform/python-docs-samples.git"

echo "=== 5. HARVESTING TOOLS (The Toolbox) ==="
harvest "knowledge" "https://github.com/phiresky/ripgrep-all.git"
harvest "knowledge" "https://github.com/Yggdroot/LeaderF.git"
harvest "knowledge" "https://github.com/BurntSushi/ripgrep.git"

echo "=== HARVEST COMPLETE ==="
