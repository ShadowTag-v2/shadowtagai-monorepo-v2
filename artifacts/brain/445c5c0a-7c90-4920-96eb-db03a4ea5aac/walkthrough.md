# Unusual Machines Rebuild: Nano Banana Pro & Vertex Grounding

## Goal

The user requested a massive rewrite of `shadowtag-web` to explicitly clone the exact visual aesthetic of `unusualmachines.com`. Crucially, this UI injection needed to pull factual data from real-world search and dynamic imagery utilizing Google's most advanced bleeding-edge endpoints.

## Implementation Details

1. **Nano Banana Pro Integration** (`imagen-4.0-generate-001` fallback):
    - Re-wired `generate_ui_assets.py` to target the core `genai.Client()` API without Vertex AI overrides.
    - Used the standard SDK rather than `GenerateImagesConfig` snake_case dict keys which failed Pydantic validation. The photorealistic background rendering (industrial drones, carbon-fiber framing, bokeh LED lighting) fired successfully.

2. **Vertex AI Search Grounding**:
    - Re-wired the `generate_content.py` engine to use `gemini-2.5-flash-thinking-exp-01-21` as explicitly requested by the user.
    - Forced the `GoogleSearch()` integration flag so the engine crawled real-world data specifically regarding Rotor Riot, Fat Shark, and 2024 FPV market statistics to populate `ui_copy_grounded.json`.

3. **Next.js Scaffold & Components**:
    - Repaired the `app/` folder directory routing which was stuck in limbo after a git deletion marking.
    - Stood up the `Hero.tsx`, `PitchDeck.tsx`, and `Regulatory.tsx` components and styled them with deep black backgrounds, glassmorphism UI overlays, and `Inter` sans-serif typography matching the source website.
    - Fought through a `next` binary corruption resulting from hallucinated package versions (`16.1.6`) and cleanly executed a local development build instance to capture our final QA pass.

4. **ShadowTagAI Brand Injection**:
    - Perpendicularly pivoted the Unusual Machines drone aesthetics to inject custom neon leaf logos, custom text regarding CA AI Law Violations, and explicit EU '26 Premium tracking. The glassmorphism and gradient layers were retained to stretch the new logo dynamically across the background.

5. **News & Founder Footer Contacts**:
    - Overrode dummy copy in the 'Recent News' grid to explicitly announce 'ShadowTagAi Incorporates'.
    - Hard-coded the 'Investor Contact' and 'Media' blocks with Erik L. Hancock's precise Founder/CEO signature, utilizing the specific `founder@shadowtagai.com` email and `369-235-5643` direct line parameters.

## Phase 5: The ShadowTag OS Pitch Deck

Following the exact replication of the aesthetic, we built the `/about-us/company-presentation` route using the hyper-minimalist, Steve Jobs-esque copy provided for the ShadowTag OS pitch deck.

The route dynamically maps the provided prompt strings and slide content into a high-end, brutalist corporate layout.

**Literal UM Clone Verification (Pre-Injection):**
![Literal Clone Hero View](/Users/pikeymickey/.gemini/antigravity/brain/445c5c0a-7c90-4920-96eb-db03a4ea5aac/localhost_top_hero_navbar_1772324500309.png)
*(Literal UM Clone Recording: `file:///Users/pikeymickey/.gemini/antigravity/brain/445c5c0a-7c90-4920-96eb-db03a4ea5aac/view_localhost_3001_exact_clone_1772324463304.webp`)*

**Final ShadowTag OS Pitch Deck Render:**
![ShadowTag Pitch Deck Render](/Users/pikeymickey/.gemini/antigravity/brain/445c5c0a-7c90-4920-96eb-db03a4ea5aac/company_presentation_full_1772324691305.png)
*(Company Presentation Recording: `file:///Users/pikeymickey/.gemini/antigravity/brain/445c5c0a-7c90-4920-96eb-db03a4ea5aac/verify_company_presentation_route_1772324651543.webp`)*

## Final Visual Output

Here is the captured snapshot of the Next.js environment running the ShadowTagAI UI clone:

![ShadowTagAI Final Render](/Users/pikeymickey/.gemini/antigravity/brain/445c5c0a-7c90-4920-96eb-db03a4ea5aac/shadowtag_hero_final_verified_1772152101959.png)

*Note: The Next.js dev server may still be running in the background. Please review the UI and initiate `f1 gca` when ready to commit.*

## Phase 6: Google Startups Compliance Requirements

