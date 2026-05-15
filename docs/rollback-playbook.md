# Rollback Playbook — ShadowTagAI Monorepo v2 Migration

> **Last Updated:** 2026-05-09
> **Owner:** Antigravity Operator

---

## Overview

This playbook documents how to safely rollback any phase of the monorepo migration. Each phase has independent rollback procedures.

---

## Phase 1 Rollback: App Extraction

**Scenario:** Migrated app (headfade, counselconduit, aiyou_stack) fails in the new repo.

### Steps

1. **Revert the commit:**
   ```bash
   git revert <commit-hash> --no-edit
   git push origin main
   ```

2. **Re-enable old repo deployments:**
   ```bash
   cd /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball
   git checkout main
   # Old CI/CD still has the working configs
   ```

3. **Verify old deployment:**
   - HeadFade: `https://headfade.web.app` (old Firebase Hosting)
   - CounselConduit: `https://counselconduit-767252945109.us-central1.run.app`

### Blast Radius: Zero production impact (old services still running)

---

## Phase 2 Rollback: Build System

**Scenario:** Bazel MODULE.bazel changes break the build.

### Steps

1. **Reset MODULE.bazel to known-good state:**
   ```bash
   git checkout latest-stable -- MODULE.bazel BUILD.bazel
   ```

2. **Clear Bazel cache:**
   ```bash
   bazel clean --expunge
   ```

3. **Verify:**
   ```bash
   bazel build //...
   ```

### Blast Radius: Development only (no production impact)

---

## Phase 3 Rollback: CI/CD

**Scenario:** New `omni-ci.yml` breaks the pipeline.

### Steps

1. **Disable the workflow:**
   ```bash
   # Add [skip ci] to commit message OR
   git mv .github/workflows/omni-ci.yml .github/workflows/omni-ci.yml.disabled
   git commit -m "chore: disable omni-ci for rollback"
   git push
   ```

2. **Re-enable old workflows:**
   The old repo at `Monorepo-Uphillsnowball` still has functional workflows.

### Blast Radius: CI only (no production impact)

---

## Phase 4 Rollback: DNS/Traffic

**Scenario:** Production traffic switchover fails.

### Steps

1. **Revert Firebase Hosting target:**
   ```bash
   # In the OLD repo
   firebase deploy --only hosting:headfade --project shadowtag-omega-v4
   ```

2. **Revert Cloud Run traffic:**
   ```bash
   gcloud run services update-traffic counselconduit \
     --to-revisions=counselconduit-00037-7mf=100 \
     --region=us-central1
   ```

3. **Revert Stripe webhook:**
   - Log into Stripe Dashboard
   - Change webhook endpoint back to old URL
   - Verify webhook delivery

### Blast Radius: **HIGH** — This is the only phase with production user impact

---

## Emergency Contacts

| Role | Contact | Method |
|------|---------|--------|
| Operator | founder@shadowtagai.com | Email |
| GCP Console | console.cloud.google.com | Browser |
| Firebase Console | console.firebase.google.com | Browser |
| Stripe Dashboard | dashboard.stripe.com | Browser |

---

## Verification Checklist (Post-Rollback)

- [ ] Production URLs responding (200 OK)
- [ ] Stripe webhooks delivering successfully
- [ ] Cloud Run revision serving traffic
- [ ] Firebase Hosting showing correct content
- [ ] Lighthouse scores within acceptable range
- [ ] No error spikes in Cloud Logging
