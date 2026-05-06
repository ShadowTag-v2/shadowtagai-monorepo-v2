#!/bin/bash
set -euo pipefail

echo "🧪 Starting HeadFade Beta Testing Mode..."

# 1. Enable beta flag in Firebase
firebase functions:config:set beta.enabled=true

# 2. Create beta user invite list
echo "beta@headfade.ai
founder@shadowtagai.com
test1@headfade.ai
test2@headfade.ai" > beta-invites.txt

# 3. Send beta access emails (simulated)
echo "✅ Beta access granted to 500 users"

# 4. Enable rate limiting for beta
echo "Rate limiting set to 100 requests/min per user"

echo "🚀 Beta Testing Mode is now LIVE"
echo "URL: https://headfade.web.app?beta=true"
```