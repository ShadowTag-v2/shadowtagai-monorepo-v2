# Walkthrough: Sentinel Gold Master v13.0

## Summary
Sentinel v13.0 is the **Sovereign OS**. It replaces the "God Model" with the **Ant Swarm** (RPI Loop) and enforcing truth via the **Ralph Loop** (Docker Verification). The UI has been updated to the "Tinted Void" aesthetic.

## Architecture

### 1. The Hive & Oxygen (`infra/main.tf`)
- **Cloud NAT:** "The Oxygen" allowing outbound access for isolated swarms.
- **N2 Workstations:** "The Hive" enabling Nested Virtualization for Docker-in-Docker.
- **Shadow Trap:** Traffic direction to isolate suspects.

### 2. The Brain (`kernel/swarm_server.py`)
- **RPI Loop:** Research -> Plan -> Implement agents with fresh context.
- **Ralph Loop:** `verifier_ant` runs `docker build` to prove code validity.
- **AG-UI:** Standardized event stream.

### 3. The Face (`web/`)
- **Tinted Void:** Electric Violet + Deepest Black (`tailwind.config.ts`).
- **Gucci Logo:** Grayscale by default, blooms green on hover (`page.tsx`).
- **Matrix Debugger:** Visualizes the raw AG-UI stream (`Cockpit.tsx`).

## Deployment

To launch the Sovereign Node:

```bash
cd apps/sentinel
make up
```

## Validation
- **Syntax:** Python kernel verifies successfully.
- **Config:** Terraform includes N2/NAT resources.
- **Protocol:** Code implements the RPI loop explicitly.
- **Visual:** Landing page updated with "Never Resting, Ever Resting".
  ![Landing Page Verification](/Users/pikeymickey/.gemini/antigravity/brain/dc6d20af-2131-4f3d-b5b7-d446f55d0ab1/landing_page_check_1770690689436.png)
- **Aesthetic Upgrade (Gucci-Tier):** Updated to "Bio-Digital" aesthetic with Rich Void/Growth Green palette and "Sovereign Shield" layout.
  ![Bio-Digital Verification](/Users/pikeymickey/.gemini/antigravity/brain/dc6d20af-2131-4f3d-b5b7-d446f55d0ab1/localhost_homepage_1770690866749.png)
- **Footer Text Verified:** Updated copyright to "Never Resting, Ever Vesting".
  ![Footer Verification](/Users/pikeymickey/.gemini/antigravity/brain/dc6d20af-2131-4f3d-b5b7-d446f55d0ab1/footer_check_1770690963470.png)
- **Corporate Blue Refinement:** Verified Dark Blue background, Light Blue text, and Center-Justified layout on `localhost:3002`.
  ![Corporate Blue Initial](/Users/pikeymickey/.gemini/antigravity/brain/dc6d20af-2131-4f3d-b5b7-d446f55d0ab1/localhost_3002_initial_1770693161443.png)
  ![Contact Modal](/Users/pikeymickey/.gemini/antigravity/brain/dc6d20af-2131-4f3d-b5b7-d446f55d0ab1/contact_info_modal_1770693181838.png)
- **Mountain View Minimalist Pivot:** Verified Deep Navy background, Search Engine layout, and Judge 6 content on `localhost:3002`.
  ![Contact Revealed](/Users/pikeymickey/.gemini/antigravity/brain/dc6d20af-2131-4f3d-b5b7-d446f55d0ab1/contact_info_revealed_1770694301772.png)
- **Elegance & Copy Refinement:** Verified "HIPAA" correction, Judge 6 Grid, and Full Contact Dossier on `localhost:3002`.
  ![Contact Dossier](/Users/pikeymickey/.gemini/antigravity/brain/dc6d20af-2131-4f3d-b5b7-d446f55d0ab1/contact_page_verified_1770694698327.png)
- **Logo & Motto Refinement:** Verified new Neon Leaf Logo and "Never Resting, Ever Vesting" motto on `localhost:3002`.
  ![Logo & Motto](/Users/pikeymickey/.gemini/antigravity/brain/dc6d20af-2131-4f3d-b5b7-d446f55d0ab1/verification_localhost_3002_1770695853081.png)
- **Layout Refactor (Phase 3.10):**
  - **Top Half:** Dedicated Hero section for the Logo (50vh).
  - **Bottom Half:** Value proposition and Judge 6 grid.
  - **Contact Page:** Dedicated view with "High Clearance" padding to avoid ReCAPTCHA badge overlap.
  - **Aesthetic:** "Full Page Superimposed Logo" with blend mode fix for checkerboard artifacts and transparency through text blocks.
  ![Final Logo Layout](/Users/pikeymickey/.gemini/antigravity/brain/dc6d20af-2131-4f3d-b5b7-d446f55d0ab1/landing_page_full_1770940976381.png)
  ![Logo Transparency Detail](/Users/pikeymickey/.gemini/antigravity/brain/dc6d20af-2131-4f3d-b5b7-d446f55d0ab1/landing_page_logo_transparency_1770941048656.png)
- **Omega Loop (Phase 4):** "Linear / Vercel" UI Overhaul.
  - **Deep Navy Void:** Replaced gradients with `bg-[#02040A]`.
  - **Glassmorphism:** Implemented `backdrop-blur-xl` and `bg-white/[0.03]` for all panels.
  - **Substrate Logo:** Positioned the solid black logo with `mix-blend-screen` to create a glowing background watermark.
  ![Top View Logo Glow](/Users/pikeymickey/.gemini/antigravity/brain/dc6d20af-2131-4f3d-b5b7-d446f55d0ab1/top_view_logo_glow_1770943488445.png)
  ![Corrected Purple/Green Logo (Slanted)](/Users/pikeymickey/.gemini/antigravity/brain/dc6d20af-2131-4f3d-b5b7-d446f55d0ab1/slanted_logo_v3_1770961867467.png)
- **Branding Update:** Changed name from "ShadowTag Omega" to "ShadowTagAi" in site metadata.
  ![Verified Site Title](/Users/pikeymickey/.gemini/antigravity/brain/dc6d20af-2131-4f3d-b5b7-d446f55d0ab1/shadowtagai_homepage_1771006687464.png)
- **Production Deployment:** Verified live site `shadowtag-web` with new assets.
  * *Note: `uphillsnowball` service was deprecated/deleted; `shadowtag-web` is the active production target.*
- **Sovereign Shield (Phase 8):**
  - **Optimization:** Reduced deployment context from 17GB to 715KB via `.gcloudignore`.
  - **Defense:** Integrated ReCAPTCHA Enterprise (Server-side verification) and created Cloud Armor WAF policy `sovereign-shield-policy`.
  - **Debug:** Resolved `npm ci` build failure by whitelisting `package-lock.json`. Resolved 500 API error by granting `recaptchaenterprise.assessmentCreator` IAM role.
