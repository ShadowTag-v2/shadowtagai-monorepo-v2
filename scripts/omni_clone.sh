#!/usr/bin/env bash
# Omni-Ingest Bulk Clone Script — Deduplicated, shallow, with skip list
# Skips: brave-core, devtools-frontend, ollama, daScript (too large)
set -euo pipefail

DEST="external_repos/omni_ingest"
mkdir -p "$DEST"

# Already cloned in external_repos/ (top-level)
ALREADY_CLONED=(
  pyjwt anything_about_game super-dev cfo-stack cc-sdd adk-js bubbletea
  Inquirer.js lighthouse lighthouse-ci DataflowTemplates gcsfuse
  cloud-foundation-fabric agentsmithy cloud-builders gke-mcp cloud-run-button
  cloud-run-mcp agent-starter-pack memorystore-cluster-autoscaler
  firebase-extensions click-to-deploy-solutions playwright-mcp cli
)

# Skip list (too large)
SKIP_LIST=(brave-core devtools-frontend ollama daScript)

# Deduplicated target URLs
URLS=(
  "https://github.com/JCodesMore/ai-website-cloner-template.git"
  "https://github.com/mainion-ai/memory-kernel.git"
  "https://github.com/wjgoarxiv/antigravity-swarm.git"
  "https://github.com/roshunsunder/filesift.git"
  "https://github.com/anthony-maio/mnemos.git"
  "https://github.com/andreskull/spec-driven-ai-coding.git"
  "https://github.com/AgriciDaniel/claude-seo.git"
  "https://github.com/filipecalegario/awesome-vibe-coding.git"
  "https://github.com/kitnil/notes.git"
  "https://github.com/majiayu000/claude-skill-registry.git"
  "https://github.com/jnMetaCode/superpowers-zh.git"
  "https://github.com/Leonxlnx/taste-skill.git"
  "https://github.com/davideast/stitch-mcp.git"
  "https://github.com/sickn33/antigravity-awesome-skills.git"
  "https://github.com/intellectronica/ruler.git"
  "https://github.com/gitleaks/gitleaks.git"
  "https://github.com/gitleaks/gitleaks-action.git"
  "https://github.com/mazen160/secrets-patterns-db.git"
  "https://github.com/betterleaks/betterleaks.git"
  "https://github.com/git-lfs/git-lfs.git"
  "https://github.com/git-lfs/lfs-test-server.git"
  "https://github.com/PyCQA/bandit.git"
  "https://github.com/jujumilk3/leaked-system-prompts.git"
  "https://github.com/Piebald-AI/claude-code-system-prompts.git"
  "https://github.com/matthew-lim-matthew-lim/claude-code-system-prompt.git"
  "https://github.com/kk-r/skillify-skill.git"
  "https://github.com/GoogleChrome/chrome-extensions-samples.git"
  "https://github.com/GoogleChrome/workbox.git"
  "https://github.com/GoogleChrome/web-vitals.git"
  "https://github.com/GoogleChrome/rendertron.git"
  "https://github.com/GoogleChrome/chromium-dashboard.git"
  "https://github.com/GoogleChrome/webstatus.dev.git"
  "https://github.com/GoogleChrome/lighthouse-stack-packs.git"
  "https://github.com/GoogleChrome/samples.git"
  "https://github.com/vercel-labs/skills.git"
  "https://github.com/elder-plinius/ST3GG.git"
  "https://github.com/google-labs-code/stitch-skills.git"
  "https://github.com/YouMind-OpenLab/awesome-nano-banana-pro-prompts.git"
  "https://github.com/ChromeDevTools/awesome-chrome-devtools.git"
  "https://github.com/ChromeDevTools/devtools-protocol.git"
  "https://github.com/ChromeDevTools/chrome-devtools-mcp.git"
  "https://github.com/ChromeDevTools/debugger-protocol-viewer.git"
  "https://github.com/ChromeDevTools/vite-plugin-devtools-json.git"
  "https://github.com/dair-ai/Prompt-Engineering-Guide.git"
  "https://github.com/aishwaryanr/awesome-generative-ai-guide.git"
  "https://github.com/agentskills/agentskills.git"
  "https://github.com/microsoft/vscode-copilot-chat.git"
  "https://github.com/GantisStorm/essentials-claude-code.git"
  "https://github.com/psbots/clauADA.git"
  "https://github.com/browser-use/browser-use.git"
  "https://github.com/shawn-maybush/google_style_guide_agent_skills.git"
  "https://github.com/karozi/Awesome-Vibecoding-and-Speccoding-Resources.git"
  "https://github.com/lbjlaq/Antigravity-Manager.git"
  "https://github.com/airbnb/javascript.git"
  "https://github.com/vuejs-templates/webpack.git"
  "https://github.com/coryhouse/react-slingshot.git"
  "https://github.com/jsx-eslint/eslint-plugin-react.git"
  "https://github.com/kinopeee/windsurf-antigravity-rules.git"
  "https://github.com/liuw1535/antigravity2api-nodejs.git"
  "https://github.com/study8677/antigravity-workspace-template.git"
  "https://github.com/GoogleCloudPlatform/generative-ai.git"
  "https://github.com/gemini-projects/gemini.git"
  "https://github.com/zszszszsz/.config.git"
  "https://github.com/harikrishna8121999/antigravity-workflows.git"
  "https://github.com/obra/superpowers.git"
  "https://github.com/PleasePrompto/notebooklm-skill.git"
  "https://github.com/zubair-trabzada/geo-seo-claude.git"
  "https://github.com/google-gemini/gemini-skills.git"
  "https://github.com/outsourc-e/hermes-workspace.git"
  "https://github.com/microsoft/botframework-solutions.git"
  "https://github.com/coderabbitai/skills.git"
  "https://github.com/rodydavis/skills.git"
  "https://github.com/Toowiredd/claude-skills-automation.git"
  "https://github.com/arben-adm/mcp-sequential-thinking.git"
  "https://github.com/vercel-labs/agent-skills.git"
  "https://github.com/killop/anything_about_game.git"
)

SUCCESS=0
FAIL=0
SKIP=0

for url in "${URLS[@]}"; do
  repo_name=$(basename "$url" .git)
  
  # Check skip list
  skip=false
  for s in "${SKIP_LIST[@]}"; do
    [[ "$repo_name" == "$s" ]] && skip=true && break
  done
  if $skip; then
    echo "⏭️  SKIP (too large): $repo_name"
    ((SKIP++))
    continue
  fi
  
  # Check if already cloned at top level
  already=false
  for a in "${ALREADY_CLONED[@]}"; do
    [[ "$repo_name" == "$a" ]] && already=true && break
  done
  if $already; then
    echo "✅ EXISTS (top-level): $repo_name"
    ((SKIP++))
    continue
  fi
  
  # Check if already in omni_ingest
  if [ -d "$DEST/$repo_name" ]; then
    echo "✅ EXISTS (omni_ingest): $repo_name"
    ((SKIP++))
    continue
  fi
  
  # Clone
  echo "📥 Cloning $repo_name..."
  if git clone --depth 1 "$url" "$DEST/$repo_name" 2>/dev/null; then
    ((SUCCESS++))
    echo "   ✅ Done"
  else
    ((FAIL++))
    echo "   ❌ Failed: $url"
  fi
done

echo ""
echo "🎉 Omni-clone complete: $SUCCESS cloned, $SKIP skipped, $FAIL failed"
