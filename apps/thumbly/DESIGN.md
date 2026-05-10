---
name: Thumbly
description: >
  Instantaneous YouTube thumbnail generator with Stripe-deterministic ledgers.
  Dark luxury glassmorphism with emerald-to-cyan gradient accent system.
  Powered by Nano Banana 2 (Gemini 3.1 Flash Image) inference engine.
colors:
  # Core surfaces — pure black base with glass overlays
  surface: "#000000"
  surface-glass: "#18181B"
  surface-glass-dark: "#0A0A0A"
  on-surface: "#FAFAFA"
  on-surface-variant: "#A1A1AA"
  # Primary ink — white text on dark void
  primary: "#FAFAFA"
  on-primary: "#000000"
  # Accent gradient endpoints
  tertiary: "#34D399"
  tertiary-end: "#22D3EE"
  on-tertiary: "#022C22"
  # Sub-pixel borders
  outline-variant: "#2A2A2E"
  outline-hover: "#3A3A40"
  # Status
  status-success: "#34D399"
  status-error: "#EF4444"
  # Secondary — muted zinc for meta
  secondary: "#71717A"
  on-secondary: "#FAFAFA"
  # Inverse
  inverse-surface: "#FAFAFA"
  inverse-on-surface: "#000000"
typography:
  headline-display:
    fontFamily: Inter
    fontSize: 64px
    fontWeight: 800
    lineHeight: 1.1
    letterSpacing: -0.03em
  headline-lg:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Outfit
    fontSize: 28px
    fontWeight: 700
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
    fontWeight: 400
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
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: 500
    lineHeight: 1
    letterSpacing: 0.05em
rounded:
  sm: 8px
  md: 12px
  lg: 16px
  xl: 20px
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
  canvas-boundary-w: 1280px
  canvas-boundary-h: 720px
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.on-tertiary}"
    typography: "{typography.label-lg}"
    rounded: "{rounded.lg}"
    height: 48px
    padding: 0 28px
  button-primary-hover:
    backgroundColor: "{colors.tertiary-end}"
  card-glass:
    backgroundColor: "{colors.surface-glass}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.lg}"
    padding: "{spacing.lg}"
  card-glass-dark:
    backgroundColor: "{colors.surface-glass-dark}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.lg}"
    padding: "{spacing.lg}"
  hero-headline:
    backgroundColor: "{colors.on-primary}"
    textColor: "{colors.primary}"
    typography: "{typography.headline-display}"
  canvas-sandbox:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    width: "{spacing.canvas-boundary-w}"
    height: "{spacing.canvas-boundary-h}"
  input-prompt:
    backgroundColor: "{colors.surface-glass}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    height: 48px
    padding: 0 16px
  micro-border-card:
    backgroundColor: "{colors.surface-glass}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.lg}"
    padding: "{spacing.lg}"
  micro-border-card-hover:
    backgroundColor: "{colors.surface-glass}"
    textColor: "{colors.on-surface}"
  badge-success:
    backgroundColor: "{colors.status-success}"
    textColor: "{colors.on-tertiary}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    padding: 4px 12px
  badge-error:
    backgroundColor: "{colors.status-error}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    padding: 4px 12px
  credit-counter:
    backgroundColor: "{colors.outline-variant}"
    textColor: "{colors.on-surface-variant}"
    typography: "{typography.label-lg}"
    rounded: "{rounded.full}"
    padding: 4px 16px
  meta-label:
    backgroundColor: transparent
    textColor: "{colors.secondary}"
    typography: "{typography.label-sm}"
  oauth-gate:
    backgroundColor: "{colors.surface-glass}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.xl}"
    padding: "{spacing.xl}"
  chip-inverse:
    backgroundColor: "{colors.inverse-surface}"
    textColor: "{colors.inverse-on-surface}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    padding: 4px 12px
  nav-outline:
    backgroundColor: transparent
    textColor: "{colors.on-surface}"
    typography: "{typography.label-lg}"
    height: 56px
  border-hover:
    backgroundColor: "{colors.outline-hover}"
    textColor: "{colors.on-secondary}"
    typography: "{typography.label-md}"
  page-canvas:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
---

## Overview

Thumbly is an instantaneous YouTube thumbnail generator utilizing
Stripe-deterministic ledgers and extremely high-impact visual aesthetics to
drive conversion-rate perfection. Under the hood, it rigidly enforces the
utilization of **Nano Banana 2 (Gemini 3.1 Flash Image)** for primary
text-rendering and world-knowledge asset generation at maximum inference speed.

### Deployment Target
1. **Frontend Rendering:** Stitch AI Engine (direct synthesis via this DESIGN.md).
2. **Backend/Cloud Infrastructure:** Google AI Studio native @Firebase Integration
   (Firestore DB, Firebase Authentication, Cloud Functions). Local Next.js/Supabase
   routes are officially deprecated in favor of this hyper-tight bundle.

