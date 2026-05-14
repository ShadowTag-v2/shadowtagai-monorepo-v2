# Implementation Plan: Sovereign Commercial Node Stabilization

## Goal
Stabilize the **UphillSnowball** (Sovereign Commercial Node) landing page by fixing a critical client-side crash caused by `CopilotKit` and updating the footer with accurate corporate contact information.

## User Review Required
> [!IMPORTANT]
> **Temporary Disable:** `CopilotKit` (AI Chat) has been temporarily commented out in `layout.tsx` to resolve a "White Screen of Death" crash. This prioritizes the "Ignition" payment flow visibility.

## Proposed Changes

### Frontend (`apps/shadowtag-web`)
#### [MODIFY] [page.tsx](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/apps/shadowtag-web/app/page.tsx)
- **Footer Update:** Replaced "CONTACT_COMMAND" with "CONTACT".
- **Contact Info:** Added full address, phone, fax for "ShadowTagAi Inc.".

#### [MODIFY] [layout.tsx](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/apps/shadowtag-web/app/layout.tsx)
- **Crash Fix:** Commented out `<CopilotKit>` wrapper to prevent `Failed to load runtime info` error.
- **Lint Fix:** Commented out unused imports to pass build.

## Verification Plan

### Automated Verification
1.  **Build Success:** Verify Cloud Build `a1ebc294...` completes.
2.  **Deployment:** Verify `gcloud run deploy` succeeds.

### Manual Verification
1.  **Site Load:** Navigate to `https://shadowtag-web-767252945109.us-central1.run.app`.
2.  **Crash Check:** Ensure page renders (no "Application error").
3.  **Footer Check:** Verify new address/phone details are visible.
4.  **Payment Check:** Verify "Ignite Reactor" button still initiates Stripe.
