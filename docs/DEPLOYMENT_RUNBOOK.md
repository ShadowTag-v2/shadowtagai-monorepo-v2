# HeadFade Truth Oracle — Full Deployment Runbook

**Version**: 1.0  
**Last Updated**: 2026-05-05

---

## 1. Pre-Deployment Checklist

- [ ] All 44 tasks from both checklists completed
- [ ] `npm run build` passes in `antigravity-core/mcp`
- [ ] Stripe webhook secret configured in GCP Secret Manager
- [ ] Workload Identity Federation enabled for Jules service account
- [ ] Firebase Data Connect schema deployed
- [ ] `headfade.web.app` Lighthouse score ≥ 90

---

## 2. Deployment Steps

### Step 1: Build & Test
```bash
cd antigravity-core/mcp
npm ci
npm run build
npm test
```

### Step 2: Deploy MCP Server to Cloud Run
```bash
./scripts/deploy-mcp.sh
```

### Step 3: Deploy Frontend (Embed Player + Marketplace)
```bash
cd apps/headfade/pwa
npm run build
firebase deploy --only hosting
```

### Step 4: Configure Stripe Webhook
```bash
stripe login
stripe listen --forward-to https://headfade-mcp-[hash]-uc.a.run.app/api/webhooks/stripe
```

### Step 5: Verify Workload Identity
```bash
python scripts/jules-vault.ts
```

### Step 6: Run Final Smoke Tests
- [ ] `verify_synthetic_video` returns valid data
- [ ] `purchase_workflow_license` completes successfully
- [ ] Embed Player shows live forensics
- [ ] Marketplace purchase flow works end-to-end

---

## 3. Post-Deployment

- Update `docs/headfade-strategy.md` with live URLs
- Announce on X using `launch-thread.md`
- Monitor Cloud Run logs for 24 hours
- Enable autoscaling (min 2, max 100)

---

**Status**: Ready for Production Launch
```