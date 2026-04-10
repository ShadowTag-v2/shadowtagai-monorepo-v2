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
# Replace any legacy gemini-3.1-family or 2.5 references
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
