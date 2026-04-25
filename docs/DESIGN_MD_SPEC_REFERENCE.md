# DESIGN.md Specification — Persistent Reference

> **Source:** [google-labs-code/design.md](https://github.com/google-labs-code/design.md) (Apache-2.0)
> **Spec Version:** `alpha`
> **CLI Package:** `@google/design.md@0.1.1`
> **Local Clone:** `external_repos/design_md/`
> **Created:** 2026-04-25

## Overview

DESIGN.md is a dual-layer design system format:
1. **YAML frontmatter** — Machine-readable design tokens (colors, typography, rounded, spacing, components)
2. **Markdown body** — Human-readable design rationale in prescribed `##` section order

## YAML Frontmatter Schema

```yaml
---
version: alpha                    # optional, current: "alpha"
name: <string>                    # required
description: <string>             # optional
colors:
  <token-name>: <Color>           # "#" + hex (sRGB), e.g. "#1A1C1E"
typography:
  <token-name>:
    fontFamily: <string>
    fontSize: <Dimension>         # number + unit (px, em, rem)
    fontWeight: <number>          # 400, 600, 700
    lineHeight: <Dimension|number>  # 24px or 1.6 (unitless = multiplier)
    letterSpacing: <Dimension>
    fontFeature: <string>         # font-feature-settings
    fontVariation: <string>       # font-variation-settings
rounded:
  <scale-level>: <Dimension>     # xs, sm, md, lg, xl, full
spacing:
  <scale-level>: <Dimension|number>
components:
  <component-name>:
    <property>: <string|token reference>
---
```

## Token Types

| Type | Format | Example |
|------|--------|---------|
| Color | `#` + hex (sRGB) | `"#1A1C1E"` |
| Dimension | number + unit | `48px`, `-0.02em`, `1.5rem` |
| Number | unitless | `400`, `1.6` |
| Token Reference | `{path.to.token}` | `{colors.primary}`, `{rounded.lg}` |

## Mandatory Section Order

Sections use `##` headings. Can be omitted, but *order is enforced*:

| # | Section | Aliases |
|---|---------|---------|
| 1 | **Overview** | Brand & Style |
| 2 | **Colors** | — |
| 3 | **Typography** | — |
| 4 | **Layout** | Layout & Spacing |
| 5 | **Elevation & Depth** | Elevation |
| 6 | **Shapes** | — |
| 7 | **Components** | — |
| 8 | **Do's and Don'ts** | — |

## Component Property Tokens

```yaml
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"    # Token ref, NEVER raw hex
    textColor: "{colors.on-primary}"
    typography: "{typography.label-md}"
    rounded: "{rounded.lg}"
    padding: 12px
    height: 48px
    width: 200px
    size: 40px
  button-primary-hover:
    backgroundColor: "{colors.tertiary-container}"
```

## 8 Lint Rules

| Rule | Severity | Check |
|------|----------|-------|
| `broken-ref` | **error** | Token refs (`{colors.primary}`) that don't resolve |
| `missing-primary` | warning | Colors defined but no `primary` token |
| `contrast-ratio` | warning | Component bg/text pairs below WCAG AA (4.5:1) |
| `orphaned-tokens` | warning | Color tokens defined but never ref'd by components |
| `token-summary` | info | Count of tokens per section |
| `missing-sections` | info | Optional sections absent when tokens exist |
| `missing-typography` | warning | Colors defined but no typography tokens |
| `section-order` | warning | Sections out of canonical order |

## CLI Quick Reference

```bash
# Validate structure + WCAG contrast
npx @google/design.md lint DESIGN.md

# Token-level change detection between versions
npx @google/design.md diff DESIGN-old.md DESIGN-new.md

# Export to Tailwind theme config (generate in CI, NOT committed)
npx @google/design.md export --format tailwind DESIGN.md > tailwind.theme.json

# Export to W3C DTCG tokens.json
npx @google/design.md export --format dtcg DESIGN.md > tokens.json

# Output full spec to inject into agent prompts
npx @google/design.md spec
npx @google/design.md spec --rules-only --format json
```

## Recommended Token Names (Non-Normative)

- **Colors:** `primary`, `secondary`, `tertiary`, `neutral`, `surface`, `on-surface`, `on-primary`, `error`
- **Typography:** `headline-display`, `headline-lg`, `headline-md`, `body-lg`, `body-md`, `body-sm`, `label-lg`, `label-md`, `label-sm`
- **Rounded:** `none`, `sm`, `md`, `lg`, `xl`, `full`
- **Spacing:** `xs`, `sm`, `md`, `lg`, `xl`, `base`, `gutter`, `margin`

## Semantic Role Mapping (Critical — Do NOT Confuse)

| Token | Semantic Meaning | Common Mistake |
|-------|-----------------|----------------|
| `primary` | Main **text/ink** color | ❌ Using it for brand button color |
| `neutral` | **Canvas/background** surface | ❌ Using it for disabled states |
| `tertiary` | **Accent/interaction** (CTAs, highlights) | ❌ Using it decoratively |
| `on-primary` | Text **ON** a primary-colored surface | ❌ Confusing with primary text |

## Consumer Behavior for Unknown Content

| Scenario | Behavior |
|----------|----------|
| Unknown section heading | Preserve; don't error |
| Unknown color token name | Accept if value is valid hex |
| Unknown typography token name | Accept as valid typography |
| Unknown component property | Accept with warning |
| Duplicate section heading | **Error; reject file** |

## Project-Level Topology (Our Convention)

| File | Purpose | SSOT For |
|------|---------|----------|
| `apps/<app>/DESIGN.md` | Universal UI truth (spec-compliant) | All frontend code generation |
| `apps/<app>/.stitch/DESIGN.md` | Stitch engine context | Stitch screen generation only |
| `docs/templates/DESIGN_TEMPLATE.md` | New project template | Bootstrapping |

## Related Skills

| Skill | Tier | Role |
|-------|------|------|
| `designmd-stitch-visual-mastery` | 1 (Global) | Full spec enforcement + CLI integration |
| `stitch-design-spec` | 2 (Brain) | Project-scope routing + lint sequencing |
| `design-md` (stitch-skills) | Legacy | Older extraction workflow (superseded) |
