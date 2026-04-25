---
name: "Directive Obsidian"
description: >
  Stitch engine design context for KovelAI. The Transparent Authority aesthetic —
  layered glass and light with intentional asymmetry. Built for the Kovel Directive
  Gate, War Room Dashboard, and Landing Page screens.
  Stitch Project ID: 10668904013221153385
  Design System Asset: assets/299ecdd5d43c4a54af8030b114be6176
colors:
  # Core palette (Stitch-specific naming with underscores)
  primary: "#A8E8FF"
  primary_container: "#00D4FF"
  secondary: "#7AD0FF"
  tertiary: "#3EFE8A"
  error: "#FFB4AB"
  surface: "#111125"
  surface_container_low: "#1A1A2E"
  surface_container: "#1E1E32"
  surface_container_high: "#28283D"
  surface_container_highest: "#333348"
  on_surface: "#E2E0FC"
  on_surface_variant: "#BBC9CF"
  outline_variant: "#3C494E"
  # Status colors (custom domain)
  status_approved: "#00E676"
  status_conditional: "#FFB347"
  status_rejected: "#FF5252"
  # Primary container text
  on_primary_container: "#003344"
  # Surface variants for glass effects
  surface_bright: "#2A2A45"
typography:
  headline-display:
    fontFamily: Space Grotesk
    fontSize: 64px
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 40px
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 28px
    fontWeight: 600
    lineHeight: 1.25
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: 400
    lineHeight: 1.6
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 500
    lineHeight: 1.5
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 600
    lineHeight: 1
    letterSpacing: 0.02em
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1
    letterSpacing: 0.04em
  label-data:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "tnum"
rounded:
  sm: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  2xl: 48px
  3xl: 64px
  card-inner: 0.75rem
components:
  button-primary:
    backgroundColor: "{colors.primary_container}"
    textColor: "{colors.on_primary_container}"
    typography: "{typography.label-lg}"
    rounded: "{rounded.lg}"
    height: 44px
    padding: 0 24px
  button-secondary-glass:
    backgroundColor: "{colors.surface_bright}"
    textColor: "{colors.primary}"
    typography: "{typography.label-lg}"
    rounded: "{rounded.lg}"
    height: 44px
    padding: 0 24px
  button-tertiary:
    backgroundColor: transparent
    textColor: "{colors.primary}"
    typography: "{typography.label-lg}"
  card-standard:
    backgroundColor: "{colors.surface_container}"
    textColor: "{colors.on_surface}"
    rounded: "{rounded.xl}"
    padding: "{spacing.lg}"
  card-elevated:
    backgroundColor: "{colors.surface_container_high}"
    textColor: "{colors.on_surface}"
    rounded: "{rounded.xl}"
    padding: "{spacing.lg}"
  card-interactive:
    backgroundColor: "{colors.surface_container_highest}"
    textColor: "{colors.on_surface}"
    rounded: "{rounded.xl}"
    padding: "{spacing.lg}"
  section-base:
    backgroundColor: "{colors.surface_container_low}"
    textColor: "{colors.on_surface}"
    padding: "{spacing.3xl}"
  input-field:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on_surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    height: 44px
    padding: 0 16px
  compliance-gauge:
    backgroundColor: "{colors.surface_container}"
    textColor: "{colors.on_surface_variant}"
    rounded: "{rounded.full}"
    size: 120px
  status-approved:
    backgroundColor: "{colors.status_approved}"
    textColor: "{colors.surface}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    padding: 4px 12px
  status-conditional:
    backgroundColor: "{colors.status_conditional}"
    textColor: "{colors.surface}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    padding: 4px 12px
  status-rejected:
    backgroundColor: "{colors.status_rejected}"
    textColor: "{colors.surface}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    padding: 4px 12px
  ghost-border-panel:
    backgroundColor: "{colors.surface_container}"
    textColor: "{colors.on_surface}"
    rounded: "{rounded.xl}"
    padding: "{spacing.lg}"
  nav-accent:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.surface}"
    typography: "{typography.label-lg}"
    rounded: "{rounded.md}"
  data-label:
    backgroundColor: transparent
    textColor: "{colors.on_surface_variant}"
    typography: "{typography.label-data}"
  error-indicator:
    backgroundColor: "{colors.error}"
    textColor: "{colors.surface}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    padding: 4px 12px
  ghost-divider:
    backgroundColor: "{colors.outline_variant}"
    height: 1px
  page-canvas:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on_surface}"
  compliance-pass-badge:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.surface}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    padding: 4px 12px
---

## Overview

> Stitch Project ID: 10668904013221153385
> Design System Asset: assets/299ecdd5d43c4a54af8030b114be6176
> Origin: Generated by Stitch MCP

This design system is built upon the North Star of **"The Transparent Authority."**
In the high-stakes world of legal compliance, the interface must feel like an
immutable source of truth, yet remain fluid and hyper-modern.

We treat the UI as a single, cohesive environment of **layered glass and light**.
Intentional asymmetry (right-aligned technical metadata vs left-aligned editorial
headlines) creates a bespoke, engineered feel. The hierarchy is defined not by
lines, but by the **physical stacking of translucent surfaces**.