## Colors

The palette centers on **absolute pure black** as the spatial void, overlaid
with highly diffused emerald and cyan radial blurs for atmospheric depth:

- **Surface (#000000):** Pure black base — the spatial void canvas that receives
  all framer-motion generated radial blur overlays (emerald-500/20, cyan-500/20).
- **Primary (#FAFAFA):** Near-white ink for maximum contrast on the black void.
- **Tertiary (#34D399):** Emerald-400 — the warm end of the signature
  emerald-to-cyan gradient accent (`from-emerald-400 to-cyan-400`).
- **Tertiary-End (#22D3EE):** Cyan-400 — the cool end of the gradient accent.
- **Surface-Glass (#18181B):** Zinc-900 — the translucent glass surface base for
  cards and overlays, paired with `backdrop-blur-xl`.
- **Outline-Variant (#2A2A2E):** Sub-pixel thin, high-contrast border at
  white/10 opacity equivalent. Hover state ramps to outline-hover (#3A3A40).
- **Secondary (#71717A):** Muted zinc-500 for metadata labels and deemphasized text.

## Typography

The typography enforces **geometric font density** using Inter as the primary
workhorse and Outfit for select headline variants:

- **Hero Headers:** Inter 800 with radical gradient text treatment
  (`bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-cyan-400`).
  The gradient spans are a core identity element.
- **Subheadlines:** Outfit 700 at 28px for secondary heading weight.
- **Body:** Inter 400 at 14-18px for all descriptive content.
- **Labels:** Inter 500-600 at 11-14px with letter-spacing for data and UI labels.
- **System fallback:** system-ui.

## Layout

The layout is organized around the **thumbnail canvas sandbox** — a fixed
1280×720 rendering boundary that is the product's central element:

- **Unauthenticated view:** Full-width hero with H1, gradient text, and
  illuminated CTA routing to Firebase OAuth.
- **Authenticated studio:** Canvas-centric layout with the 1280×720 sandbox
  as the focal point, surrounded by input vectors and control panels.
- **Credit entitlement hooks:** Active Firebase function calls verifying
  `userRecord.credits > 0` before synthesis. Generation blocked on zero-balance.

## Elevation & Depth

Depth is achieved through **spatial backgrounds** — highly diffused radial
blurs at large scales (120px blur radius) creating atmospheric gradients
behind the glass surfaces:

- **Level 0 (Void):** Pure black `#000000` with emerald/cyan radial blur
  overlays via framer-motion.
- **Level 1 (Glass):** Zinc-900 (`#18181B`) surfaces with `backdrop-blur-xl`
  and sub-pixel white/10 borders.
- **Level 2 (Elevated Glass):** Same glass treatment with increased border
  luminosity on hover (white/10 → white/20).
- **No traditional shadows.** Atmospheric blur replaces elevation hierarchy.

## Shapes

The shape language is **generously rounded** — softer than KovelAI or
ShadowTagAI to match the consumer-grade, high-energy aesthetic:

- **Cards:** `16px` (lg) — warm containment for glass surfaces.
- **Buttons:** `16px` (lg) — matching cards for visual cohesion.
- **Canvas Sandbox:** `12px` (md) — slightly sharper for the workspace tool.
- **Badges/Pills:** `9999px` (full) for status indicators and credits counter.
- **OAuth Gate:** `20px` (xl) — extra-rounded for the authentication panel.

## Components

### Unauthenticated Hero
- **H1:** "Generate High-Conversion YouTube Thumbnails." in gradient text.
- **CTA:** Illuminated emerald button routing to Firebase OAuth gate.

### Authenticated Studio Sandbox
- **Canvas:** 1280×720 rendering boundary as the central infinite-canvas.
- **Input Vectors:** Text prompt fields with surface-glass background and
  prompt injection constraints enforced upstream.
- **Credit Counter:** Badge displaying `userRecord.credits` with live
  Firebase function verification.

### Entitlement Controls
- **The Ledger:** Firebase function calls gating visual synthesis on credit
  balance > 0. Zero-balance accounts see the credit purchase flow.
- **OAuth Gate:** Glass panel with Firebase OAuth integration and rounded-xl
  corners for the authentication experience.

## Do's and Don'ts

- Do use the emerald-to-cyan gradient for hero text and primary CTAs
- Do use pure black (#000000) as the spatial void base (Thumbly is the exception)
- Do apply `backdrop-blur-xl` to all glass surfaces
- Do use sub-pixel borders (outline-variant) for card edge definition
- Do enforce credit verification before any thumbnail synthesis call
- Don't use solid background colors larger than card-sized elements — use radial blurs
- Don't use traditional box-shadows — use atmospheric blur overlays
- Don't mix more than two font families (Inter + Outfit max)
- Don't use borders wider than 1px — sub-pixel aesthetic is core identity
- Don't expose the 1280×720 canvas boundary to unauthenticated users
