---
name: cognitive-structural-synthesis
description: End-to-end workflow for structural cloning, utilizing the Google Design MCP for semantic extraction, running Bandit/Lighthouse validations, and injecting a Cognitive Suite product pitch.
---
# Cognitive Structural Synthesis (V3)

## The Pipeline
**1. Structural Scrape:** Run `execute_headless_structural_clone` to download the 1:1 HTML shell.
**2. Security Gate (Bandit):** Run `bandit -r ./clone-base`. Ensure URL fetching logic safely handles B310 warnings (apply `# nosec B310` or inline exceptions to intentional scraper targets).
**3. Design Archaeology via Google Design MCP:**
   - Call the `google-design` MCP server tools. Pass it the scraped CSS.
   - Instruct the MCP server to output a strictly compliant `DESIGN.md` file (Tokens = Roles).
**4. MCP-Driven Auto-Correction:** Use the MCP tools to validate WCAG contrast. Adjust the hex frontmatter based on the MCP's structured JSON response until validation passes.
**5. Hollow & Inject:** Trigger `orchestrate_cognitive_injection` (Mariner, Flow, Opal, Whisk, Labs FX, Veo 3.1) to compile new assets perfectly constrained to the layout geometry. Ensure generated assets inherit the color palette validated by the `google-design` MCP.
**6. Assembly & Lighthouse Gate:** Weave assets into the HTML shell. Run Lighthouse CI (`lhci autorun`). You may only commit to staging if Performance, A11y, and SEO scores remain >= 90.
