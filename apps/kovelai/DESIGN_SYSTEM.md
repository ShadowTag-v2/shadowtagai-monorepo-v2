# KovelAI — DESIGN_SYSTEM.md
## Creative North Star: "The Sovereign Lens"

> Extracted from Stitch MCP project `8471866363933916169` (KovelAI — Legal AI Platform)
> Design Theme: Sovereign Lens | Color Variant: FIDELITY | Device: DESKTOP
> Last synced: 2026-04-22

---

## Identity

| Property | Value |
|----------|-------|
| Project | KovelAI — Legal AI Platform |
| Stitch ID | `8471866363933916169` |
| Color Mode | DARK |
| Headline Font | Inter |
| Body Font | Inter |
| Label Font | Inter |
| Roundness | ROUND_FOUR |
| Spacing Scale | 3 |
| Color Variant | FIDELITY |

---

## Color Tokens

### Core Palette

| Role | Hex | Usage |
|------|-----|-------|
| `primary` | `#fffffd` | Main accent, high-contrast text |
| `primary_container` | `#00ffd1` | CTA backgrounds, hero elements |
| `primary_fixed` | `#15ffd1` | Fixed primary declarations |
| `primary_fixed_dim` | `#00e0b7` | Reduced fixed primary |
| `secondary` | `#c3c0ff` | Supporting accent (indigo) |
| `secondary_container` | `#3626ce` | Secondary containers |
| `tertiary` | `#ffffff` | Warm accent |
| `tertiary_container` | `#e9ddff` | Tertiary containers (violet) |
| `error` | `#ffb4ab` | Error states |
| `error_container` | `#93000a` | Error containers |

### Surface Hierarchy

| Role | Hex | Usage |
|------|-----|-------|
| `surface` | `#0f131f` | Base canvas / void |
| `surface_bright` | `#353946` | Elevated surfaces |
| `surface_container` | `#1b1f2c` | Primary containers |
| `surface_container_high` | `#262a37` | Interactive cards |
| `surface_container_highest` | `#313442` | Modals, overlays |
| `surface_container_low` | `#171b28` | Large content blocks |
| `surface_container_lowest` | `#0a0e1a` | Deepest background |
| `surface_dim` | `#0f131f` | Dimmed surfaces |
| `surface_variant` | `#313442` | Variant containers |
| `surface_tint` | `#00e0b7` | Tint overlay |

### Text / On-Surface

| Role | Hex |
|------|-----|
| `on_background` | `#dfe2f3` |
| `on_surface` | `#dfe2f3` |
| `on_surface_variant` | `#b9cbc3` |
| `on_primary` | `#00382c` |
| `on_primary_container` | `#00725c` |
| `on_secondary` | `#1d00a5` |
| `on_tertiary` | `#3c0090` |
| `on_error` | `#690005` |

### Outline

| Role | Hex |
|------|-----|
| `outline` | `#83958d` |
| `outline_variant` | `#3a4a44` |

### Override Colors

| Role | Hex |
|------|-----|
| Override Primary | `#00FFD1` |
| Override Secondary | `#4F46E5` |
| Override Tertiary | `#7000FF` |
| Override Neutral | `#0A0E1A` |

---

## Design Rules

### The "No-Line" Rule
To maintain a premium, bespoke feel, **1px solid borders are strictly prohibited for sectioning.** Structural boundaries must be defined through:
- **Background Shifts:** `surface_container_low` (#171B28) against `surface` (#0F131F)
- **Negative Space:** Generous gutters from spacing scale 3
- **Tonal Transitions:** Subtle shifts in the navy spectrum

### Glass & Gradient Rule
- **Sovereign Gradient:** Linear gradient `primary_fixed` (#15FFD1) → `secondary_container` (#3626CE)
- **Glassmorphism:** `surface` at 60-80% opacity, `backdrop-filter: blur(24px)`
- **Ghost Border:** `outline_variant` (#3A4A44) at **15% opacity** — felt, not seen

### Surface Philosophy
Treat the UI as a physical stack of semi-translucent materials:
1. **Base Layer:** `surface_container_lowest` (#0A0E1A) — deep background/void
2. **Middle Layer:** `surface_container_low` (#171B28) — primary workspace areas
3. **Top Layer:** `surface_container_highest` (#313442) — interactive cards, floating elements

### Ambient Shadows
- For floating elements: `0px 24px 48px -12px` with 10% opacity of `on_secondary_fixed` (#0F0069)
- Teal glows: `primary_container` (#00FFD1) with 20-40px blur at 10% opacity behind AI components

### Typography Rules
- Display/Headlines: Inter Bold, -0.02em letter-spacing, 3.5rem display-lg
- Body: Inter, 0.875rem body-md, line-height 1.6
- Secondary metadata: `on_surface_variant` (#B9CBC3)
- Labels: Inter label-md, `font-feature-settings: "tnum"` for numerical alignment

### Components
- **Primary Button:** Sovereign Gradient (primary_fixed → secondary_fixed_dim), `on_primary_fixed` text
- **Secondary (Ghost):** No background, ghost border, `primary_fixed` text
- **Input Fields:** `surface_container_high` background, no border, ghost border on focus
- **Glass Navigation:** Fixed sidebar with glassmorphism, 2px vertical `primary_container` light bar for active state
- **AI Insight Chips:** `tertiary_container` background with subtle indigo pulse animation

---

## MCP Validation Source
- **Google Design MCP:** `https://design.googleapis.com/mcp`
- Tool: `generate_brand_color_scheme` with primary=#00FFD1, secondary=#4F46E5, tertiary=#7000FF, neutral=#0A0E1A
- All color tokens mathematically derived from FIDELITY variant
