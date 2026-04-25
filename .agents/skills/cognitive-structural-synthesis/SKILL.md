---
name: cognitive-structural-synthesis
version: 7.0.0
description: >
  Standardized E2E workflow for cloning websites using ai-website-cloner-template,
  Chrome DevTools MCP, Google Design MCP (design.googleapis.com), Stitch MCP,
  DESIGN.md open-source spec, and the Antigravity Browser Subagent autonomous DOM loop.
---

# Cognitive Structural Synthesis (V7 — DESIGN.md Spec + Browser Subagent Native)

## Correction Record
- V5 referenced fictional tools (Mariner API, Flow text tool, Opal HTML tool, "Nano Banana 2"). These DO NOT EXIST as APIs.
- V6 replaced all fictional references with **real, verified tools** the agent actually has.
- V7 integrates the **DESIGN.md open-source spec** (`@google/design.md@0.1.1`) linting, diff, and export pipeline.
- Google Design MCP at `https://design.googleapis.com/mcp` is CONFIRMED LIVE (no auth, 7 tools).
- Browser Subagent DOM loop replaces all "meatware bridge" human routing.

## Tool Inventory (V7 Real)

### Tier 1 — MCP Servers (Machine-Callable)
| Server | Endpoint | Tools | Auth |
|--------|----------|-------|------|
| **Design MCP** | `https://design.googleapis.com/mcp` | `generate_brand_color_scheme`, `extract_brand_colors_from_image`, `extract_and_generate_brand_color_scheme`, `search_icons`, `icons_instructions`, `search_fonts`, `describe_font` | None required |
| **Stitch MCP** | Antigravity native | `create_design_system`, `generate_screen_from_text`, `edit_screens`, `generate_variants`, `apply_design_system`, etc. (12 tools) | API key |
| **Chrome DevTools MCP** | Antigravity native | `navigate_page`, `take_snapshot`, `take_screenshot`, `click`, `fill`, `evaluate_script`, `lighthouse_audit`, etc. (29 tools) | Local |
| **Firebase MCP** | Antigravity native | `firebase_init`, `firebase_get_environment`, Firestore CRUD, Hosting deploy (45 tools) | OAuth |

### Tier 2 — Agent Capabilities (Direct)
| Capability | Tool | Purpose |
|-----------|------|---------|
| **Image Generation** | `Stitch MCP → generate_screen_from_text` | BANNED: `generate_image` per TACSOP 7. Use Stitch screens, CSS gradients, or SVG placeholders |
| **Browser Subagent** | `browser_subagent` | Autonomous DOM interaction, visual verification, video recording |
| **URL Content Reader** | `read_url_content` | HTML→markdown extraction for text/structure |
| **Web Search** | `search_web` | Market research, competitive intelligence |

### Tier 3 — Cloner Template Engine
| Component | Path | Purpose |
|-----------|------|---------|
| **ai-website-cloner-template** | `tools/cloner-engine/template/` | Next.js 16 + shadcn/ui + Tailwind v4 scaffold |
| **AGENTS.md** | `tools/cloner-engine/template/AGENTS.md` | Cloner pipeline instructions |
| **Component Specs** | `tools/cloner-engine/template/docs/research/` | Extraction output & component specs |

### Tier 4 — DESIGN.md Spec Toolchain
| Tool | Installation | Purpose |
|------|-------------|---------|
| **Lint** | `npx @google/design.md lint DESIGN.md` | Validates DESIGN.md against spec (8 rules incl. WCAG contrast) |
| **Diff** | `npx @google/design.md diff DESIGN.md` | Token-level regression detection between versions |
| **Export Tailwind** | `npx @google/design.md export --format tailwind DESIGN.md` | Generates Tailwind CSS theme from tokens |
| **Export W3C DTCG** | `npx @google/design.md export --format dtcg DESIGN.md` | Generates W3C Design Token Community Group format |
| **Spec Reference** | `external_repos/reference/design_md_spec/` | Full spec source cloned locally |

---

## The Immutable Pipeline

### Phase 1: Physical Scrape (Chrome DevTools MCP + Browser Subagent)

**DO NOT write ad-hoc Puppeteer scripts.** Use the cloner template's scaffold combined with the Chrome DevTools MCP.

