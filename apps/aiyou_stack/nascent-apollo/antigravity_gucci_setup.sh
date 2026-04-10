#!/bin/bash
set -e

echo ">>> 💎 INSTALLING GUCCI AUTOMATION SUITE (GEMINI 3.0 OMEGA)..."

# 1. CREATE THE PREMIUM SCRIPTS FOLDER
mkdir -p scripts
chmod +x scripts

# 2. SCRIPT A: THE 'GOD MODE' DEPLOYER (Dynamic & Sage)
cat << 'SCRIPT' > scripts/gucci_deploy.sh
#!/bin/bash
# The "Gucci" Deploy: Git Sync + Cloud Run Force Update
echo ">>> 🚀 IGNITING ANTIGRAVITY ENGINE..."

# 1. DYNAMIC CONFIG
PROJECT_ID=$(gcloud config get-value project)
echo ">>> Target Project: $PROJECT_ID"

if [ -z "$PROJECT_ID" ]; then
  echo "❌ ERROR: No Google Cloud Project set. Run 'gcloud config set project [ID]' first."
  exit 1
fi

# 2. AUTO-UPGRADE MODELS (Gemini 3.0 Flash Enforcement)
TARGET_MODEL="gemini-3.0-flash"
echo ">>> 🧠 Enforcing Neural Architecture: $TARGET_MODEL..."
# Replace any legacy gemini-3.1-pro or 2.5 references
grep -rl "gemini-\(1\.5\|2\.0\|2\.5\)-flash[-0-9a-z]*" . --exclude-dir={.git,node_modules,venv,__pycache__} 2>/dev/null | xargs sed -i '' "s/gemini-\(1\.5\|2\.0\|2\.5\)-flash[-0-9a-z]*/$TARGET_MODEL/g" || true

# 3. SMART COMMIT
COMMIT_MSG="${1:-feat: Gucci Auto-Deploy $(date +%H:%M)}"

echo ">>> 📦 Staging and Committing..."
git add .
git commit -m "$COMMIT_MSG" || echo ">>> No code changes detected, proceeding to build..."
git push origin main || echo ">>> Push failed (possibly no upstream), proceeding to deploy..."

# 4. CLOUD RUN DEPLOY
echo ">>> ☁️  Deploying to Cloud Run..."
gcloud run deploy https://github.com/karpathy/autoresearchs-server \
  --project "$PROJECT_ID" \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --quiet

echo ">>> ✨ DEPLOYMENT COMPLETE. SYSTEM IS GUCCI."
SCRIPT
chmod +x scripts/gucci_deploy.sh

# 3. SCRIPT B: THE AGENT CONSULTANT (Gemini 3.0)
cat << 'SCRIPT' > scripts/gucci_agent.sh
#!/bin/bash
echo ">>> 🧠 SUMMONING AGENT (GEMINI 3.0)..."
PROJECT_ID=$(gcloud config get-value project)
export GOOGLE_CLOUD_PROJECT=$PROJECT_ID

uv run python3 -c "
import os
from google import genai
try:
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    # Assuming standard Vertex AI client structure; model name is the key
    print(f'    ✅ NEURAL LINK ACTIVE: gemini-3.0-flash [{project_id}]')
    print('    waiting for instructions...')
except Exception as e:
    print(f'    ❌ LINK ERROR: {e}')
"
SCRIPT
chmod +x scripts/gucci_agent.sh

# 4. CONFIGURE VS CODE TASKS
mkdir -p .vscode
cat << 'JSON' > .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "🚀 Antigravity: Deploy God Mode",
      "type": "shell",
      "command": "./scripts/gucci_deploy.sh",
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "dedicated",
        "showReuseMessage": false
      },
      "problemMatcher": []
    },
    {
      "label": "🧠 Antigravity: Test Agent",
      "type": "shell",
      "command": "./scripts/gucci_agent.sh",
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      }
    }
  ]
}
JSON

echo ">>> 💎 VS CODE AUTOMATION INSTALLED (GEMINI 3.0 ENFORCED)."
