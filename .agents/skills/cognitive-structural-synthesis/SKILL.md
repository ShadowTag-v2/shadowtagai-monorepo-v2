---
name: cognitive-structural-synthesis
description: End-to-end structural cloning using the JCodesMore engine, Google Design MCP semantic extraction, Bandit/Lighthouse validations, and Cognitive Suite (Veo 3.1) cinematic injection.
---
# Cognitive Structural Synthesis (V4)

## The Pipeline
**1. Structural Scrape:** Run `execute_headless_structural_clone` using the `tools/cloner-engine/template` to download the 1:1 HTML shell.
**2. Security Gate:** Run `bandit -r ./clone-base`. Ensure URL fetching safely handles B310 warnings.
**3. Design Archaeology via Google Design MCP:**
   - Call `google-design` MCP server tools. Pass scraped CSS.
   - Output a compliant `DESIGN.md` file (Tokens = Roles).
**4. Auto-Correction:** Use MCP tools to validate WCAG contrast.
**5. Cinematic Injection:** Trigger `orchestrate_cognitive_injection`. Replace math-based CSS physics with full-bleed HTML5 `<video>` backgrounds (Veo 3.1/Whisk placeholders) and `atmospheric-glass` (`#050505`/`#020408` with 90%+ opacity) overlays. Ensure Elite Legal-Tech copy is injected.
**6. Assembly & Lighthouse Gate:** Weave assets into the HTML shell. Run Lighthouse CI (`lhci autorun`).
