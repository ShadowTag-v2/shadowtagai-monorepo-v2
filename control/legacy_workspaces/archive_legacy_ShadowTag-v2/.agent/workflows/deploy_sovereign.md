---
description: Deploy Sovereign OS (Trinity Cockpit) to Cloud Run
---

# Deploy Sovereign OS (Sovereign Eyes Only)

Per the Constitution (GEMINI.md), the Project ID is **`shadowtag-omega-v4`**.
Do NOT use `acquired-jet-478701-b3`.

## 1. Verify Project

```bash
gcloud config set project shadowtag-omega-v4
```

## 2. Deploy (Cockpit)

// turbo

```bash
cd trinity/apps/cockpit
gcloud builds submit . --tag gcr.io/shadowtag-omega-v4/trinity-os
gcloud run deploy trinity-os \
  --image gcr.io/shadowtag-omega-v4/trinity-os \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```