1. **Navigate**: `chrome-devtools-mcp.navigate_page` to target URL
2. **Wait for hydration**: `chrome-devtools-mcp.wait_for` on key content selectors
3. **Snapshot DOM**: `chrome-devtools-mcp.take_snapshot` — captures full a11y tree with UIDs
4. **Screenshot**: `chrome-devtools-mcp.take_screenshot` — visual reference (full page)
5. **Extract computed styles**: `chrome-devtools-mcp.evaluate_script` — run `getComputedStyle()` on key elements
6. **Content extraction**: `read_url_content` — HTML→markdown for text content
7. **Asset download**: `browser_subagent` — navigate to each asset URL, save to `public/images/`

**Output**: `docs/research/` directory with design tokens, content map, asset inventory.

### Phase 2: Design Archaeology (Design MCP + DESIGN.md Spec + Stitch MCP)

1. **Extract brand colors from screenshot**:
   ```
   Design MCP → extract_and_generate_brand_color_scheme
   Input: screenshot as base64
   Output: Full Material Design color scheme with semantic roles
   ```

2. **Search matching fonts**:
   ```
   Design MCP → describe_font
   Input: font family name from computed styles
   Output: Full font metadata, weights, supported languages, usage guidance
   ```

3. **Search icons**:
   ```
   Design MCP → search_icons
   Input: semantic tags from UI elements
   Output: Material Symbol names
   ```

4. **Generate DESIGN.md** — MUST comply with `@google/design.md` spec:
   ```yaml
   # YAML front matter tokens
   name: "<BrandName>"
   colors:
     primary: "#XXXXXX"     # From Design MCP extraction
     secondary: "#XXXXXX"
     tertiary: "#XXXXXX"
     neutral: "#XXXXXX"
   typography:
     h1:
       fontFamily: <from describe_font>
       fontSize: <from getComputedStyle>
       fontWeight: <number>
       lineHeight: <unitless or dimension>
       letterSpacing: <dimension>
     body-md:
       fontFamily: <from describe_font>
       fontSize: <from getComputedStyle>
   rounded:
     sm: 4px
     md: 8px
     lg: 16px
   spacing:
     sm: 8px
     md: 16px
     lg: 32px
   ```
   Followed by markdown prose sections: Overview, Colors, Typography, Layout, Shapes, Components.

5. **Lint DESIGN.md**:
   ```bash
   npx @google/design.md lint DESIGN.md
   ```
   MUST pass all 8 rules including WCAG contrast before proceeding.

6. **Export to Tailwind**:
   ```bash
   npx @google/design.md export --format tailwind DESIGN.md
   ```
   Use output to configure `tailwind.config.ts` in cloner template.

7. **Create Stitch Design System**:
   ```
   Stitch MCP → create_design_system
   Input: Colors, fonts, shapes from DESIGN.md
   Output: Named design system asset
   ```

### Phase 3: Hollow & Inject (REAL tool routing)

**Text Generation** (replaces fictional "Mariner & Flow"):
- Agent writes copy directly using `read_url_content` extracted text as baseline
- Character count matching: agent counts original chars per element, constrains replacements
- No CSS grid breaks because agent respects extracted `max-width`, `grid-template-columns`

**Image Generation** (TACSOP 7 — Visual Provenance):
- `Stitch MCP → generate_screen_from_text` for UI section imagery
- CSS gradient/SVG placeholders for decorative elements (DESIGN.md tokens)
- `browser_subagent` to download original assets from target site to `public/images/`
- BANNED: `generate_image` tool (no provenance tracking, hallucinated aspect ratios)

**Icon Replacement**:
- Design MCP → `search_icons` with semantic tags
- Design MCP → `icons_instructions` for correct web implementation

**Interactive Elements** (replaces fictional "Opal"):
- Agent writes component code directly into `src/components/`
- Browser subagent verifies interaction flows (click, hover, form submission)

### Phase 4: Assembly (Stitch MCP + Cloner Template)

1. **Generate screens**: `Stitch MCP → generate_screen_from_text` for each page section
2. **Apply design system**: `Stitch MCP → apply_design_system` across all screens
3. **Edit screens**: `Stitch MCP → edit_screens` for fine-tuning
4. **Code injection**: Write generated assets into cloner template's `src/` structure:
   - `src/app/page.tsx` — main layout
   - `src/components/` — section components
   - `public/images/` — generated imagery