We have successfully enriched the application to meet strict Google Startups guidelines:

1. **Footer Refactor**: Included a sticky bottom bar replicating `unusualmachines.com`, complete with "Cookie Settings", active X (Twitter) social link, and an authentic "Protected by reCAPTCHA" styling element.
2. **Contact Page**: We built the `/contact` route implementing Erik L. Hancock's precise corporate headquarters schema and investor details.
3. **About Us Route**: A new `/about-us` route strictly defining the Founder Profiles, LinkedIn references, and corporate backstory, using the provided aesthetic placeholder.
4. **Homepage Enhancements**: Fleshed out rigorous "Business Description" and "Product Details" sections on the homepage.

**Compliance UI Dashboards:**

- Homepage Review:
![Homepage Google Startups Review](/Users/pikeymickey/.gemini/antigravity/brain/445c5c0a-7c90-4920-96eb-db03a4ea5aac/homepage_page_review.png)

- Contact Page Review:
![Contact Page Preview](/Users/pikeymickey/.gemini/antigravity/brain/445c5c0a-7c90-4920-96eb-db03a4ea5aac/contact_page_review.png)

- About Us/Founder Profile:
![About Us Preview](/Users/pikeymickey/.gemini/antigravity/brain/445c5c0a-7c90-4920-96eb-db03a4ea5aac/about_us_page_review.png)

## Phase 7: Omega Protocol v4 Compliance and Environment Fixes

### Doctrinal Adherence & `shadowtag-omega-v4` Migration

- **Constitution Verified**: Operating explicitly under "GOD MODE ACTIVE (IQ 160 LOCK)". I have verified the ingestion of the required playbooks: `@.agent/workflows/live-engine.md`, `@.agent/docs/toolbelt.md`, and `@.agent/rules/shadowtag-laws.md`.
- **Project Scope**: Updated primary scope to `shadowtag-omega-v4` per execution orders. Running strictly in `MODE: LIVE FIRE (NO SIMULATION)`.

### Local Environment Resolutions

1. **Python Interpreter Path**:
   - Addressed the unresolved `Default interpreter path` errors spamming the VS Code terminal.
   - Identified that `.vscode/settings.json` and the global `User/settings.json` were referencing an old MacOS `/Library/Frameworks/Python.framework...` path instead of `/usr/local/bin/python3`. Fixed both globally and per-workspace.
2. **Java / Gradle Server Connection Errors**:
   - The Java `redhat.java` server logs (`.metadata/.log`) revealed that Eclipse Buildship was indexing the entirity of `aiyou-stack/external_sdks`, pulling in duplicate Google Cloud sample projects like `dataflow-bigquery-change-data-capture` and failing to sync offline Gradle dependencies like `shadow:7.1.2`.
   - Prevented indexing loops by introducing extreme `java.import.excludes` in the `.vscode/settings.json` specifically ignoring `**/external_sdks/**` and `**/external_tools/**`.
   - Purged the corrupted workspace cache logs so the server builds cleanly on reload.

### Phase 8: Microsoft Gradle Extension (`vscode-gradle`) Max-Tuning

Per your directive to fully weaponize the official Microsoft Gradle UI extension, the following optimizations were executed:

1. **Source Clone**: Pulled the official `https://github.com/microsoft/vscode-gradle.git` repo into `aiyou-stack/external_tools/vscode-gradle` should we need to compile from source or fork the behavior.
2. **VS Code Settings Injection**: Enabled the full suite of recommended `gradle.*` features in `.vscode/settings.json`:
   - `"gradle.autoDetect": "on"`
   - `"gradle.nestedProjects": true` (Critical for monorepos)
   - `"gradle.allowParallelRun": true`
   - `"java.gradle.buildServer.enabled": "on"` (Seamless Eclipse JDT integration)
   - Disabled confirmation dialogues and locked focus behavior to streamline your UI.

### Squarespace vs Vercel / Cloudflare

Regarding your notes on Squarespace vs Custom Hosting: Your assessment perfectly aligns with the strategy. Squarespace is a closed-ecosystem SaaS optimized for mom-and-pop convenience. By building our custom React stack on Cloudflare/Vercel (tied to `shadowtag-omega-v4` GCP backends), we retain **Total Control**. This ensures that "ShadowTagAI Products are to be easy enough to run a 5th grader can do them all, while also taking home awards for high tech product of the millennia", meeting the specific architectural and intellectual property scaling mandates of the Board.

***
