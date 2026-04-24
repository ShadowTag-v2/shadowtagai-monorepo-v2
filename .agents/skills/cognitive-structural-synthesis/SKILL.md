---
name: cognitive-structural-synthesis
description: "End-to-end workflow for structural cloning, Google Design MCP semantic extraction, the 11x Deep Browser Extraction loop, and Cognitive Suite injection. V4 — MCP-native + browser deep-extraction."
---

# Cognitive Structural Synthesis (V4)

## Ground Truth: Google Design MCP

> **CRITICAL:** The design specification authority is the Google Design MCP server at `https://design.googleapis.com/mcp`.
> There is NO `google-labs-code/design.md` GitHub repo. There is NO `@google-labs/design-cli` npm package.
> Phase 0 (Git clone) is **PERMANENTLY ABANDONED**.

### MCP Server Configuration

```json
{
  "google-design": {
    "command": "<node_path>",
    "args": ["<mcp-remote-path>", "https://design.googleapis.com/mcp", "--header", "X-Goog-Api-Key: ${GOOGLE_DESIGN_API_KEY}"]
  }
}
```

### Available Tools (7 Total)

| Tool | Input | Output | Purpose |
|------|-------|--------|---------|
| `generate_brand_color_scheme` | `{neutralKey, primaryKey, secondaryKey, tertiaryKey}` hex values | Unified color scheme JSON | Generate mathematically consistent brand palette |
| `extract_brand_colors_from_image` | Base64-encoded image | Array of hex colors | Extract background + accent colors from screenshot |
| `extract_and_generate_brand_color_scheme` | Base64-encoded image | Full brand color scheme JSON | Combined: extract → generate in one call |
| `search_icons` | Keywords describing usage/style/shape | Matching Material icons | Find Material Design icons |
| `icons_instructions` | None | Usage instructions | Get Material Icons/Symbols web integration guide |
| `search_fonts` | Categories and/or languages | Matching font families | Font discovery |
| `describe_font` | Font family name | Detailed description | Font metadata, weights, usage instructions |

---

## The Holy Trinity Pipeline

Three enterprise systems form an immutable validation chain. No code commits without all three passing.

```
┌─────────────────────┐     ┌──────────────┐     ┌─────────────────┐
│ Google Design MCP   │────▶│  Bandit       │────▶│  Lighthouse CI  │
│ (Visual Correctness)│     │  (Security)   │     │  (Performance)  │
│                     │     │              │     │                 │
│ • Color math        │     │ • B310 SSRF   │     │ • Perf ≥ 70     │
│ • WCAG contrast     │     │ • URL schemes  │     │ • A11y ≥ 90     │
│ • Font validation   │     │ • Injection    │     │ • SEO  ≥ 80     │
│ • Material icons    │     │ • Secrets      │     │ • BP   ≥ 80     │
└─────────────────────┘     └──────────────┘     └─────────────────┘
```

---

## The Pipeline (7 Phases)

### Phase 1: Structural Scrape

Execute `execute_headless_structural_clone`:
1. Use Chrome DevTools MCP `navigate_page` to load target URL
2. Wait for full JS execution — scroll to bottom, trigger lazy-load
3. `take_snapshot` — full-page accessibility tree
4. `take_screenshot(fullPage: true)` — pixel-perfect capture for color extraction
5. `evaluate_script` — extract all computed styles, grid geometry, font stacks
6. Save DOM structure with element dimensions for geometric constraint mapping

**Fallback:** If Chrome DevTools MCP is unavailable:
```python
from scrapling import Fetcher
page = Fetcher().get(url, headless=True, wait=10)
```

### Phase 2: Security Gate (Bandit)

```bash
/opt/homebrew/bin/python3.14 -m bandit -r ./clone-base --skip B101 -ll
```

- URL fetching logic must pass B310 audit
- Apply `# nosec B310` ONLY to intentional scraper targets with validated URL construction
- Any unresolved Medium+ findings **block** Phase 3

### Phase 3: Design Archaeology via Google Design MCP

Transform scraped CSS into semantic DESIGN.md using the MCP tools:

1. **Color Extraction:** Call `extract_and_generate_brand_color_scheme` with the fullPage screenshot (base64)
2. **Role Mapping:** Map the MCP response to semantic roles:
   - `primary` → main accent / CTA color
   - `neutral` → canvas / background color
   - `secondary` → supporting accent
   - `tertiary` → status/signal color
   - `error` → error states (derive from warm hue)
3. **Font Resolution:** Call `describe_font` for each font-family found in computed styles
4. **Icon Discovery:** Call `search_icons` for any icon elements found in the DOM
5. **Output:** Generate `.stitch/DESIGN.md` with strictly compliant tokens (Tokens = Roles)

### Phase 4: MCP-Driven WCAG Auto-Correction

1. Extract all text-on-background color pairs from the generated DESIGN.md
2. Calculate contrast ratios (WCAG AA = 4.5:1, AAA = 7:1)
3. For any failing pair:
   - Adjust lightness by minimum delta to hit 4.5:1
   - Preserve hue and saturation
   - Re-validate via `generate_brand_color_scheme` (pass corrected hex values)
4. Run `chrome-devtools-mcp` `lighthouse_audit` to confirm accessibility score ≥ 0.9

### Phase 5: The 11x Deep Extraction Loop (Research Phase)

> **V4 Addition:** Before writing copy, execute `execute_deep_browser_expansion` to mine exhaustive context.

