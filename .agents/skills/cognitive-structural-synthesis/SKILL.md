---
name: cognitive-structural-synthesis
description: End-to-end structural cloning using the JCodesMore engine, Google Design MCP semantic extraction, Bandit/Lighthouse validations, and Cognitive Suite (Veo 3.1) cinematic injection.
version: 4.0.0
---
# Cognitive Structural Synthesis (V4)

## Engine
The JCodesMore `ai-website-cloner-template` (v0.3.1) is installed at `tools/cloner-engine/template/`.
It provides a Next.js 16 + shadcn/ui + Tailwind v4 scaffold with a 474-line multi-phase cloning skill.
The `.git` folder has been archived (RULE 00 compliant) to prevent monorepo index pollution.

## The Pipeline

### 1. Structural Scrape (Chrome DevTools MCP)
Use `chrome-devtools-mcp` tools (`navigate_page`, `take_snapshot`, `take_screenshot`, `evaluate_script`) to:
- Navigate to the target URL
- Take full-page screenshots at desktop (1440px) and mobile (390px)
- Run the JCodesMore CSS extraction script to capture `getComputedStyle()` values
- Extract all images, videos, SVGs, fonts, and background images
- Perform the mandatory interaction sweep (scroll, click, hover, responsive)
- Save extraction artifacts to `tools/cloner-engine/template/docs/research/`

### 2. Security Gate
Run `bandit -r ./clone-base` (Python) or manual review for URL-fetching safety.
Ensure B310 warnings are handled. No raw `eval()` or `exec()` from scraped content.

### 3. Design Archaeology via Google Design MCP
- Call `google-developer-knowledge` MCP server tools
- Pass scraped CSS tokens to synthesize a compliant `DESIGN.md` file
- Map extracted colors to semantic roles (background, foreground, primary, muted, accent)
- Output uses oklch color space per the template's Tailwind v4 configuration

### 4. Auto-Correction (WCAG + Lighthouse)
- Use `chrome-devtools-mcp` `lighthouse_audit` tool for accessibility scoring
- Validate WCAG 2.1 AA contrast ratios on all text/background combinations
- Fix any violations in the design tokens before injection

### 5. Cinematic Injection (Quiet Luxury Override)
Replace source site aesthetics with the Cinematic Legal-Tech direction:
- Full-bleed HTML5 `<video>` backgrounds (Veo 3.1 renders or Google sample video placeholders)
- `atmospheric-glass` overlays: CounselConduit `#080d14` at 95% opacity, UphillSnowball `#030509` at 96%
- Void backgrounds: CounselConduit `#050505`, UphillSnowball `#020408`
- Inter font family (800 bold headlines, 300 light subheadlines)
- Muted neutral palette: `#8da2c0`, `#a0aabf`, `#9ca3af`
- Zero JavaScript animations — pure CSS `fadeUp` keyframes with staggered delays
- Entity Matrix: KovelAI → CounselConduit, ShadowtagAI → UphillSnowball

### 6. Assembly & Lighthouse Gate
- Weave cinematic assets into the extracted HTML shell
- Run `chrome-devtools-mcp` `lighthouse_audit` on the assembled page
- Target scores: Performance ≥90, Accessibility ≥95, Best Practices ≥90, SEO ≥90
- Fix any Lighthouse failures before declaring complete

## Component Output
The final output is a React/TypeScript component (`UnusualChassis.tsx` or similar) that:
- Preserves the structural geometry of the source site
- Replaces all visual identity with Cinematic Legal-Tech aesthetics
- Uses semantic HTML5 with `<video>`, `<section>`, `<header>`, `<footer>`
- Is responsive across desktop (1440px), tablet (768px), and mobile (390px)
- Passes `npx tsc --noEmit` with zero errors

## File Locations
| Artifact | Path |
|----------|------|
| Cloner Engine | `tools/cloner-engine/template/` |
| Clone SKILL.md | `tools/cloner-engine/template/.claude/skills/clone-website/SKILL.md` |
| Gemini Command | `tools/cloner-engine/template/.gemini/commands/clone-website.toml` |
| Research Output | `tools/cloner-engine/template/docs/research/` |
| Design References | `tools/cloner-engine/template/docs/design-references/` |
| Component Specs | `tools/cloner-engine/template/docs/research/components/` |
