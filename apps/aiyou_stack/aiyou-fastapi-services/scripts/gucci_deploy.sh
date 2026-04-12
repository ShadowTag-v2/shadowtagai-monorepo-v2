#!/bin/bash
# The "Gucci" Deploy: Git Sync + Cloud Run Force Update
echo ">>> 🚀 IGNITING ANTIGRAVITY ENGINE..."

# Pivot to the best available model automatically (2.5 or 2.0)
TARGET_MODEL="gemini-2.5-flash"
grep -rl "gemini-1.5-flash" . 2>/dev/null | xargs sed -i '' "s/gemini-1.5-flash[-0-9a-z]*/\$TARGET_MODEL/g"

# Commit & Push
git add .
git commit -m "feat: Gucci Auto-Deploy \$(date +%H:%M)" || echo "Nothing to commit, forcing deploy anyway..."
git push origin main

# Force Cloud Run Deploy
# Using the judge-six-omega service name we defined earlier
gcloud run deploy judge-six-omega \\
  --source . \\
  --region us-central1 \\
  --allow-unauthenticated \\
  --# clear-base-image \\
  --quiet

echo ">>> ✨ DEPLOYMENT COMPLETE. SYSTEM IS GUCCI."
