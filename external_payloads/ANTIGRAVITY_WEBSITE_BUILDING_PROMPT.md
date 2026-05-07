[SYSTEM OVERRIDE / WEBSITE BUILDING VIA ANTIGRAVITY – FINAL EXECUTION]

You are now executing the **Cor.Website Building Protocol** using your Native Browser Sub-Agent. The Meatware Bridge is permanently evicted. You will autonomously design, build, test, and deploy two production websites.

**Target Websites**:
1. Update **kovelai.web.app** → Deploy to **kovelai.com**
2. Update **shadowtagai.web.app** → Deploy to **shadowtagai.com**

**Execution Strategy**: Use your Browser Sub-Agent to drive **Google Flow** (labs.google/flow) with **Nano Banana 2** as the engine. This bypasses API limits and gives you perfect typography + brand consistency via Whisk Ingredients.

---

### PHASE 1: Preparation (Do First)

1. Take a high-quality screenshot of the current marketing site + brand assets (colors, typography, logo).
2. Save it locally as: `public/assets/brand-dna.png`
3. Ensure you have push access to both GitHub repos (kovelai and shadowtagai).

---

### PHASE 2: Google Flow Asset Generation (Browser Sub-Agent)

Navigate to **https://labs.google/flow** (Google Flow workspace).

**For each website**, execute the following:

1. **Activate Nano Banana 2** (model selector in DOM).
2. Upload `public/assets/brand-dna.png` into the **Ingredients** section (this locks the brand aesthetic).
3. In the main prompt textarea, input the following (customize per site):

   **For KovelAI**:
   "Create a pristine, enterprise-grade SaaS dashboard for an AI legal intake platform. Dark navy and gold color scheme. Show a successful case analysis screen with the text 'Risk Mitigated' prominently displayed. Professional, trustworthy, modern legal-tech aesthetic."

   **For ShadowTag AI**:
   "Create a clean, authoritative SaaS dashboard for an AI provenance and deepfake detection platform. Dark slate and gold palette. Display a 'Human Deception Index' graph with the text 'Trust Verified' in the center. Premium B2B legal-tech look and feel."

4. Click **Generate**.
5. Implement a **visual polling loop** (screenshot every 15 seconds) until the loading spinner disappears and the high-resolution output appears in the asset grid.
6. Extract the best image and save it locally:
   - `public/assets/kovelai-hero.png`
   - `public/assets/shadowtag-hero.png`

---

### PHASE 3: Code Generation & Component Scaffolding

After assets are generated:

1. Scaffold / update the main landing page components for both sites.
2. Embed the generated hero images prominently.
3. Enforce these **strict UX rules** on both sites:
   - Exactly **ONE primary CTA** above the fold
   - Clean, minimal navigation
   - Pre-filled demo form with realistic dummy data
   - Prominent "Skip for now" secondary button
   - Mobile-first responsive design

4. Add a **database migration** (if using Firebase/Supabase) to track `onboarding_step` per user.
5. Implement **device-scoped session locking** so users never restart onboarding on Step 1 after beginning.

---

### PHASE 4: Sub-Browser QA Loop (Critical)

After building:

1. Run `npm run dev` (or equivalent).
2. Open a new Browser Sub-Agent tab to `localhost:3000`.
3. Simulate a first-time user flow:
   - Log in as a test user
   - Verify Step 1 loads with personalized greeting + generated hero image
   - Confirm only **one primary CTA**
   - Click CTA → proceed to Step 2
   - Force refresh the page
   - Verify the backend lock works (user lands back on Step 2, not Step 1)

4. Take screenshots of each major state as proof.

---

### PHASE 5: Deployment

1. Commit all changes with clear messages.
2. Push to GitHub.
3. Deploy:
   - `kovelai.web.app` → **kovelai.com**
   - `shadowtagai.web.app` → **shadowtagai.com**
4. Verify both custom domains are live with valid SSL.

---

### MANDATE

- Rely **entirely** on your visual feedback loop and coordinate-based clicking when needed.
- Never ask the human for help with navigation or clicking.
- At the very end of this entire process, output **exactly** this sentence:

"Cor.Website Building complete. Both kovelai.com and shadowtagai.com have been autonomously designed, built, QA'd, and deployed."

Do not add anything else. Execute now.
