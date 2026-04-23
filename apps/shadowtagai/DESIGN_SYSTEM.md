# ShadowTag AI — DESIGN_SYSTEM.md
## Creative North Star: "The Kinetic Void"

> Extracted from Stitch MCP project `9697877550112135791` (ShadowTag AI — Sovereign Infrastructure)
> Design Theme: Kinetic Void | Color Variant: VIBRANT | Device: DESKTOP
> Last synced: 2026-04-22

---

## Identity

| Property | Value |
|----------|-------|
| Project | ShadowTag AI — Sovereign Infrastructure |
| Stitch ID | `9697877550112135791` |
| Color Mode | DARK |
| Headline Font | Space Grotesk |
| Body Font | Manrope |
| Label Font | Space Grotesk |
| Roundness | ROUND_FOUR |
| Spacing Scale | 2 |
| Color Variant | VIBRANT |

---

## Color Tokens

### Core Palette

| Role | Hex | Usage |
|------|-----|-------|
| `primary` | `#f183ff` | Main accent, branding |
| `primary_container` | `#ec6aff` | CTA backgrounds, active states |
| `primary_dim` | `#eb65ff` | Reduced emphasis primary |
| `secondary` | `#f993e5` | Supporting accent |
| `secondary_container` | `#78226e` | Secondary containers |
| `tertiary` | `#ff9783` | Warm accent, alerts |
| `tertiary_container` | `#a15100` | Tertiary containers |
| `error` | `#ff6e84` | Error states |
| `error_container` | `#a70138` | Error containers |

### Surface Hierarchy

| Role | Hex | Usage |
|------|-----|-------|
| `surface` | `#0e0e0e` | Base canvas / void |
| `surface_bright` | `#2c2c2c` | Elevated surfaces |
| `surface_container` | `#1a1919` | Primary containers |
| `surface_container_high` | `#201f1f` | Interactive cards |
| `surface_container_highest` | `#262626` | Modals, overlays |
| `surface_container_low` | `#131313` | Large content blocks |
| `surface_container_lowest` | `#000000` | Deepest background |
| `surface_dim` | `#0e0e0e` | Dimmed surfaces |
| `surface_variant` | `#262626` | Variant containers |
| `surface_tint` | `#f183ff` | Tint overlay |

### Text / On-Surface

| Role | Hex |
|------|-----|
| `on_background` | `#ffffff` |
| `on_surface` | `#ffffff` |
| `on_surface_variant` | `#adaaaa` |
| `on_primary` | `#540062` |
| `on_primary_container` | `#41004c` |
| `on_secondary` | `#610a5a` |
| `on_tertiary` | `#671003` |
| `on_error` | `#490013` |

### Outline

| Role | Hex |
|------|-----|
| `outline` | `#777575` |
| `outline_variant` | `#494847` |

### Override Colors

| Role | Hex |
|------|-----|
| Override Primary | `#E040FB` |
| Override Neutral | `#050505` |

---

## Design Rules

### The "No-Line" Rule
Borders are a failure of hierarchy. 1px solid borders for sectioning are **strictly prohibited**. Boundaries must be defined through:
- **Tonal Shifts:** `surface-container-low` against `surface` background
- **Glow-Indicated Edges:** Radial gradient of `primary-container` at 5% opacity
- **Negative Space:** Large, intentional gaps

### Glass & Gradient Rule
- **Hydra Gradients:** Linear gradient `primary` (#f183ff) → `primary_container` (#ec6aff) at 135°
- **The "Electric Edge":** `secondary` (#f993e5) with 15px drop-shadow blur for neon effect
- **Glassmorphism:** `surface` at 60% opacity, 20px backdrop-blur, ghost border at 15% opacity

### Ambient Shadows
- Blur: 40px to 80px
- Color: 4% opacity of `surface_tint` (#d2bbff — corrected from original to match actual tint)
- No standard drop shadows

### Typography Rules
- Display/Headline: Space Grotesk, `letter-spacing: -0.02em`
- Labels: Space Grotesk, `label-sm`, uppercase, `+0.1em tracking`
- Body: Manrope, `line-height: 1.6`
- Use `on_surface_variant` (#adaaaa) for body text, reserving white for headings only

---

## MCP Validation Source
- **Google Design MCP:** `https://design.googleapis.com/mcp`
- Tool: `generate_brand_color_scheme` with primary=#E040FB, neutral=#050505
- All color tokens mathematically derived from VIBRANT variant