## Colors

### Core Palette
- **Primary (#A8E8FF):** High-level branding — a soft cyan for emphasis on dark surfaces.
- **Primary Container (#00D4FF):** Active states and CTAs — the vivid cyan for
  maximum interactive signaling.
- **Secondary (#7AD0FF):** Supporting accents — a lighter blue for secondary interactions.
- **Tertiary (#3EFE8A):** Reserved EXCLUSIVELY for pass/success/approved states.
  Never used decoratively.
- **Error (#FFB4AB):** Soft coral for error indicators — warm enough to signal
  without harsh alarming.
- **Surface (#111125):** The base void — deep blue-tinged black that adds dimension.

### Status Colors
- **Approved (#00E676):** Emerald glow for pass states.
- **Conditional (#FFB347):** Amber glow for review-pending states.
- **Rejected (#FF5252):** Crimson glow for failure states.

### Rules
- **No-Line Rule:** 1px solid borders are strictly prohibited for sectioning.
  Use background shifts between `surface_container_low` → `surface_container` →
  `surface_container_high`.
- **Glass & Gradient:** Floating panels use surface variants at reduced opacity
  with `backdrop-blur: 20-40px`.
- **Signature Textures:** Buttons and compliance gauges use gradient from
  `primary` → `primary_container`.

## Typography

The typography uses a **dual font stack**: **Space Grotesk** for display and
headlines (lending an engineered, geometric authority), and **Inter** for body
text, labels, and data (ensuring clinical readability).

- **Headlines:** Space Grotesk at 600–700 weight with tight letter-spacing
  (-0.02em) for authoritative, compressed headings.
- **Body & Legal Text:** Inter 400-500 at 14-18px for comfortable reading
  of dense legal content.
- **Data Labels:** Inter 400 with `font-feature-settings: "tnum"` for
  tabular numeric alignment in compliance dashboards and gauges.

## Layout

The layout uses intentional asymmetry as a compositional principle:
- **Wide Narrative Left:** Editorial headlines, descriptions, and explanatory
  content occupy the larger column.
- **Narrow Metadata Right:** Technical data points, compliance scores, and
  timestamp metadata are right-aligned in a narrower column.

Whitespace of `0.75rem` (12px) replaces 1px dividers between card items.

## Elevation & Depth

- **Ambient Shadows:** Blue-tinted glass shadows using `primary_container`
  at 8% opacity with 24-48px spread — unique to this Stitch context.
- **Ghost Border:** `outline_variant` at 15% opacity — a "glint" not a hard edge.
  This is a 0.5px top-edge highlight, not a full border.
- **Glow States:** Status indicators (approved/conditional/rejected) receive a
  2px outer glow in their respective status color.
- **Roundness:** Constrained to `md` (0.375rem) and `lg` (0.5rem) — sharper
  and more technical than the root KovelAI DESIGN.md.

## Shapes

The shape language is **sharper than the root KovelAI system** to reinforce
the engineered Stitch aesthetic:

- **Cards:** `0.75rem` (xl) — the containment shape for all panels.
- **Buttons:** `0.5rem` (lg) — matching the tight technical feel.
- **Badges/Status:** `9999px` (full) for all status indicators and pills.
- **Inputs:** `0.375rem` (md) — minimal softening for form fields.

## Components

### Buttons
- **Primary:** Solid `primary_container` background with `on_primary_container`
  text — the vivid cyan CTA.
- **Secondary (Glass):** `surface_bright` at reduced opacity with ghost border —
  the floating glass button.
- **Tertiary:** Text-only in `primary` color with underline on hover.

### Cards
- No 1px dividers. Use `0.75rem` whitespace or alternating surface container
  backgrounds.
- Glassy cards get a `0.5px` top-edge highlight in `primary` at 20% opacity.
- Three elevation levels: standard → elevated → interactive.

### Input Fields
- Background: `surface` (the deepest level).
- Bottom-only 2px border in `outline_variant`.
- Focus state: bottom border glows `primary`.

### Compliance Gauges
- Concentric rings: `primary_container` (progress arc) + `surface_container`
  (empty track).
- Central figure uses headline typography.

### Screens (Generated)

| Screen | ID | Status |
|--------|-----|--------|
| Kovel Directive Gate | `a17b3c13ffc7455c907389131a1fb780` | ✅ Complete |
| War Room Dashboard | (see project) | ✅ Complete |
| Landing Page | (see project) | ✅ Complete |

## Do's and Don'ts

- Do use asymmetrical layouts (wide narrative left, narrow metadata right)
- Do apply `backdrop-blur` to all overlays and glass panels
- Do use `tertiary` (#3EFE8A) sparingly — only for PASS/approved states
- Do use `font-feature-settings: "tnum"` for all numeric data displays
- Don't use pure black `#000000` or pure white `#FFFFFF`
- Don't use high-contrast drop shadows — use ambient tinted shadows only
- Don't use Material Design rounded corners (24px+) — stay at md/lg scale
- Don't use 1px horizontal dividers between list items — use whitespace
- Don't use explicit borders for section separation — use background shifts