1. **Navigate:** Use `search_web` or Chrome DevTools MCP to open Google and enter the product concept query.
2. **AI Mode Expansion:** Navigate to Google's AI Mode tab. Auto-send the exact string "yes" 11 times, waiting for full generation between each prompt.
   - 9x fully develops the answer; 11x provides a safety buffer for complete latent space exhaustion.
3. **Capture:** Scrape the final, fully-developed text payload using `take_snapshot` / `evaluate_script`.
4. **Return:** Feed the deep-extracted context into Phase 6 as the content source.

> **Rationale:** Standard API calls return truncated summaries. By automating the Chrome UI to repeatedly confirm expansion, the underlying model fully unrolls its chain-of-thought, yielding an exhaustive research payload that dramatically improves copy quality.

### Phase 6: Hollow & Inject (Cognitive Suite)

Trigger `orchestrate_cognitive_injection`:

1. **Geometric Constraint Mapping:**
   - Measure all `<img>` and `<video>` element dimensions from Phase 1 snapshot
   - Count character limits per text container (width ÷ avg char width)
   - Map grid column/row ratios
2. **Content Generation (Constrained):**
   - **Copy:** Feed the Phase 5 deep-extracted payload to Mariner & Flow — segmented to exact character limits
   - **Imagery:** Use `generate_image` tool with exact pixel dimensions from layout
   - **Video:** Reference Veo 3.1 specs for hero media constraints
3. **Color Mutation:** Replace DESIGN.md color roles with new brand colors, then apply via Stitch MCP `apply_design_system`
4. **All generated assets MUST inherit the color palette validated by Google Design MCP in Phase 4**

### Phase 7: Assembly & Lighthouse Gate

1. Use Stitch MCP `edit_screens` to replace content
2. Export final code via Stitch MCP `get_screen`
3. Run Lighthouse CI validation:
   ```bash
   lhci autorun
   ```
4. **Gate criteria (from `.lighthouserc.json`):**
   - Performance ≥ 70 (warn)
   - Accessibility ≥ 90 (error — hard gate)
   - Best Practices ≥ 80 (warn)
   - SEO ≥ 80 (warn)
5. **Only commit to staging if all gates pass**

---

## Tool Schemas

### Tool E: Headless Structural Scraper

```json
{
  "name": "execute_headless_structural_clone",
  "description": "Uses Chrome DevTools MCP to capture a 1:1 structural clone including full-page screenshot, accessibility snapshot, and DOM geometry.",
  "parameters": {
    "type": "object",
    "properties": {
      "target_url": {"type": "string", "description": "The live URL to clone."},
      "output_directory": {"type": "string", "default": "./clones/"}
    },
    "required": ["target_url"]
  },
  "implementation": "chrome-devtools-mcp: navigate_page → take_snapshot → take_screenshot(fullPage) → evaluate_script(extract computed styles)"
}
```

### Tool F: Cognitive Suite Orchestrator

```json
{
  "name": "orchestrate_cognitive_injection",
  "description": "Chains Google Design MCP + Stitch MCP to generate multimedia assets constrained to fit a cloned HTML shell's geometry.",
  "parameters": {
    "type": "object",
    "properties": {
      "target_directory": {"type": "string"},
      "new_product_pitch": {"type": "string"},
      "design_md_path": {"type": "string"}
    },
    "required": ["target_directory", "new_product_pitch"]
  },
  "implementation": "Google Design MCP (color scheme) → Stitch MCP (screen generation) → generate_image (constrained assets)"
}
```

### Tool G: Deep Browser Context Extractor

```json
{
  "name": "execute_deep_browser_expansion",
  "description": "Drives a headless/visible Chrome browser to extract hyper-developed research via Google's AI Mode tab utilizing an 11-step prompt expansion loop.",
  "parameters": {
    "type": "object",
    "properties": {
      "initial_query": {
        "type": "string",
        "description": "The base research query for the product pitch."
      }
    },
    "required": ["initial_query"]
  },
  "system_instruction": "Use Chrome DevTools MCP or Playwright. 1) Navigate to https://www.google.com/. 2) Enter initial_query. 3) Wait for response to post. 4) Navigate to the far-left 'ai mode' tab and click it. 5) Auto-prompt the exact string 'yes' 11 times in succession, waiting for the generation to finish each time. (9x fully develops the answer; 11x provides a safety buffer). 6) Return to view and scrape the final, fully-developed text payload. 7) Return data to context."
}
```

---

## Owned Properties (Mission A Targets)

| Property | URL | DESIGN_SYSTEM.md Location | Design Language |
|----------|-----|--------------------------|-----------------|
| ShadowTag AI | shadowtagai.web.app | `apps/shadowtagai/DESIGN_SYSTEM.md` | Kinetic Void |
| KovelAI | kovelai.web.app | `apps/kovelai/DESIGN_SYSTEM.md` | Structured Precision |

## Anti-Patterns (FORBIDDEN)

- ❌ `git clone` of any `design.md` or `design-cli` repository (does NOT exist)
- ❌ `npx @google-labs/design-cli` or any local CLI (does NOT exist)
- ❌ Generating CSS from memory — ALWAYS scrape first, then validate via MCP
- ❌ Generating images without geometric constraints from source layout
- ❌ Generating copy without character-count limits from source containers
- ❌ Skipping WCAG contrast validation before Assembly phase
- ❌ Committing without Lighthouse gate passing
- ❌ Using `search_web` for design tokens (use `google-design` MCP)
- ❌ Writing copy without running the 11x Deep Extraction Loop first
- ❌ Truncating AI Mode responses before the 11th confirmation