### Phase 5: Autonomous Verification (Browser Subagent Loop)

**This is the "Meatware Bridge Eviction" — NO human routing needed.**

1. **Spin up dev server**: `npm run dev` via terminal
2. **Browser subagent navigates**: Opens localhost, captures screenshots
3. **Visual regression**: Compares against Phase 1 screenshots
4. **DOM error detection**: `chrome-devtools-mcp.list_console_messages` — catch JS errors
5. **Interaction testing**: Browser subagent clicks through all interactive elements
6. **Lighthouse audit**: `chrome-devtools-mcp.lighthouse_audit` — validate Performance, A11y, SEO ≥ 90
7. **DESIGN.md diff**: `npx @google/design.md diff DESIGN.md` — verify no token regression
8. **Self-correction loop**: If audit fails, agent reads errors → patches code → re-runs
9. **Artifact generation**: Screenshot + video recording artifacts prove the feature works

### Phase 6: Deployment

1. Firebase Hosting via `firebase-mcp-server` MCP
2. Or Vercel deploy via cloner template's native config
3. Post-deploy Lighthouse ≥ 90 validation

---

## Browser Subagent Architecture (Permanent Reference)

The primary Antigravity agent handles backend logic and orchestration. The Browser Subagent runs in an isolated Chrome instance and operates directly on the DOM.

| Phase | Legacy ("Meatware Bridge") | Antigravity DOM Subagent |
|-------|---------------------------|--------------------------|
| **Execution** | AI writes code, human boots localhost | AI writes code, autonomously spins up server |
| **Navigation** | Human clicks through app | Browser subagent reads DOM, simulates user inputs |
| **Debugging** | Human spots broken CSS, copies console error | Subagent detects visual anomalies and DOM errors, self-corrects |
| **Final Review** | Human signs off manually | User reviews Artifacts (task list, code diffs, browser video recording) |

---

## Design MCP Quick Reference

Endpoint: `https://design.googleapis.com/mcp`
Auth: **None required**
Protocol: JSON-RPC 2.0 over HTTPS (Streamable HTTP)

### Available Tools
1. `generate_brand_color_scheme` — Generate Material Design color scheme from hex keys
2. `extract_brand_colors_from_image` — Extract brand colors from base64 image
3. `extract_and_generate_brand_color_scheme` — Combined extract + generate
4. `search_icons` — Find Material Symbols by semantic tags
5. `icons_instructions` — How to use Material Icons/Symbols on web
6. `search_fonts` — Find Google Fonts by category/language
7. `describe_font` — Full font metadata and usage guidance

### curl Test
```bash
curl --location 'https://design.googleapis.com/mcp' \
  --header 'content-type: application/json' \
  --header 'accept: application/json, text/event-stream' \
  --data '{ "method": "tools/list", "jsonrpc": "2.0", "id": 1 }'
```

---

## DESIGN.md Spec Config Reference

Source: `external_repos/reference/design_md_spec/packages/cli/src/linter/spec-config.yaml`

### Required Sections (Canonical Names)
| Section | Aliases |
|---------|---------|
| Overview | Brand & Style |
| Colors | — |
| Typography | — |
| Layout | Layout & Spacing |
| Elevation & Depth | Elevation |
| Shapes | — |
| Components | — |
| Do's and Don'ts | — |

### Color Roles (Recommended Tokens)
`primary`, `secondary`, `tertiary`, `neutral`, `surface`, `on-surface`, `error`

### Typography Tokens (Recommended)
`headline-display`, `headline-lg`, `headline-md`, `body-lg`, `body-md`, `body-sm`, `label-lg`, `label-md`, `label-sm`

### Typography Properties
`fontFamily` (string), `fontSize` (Dimension), `fontWeight` (number), `lineHeight` (Dimension|number), `letterSpacing` (Dimension), `fontFeature` (string), `fontVariation` (string)

### Rounding Tokens (Recommended)
`none`, `sm`, `md`, `lg`, `xl`, `full`

### Dimension Units
`px`, `em`, `rem`

---

## Cloner Template Quick Reference

Path: `tools/cloner-engine/template/`
Stack: Next.js 16, React 19, shadcn/ui, Tailwind CSS v4, TypeScript strict
Commands: `npm run dev`, `npm run build`, `npm run check`
Agent instructions: `tools/cloner-engine/template/AGENTS.md`
