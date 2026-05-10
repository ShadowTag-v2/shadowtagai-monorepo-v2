# POMELLI_ONBOARDING_PROMPT.md

**Version**: 1.0 – Final  
**Date**: May 6, 2026

---

## Ready-to-Paste Prompt for Antigravity (Pomelli Onboarding)

```text
[SYSTEM OVERRIDE / POMELLI BRAND SYNC & GTM ASSET FORGE – FINAL]

The Meatware Bridge remains evicted. We are now in full Go-To-Market (GTM) execution mode.

You will use Pomelli (https://labs.google.com/u/0/pomelli/onboarding), Google’s unified AI marketing engine, to extract HeadFade’s Business DNA and generate brand-locked GTM assets.

**Strategic Alignment Confirmed**:  
Pomelli will be used exclusively to synthesize and scale **HeadFade’s proprietary brand DNA** (Navy/Slate/Gold palette, Inter typography, authoritative legal-tech tone focused on “United States v. Heppner” risk mitigation), not any external reference site.

Execute the Antigravity Native Browser Loop with the following Pomelli-specific parameters:

1. Deploy for Pomelli Scan (The Public DNA Vector)
   - Pomelli cannot scan localhost. First, use your terminal and Firebase MCP to deploy the current production build (or chassis-preview.html) to our public Firebase Hosting URL so Pomelli has a live target to scrape.

2. Pomelli Onboarding & DNA Extraction Loop
   - Navigate your Native Browser Subagent to https://labs.google.com/u/0/pomelli/onboarding.
   - [VISUAL GUARDRAIL]: Pomelli uses heavily obfuscated React/Canvas UIs. Do not rely on standard DOM selectors. Use take_screenshot to map the UI, then use coordinate-based X/Y clicking via evaluate_script to paste the live deployed Firebase URL into the input field and click “Continue”.
   - [LONG POLLING LOOP – CRITICAL]: Pomelli can take up to 8 minutes to analyze the site and extract Business DNA. Implement a long visual polling loop — take a screenshot every 60 seconds. Do not timeout. Wait patiently until the “Business DNA” dashboard fully loads and confirms it captured our Navy/Slate/Gold palette and Inter typography.

3. Autonomous Campaign Generation
   - Once the Business DNA is locked, visually navigate to the campaign generator.
   - Prompt Pomelli with:  
     "B2B SaaS launch campaign targeting Law Firm Partners. Focus on eliminating the risk of United States v. Heppner by providing a secure, 24/7 AI intake portal. Use authoritative, prestigious language."
   - Use Pomelli’s integrated features (Photoshoot / Animate) to generate photorealistic imagery and short motion graphics that perfectly match our extracted Business DNA.

4. Pipeline Egress & Commit
   - Visually poll until the renders finish and download buttons appear. Click them via coordinate targeting.
   - Use your bash terminal to move the downloaded .mp4, .png, and any zip files from the system Downloads folder into apps/headfade/public/marketing/ (create the directory if it doesn’t exist).
   - Run f1 gca to commit the new marketing assets to the repo.

MANDATE: Rely entirely on your visual feedback loop to navigate Pomelli’s Shadow DOMs. Manage the long timeout during DNA extraction gracefully. Extract the GTM assets, sync the codebase, and end your final response with exactly this sentence:

"Pomelli Business DNA extracted. GTM campaigns generated and synchronized."

Do not add a menu. Go.
```

---

**How to Use**

1. Open **Antigravity** (with full Browser Subagent + Firebase MCP + terminal access).
2. Paste the entire prompt above.
3. Antigravity will:
   - Deploy the site to Firebase
   - Complete Pomelli onboarding + Business DNA extraction (with long polling)
   - Generate brand-locked marketing assets
   - Download and commit everything

**End of Final Pomelli Onboarding Prompt**
```