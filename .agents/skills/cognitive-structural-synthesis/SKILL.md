---
name: cognitive-structural-synthesis
description: End-to-end workflow for structurally cloning a target website, reverse-engineering its DESIGN.md semantic spec using the Google Design MCP (design.googleapis.com/mcp), and injecting a new product pitch using Stitch MCP and the Google External Cognitive Suite.
---

# Cognitive Structural Synthesis

## When to Use This Skill

1. **Design Archaeology:** When asked to generate a `DESIGN.md` for live owned properties (ShadowTagAI, KovelAI).
2. **Structural Hijacking:** When cloning a site and replacing branding/content with a new product pitch while preserving JS layouts.
3. **Brand Color Extraction:** When extracting color palettes from screenshots or existing sites.
4. **WCAG Auto-Correction:** When auditing and fixing accessibility contrast violations in design tokens.

## Ground Truth: Google Design MCP

The canonical design spec authority is **NOT** a GitHub repository.
It is the Google Design MCP server at `https://design.googleapis.com/mcp`.

### Available Tools (Ground Truth)

| Tool | Purpose |
|------|---------|
| `generate_brand_color_scheme` | Generate unified color scheme from hex inputs (neutralKey, primaryKey, secondaryKey, tertiaryKey) |
| `extract_brand_colors_from_image` | Extract background + accent colors from base64-encoded image |
| `extract_and_generate_brand_color_scheme` | Combined: extract from image → generate full scheme |
| `search_icons` | Find Material Design icons by keyword |
| `icons_instructions` | Get Material Icons/Symbols usage instructions |
| `search_fonts` | Find fonts by category/language |
| `describe_font` | Get detailed font family description |

### Usage Pattern

```bash
# List all available tools
curl --location 'https://design.googleapis.com/mcp' \
  --header 'content-type: application/json' \
  --header 'accept: application/json, text/event-stream' \
  --data '{ "method": "tools/list", "jsonrpc": "2.0", "id": 1 }'

# Generate color scheme from brand colors
curl --location 'https://design.googleapis.com/mcp' \
  --header 'content-type: application/json' \
  --data '{
    "method": "tools/call",
    "jsonrpc": "2.0",
    "id": 2,
    "params": {
      "name": "generate_brand_color_scheme",
      "arguments": {
        "neutralKey": "#0a0f1e",
        "primaryKey": "#c9a96e",
        "secondaryKey": "#8da3be",
        "tertiaryKey": "#4caf80"
      }
    }
  }'
```

## The Pipeline

### Phase 0: Ground Truth Alignment

Before writing any DESIGN.md color tokens, call the Google Design MCP:
1. Screenshot the target site (use `chrome-devtools-mcp` `take_screenshot`)
2. Call `extract_and_generate_brand_color_scheme` with the base64 screenshot
3. Use the returned scheme as the canonical color roles

### Phase 1: Structural Scrape

Execute `execute_headless_structural_clone`:
1. Use Chrome DevTools MCP to navigate to the target URL
2. Wait for full JS execution (scroll to bottom, lazy-load triggers)
3. Take a full-page accessibility snapshot (`take_snapshot`)
4. Capture full-page screenshot for color extraction
5. Save the DOM structure for geometric analysis

**Fallback:** If Chrome DevTools MCP is not available, use Scrapling:
```python
from scrapling import Fetcher
page = Fetcher().get(url, headless=True, wait=10)
```

### Phase 2: Design Archaeology (The Translation Bridge)

Translate scraped hardcoded CSS into semantic DESIGN.md:

1. **Extract Raw Tokens:** Parse CSS custom properties, hex codes, font-family declarations, spacing values
2. **Map to Semantic Roles:**
   - `primary` = main accent / CTA color
   - `neutral` = canvas / background color
   - `secondary` = supporting accent
   - `tertiary` = status/signal color
   - `error` = error states
3. **Generate DESIGN.md:** Using Stitch MCP `create_design_system` or `update_design_system`, create a design system that maps to these roles
4. **Font Resolution:** Use Google Design MCP `describe_font` to get canonical font metadata

### Phase 3: WCAG Auto-Correction

1. Extract all text-on-background color pairs from the DESIGN.md
2. Calculate contrast ratios (WCAG AA = 4.5:1, AAA = 7:1)
3. For any failing pair:
   - Lighten text or darken background by minimum delta to hit 4.5:1
   - Preserve hue and saturation, adjust only lightness
   - Update the DESIGN.md frontmatter with corrected hex values
4. Run Lighthouse accessibility audit via `chrome-devtools-mcp` `lighthouse_audit`

### Phase 4: Hollow & Inject (Cognitive Suite)

For structural hijacking (replacing branding while preserving layout):

1. **Geometric Constraint Mapping:**
   - Measure all `<img>` and `<video>` element dimensions from the snapshot
   - Count character limits per text container
   - Map grid column/row ratios
2. **Content Generation (Constrained):**
   - **Copy:** Use Google AI Mode / Deep Research to generate market copy segmented to exact character limits
   - **Imagery:** Use `generate_image` tool with exact pixel dimensions matching placeholder aspect ratios
   - **Video:** Reference Veo 3.1 specs from `.stitch/kovelai-hero-video-spec.md` for hero media constraints
3. **Color Mutation:** Change DESIGN.md color roles to new brand, then apply via Stitch MCP `apply_design_system`

### Phase 5: Assembly

1. Use Stitch MCP `edit_screens` to replace content in generated screens
2. Export final code via Stitch MCP `get_screen` (fetch HTML/CSS)
3. Validate structure preserved by comparing DOM tree depth/breadth

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
  "implementation": "Uses chrome-devtools-mcp navigate_page → take_snapshot → take_screenshot (fullPage: true) → evaluate_script (extract computed styles)"
}
```

### Tool F: Cognitive Suite Orchestrator

```json
{
  "name": "orchestrate_cognitive_injection",
  "description": "Interfaces with Google Design MCP + Stitch MCP to generate multimedia assets constrained to fit a cloned HTML shell's aspect ratios and character limits.",
  "parameters": {
    "type": "object",
    "properties": {
      "target_directory": {"type": "string", "description": "Path to the cloned data."},
      "new_product_pitch": {"type": "string", "description": "The concept for the new product to inject."},
      "design_md_path": {"type": "string", "description": "Path to the semantic DESIGN.md blueprint."}
    },
    "required": ["target_directory", "new_product_pitch"]
  },
  "implementation": "Google Design MCP (color scheme) → Stitch MCP (screen generation) → generate_image (constrained assets)"
}
```

## Owned Properties (Mission A Targets)

| Property | URL | DESIGN_SYSTEM.md Location | Design Language |
|----------|-----|--------------------------|-----------------|
| ShadowTag AI | shadowtagai.web.app | `apps/shadowtagai/DESIGN_SYSTEM.md` | Kinetic Void |
| KovelAI | kovelai.web.app | `apps/kovelai/DESIGN_SYSTEM.md` | Structured Precision |

## Anti-Patterns (FORBIDDEN)

- ❌ Generating CSS from memory — ALWAYS scrape first
- ❌ Using `google-labs-code/design.md` GitHub repo (does not exist as public repo — use `design.googleapis.com/mcp`)
- ❌ Generating images without geometric constraints from the source layout
- ❌ Generating copy without character-count limits from the source containers
- ❌ Skipping WCAG contrast validation before Assembly phase
- ❌ Using `npm install -g @google-labs/design-cli` (does not exist — use the Google Design MCP endpoint)
