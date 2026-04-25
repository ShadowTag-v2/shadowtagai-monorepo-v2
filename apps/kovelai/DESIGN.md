---
name: KovelAI
description: >
  The Shopify for Legal AI — Privilege-Protected AI for every client query.
  Post-Heppner privileged AI routing for law firms.
  Dark mode glassmorphism with cyan accent as primary interactive color.
colors:
  # Core surface hierarchy
  surface: "#0A0A0F"
  surface-dim: "#0A0A0F"
  surface-container-low: "#0D1117"
  surface-container: "#111827"
  surface-container-high: "#1A1F2E"
  on-surface: "#FFFFFF"
  on-surface-variant: "#8B949E"
  on-surface-elevated: "#C9D1D9"
  # Primary ink — white text on dark backgrounds
  primary: "#FFFFFF"
  on-primary: "#0A0A0F"
  # Accent — the signature cyan
  tertiary: "#00BCD4"
  on-tertiary: "#003238"
  tertiary-container: "#00838F"
  # Semantic — model-specific brand colors
  secondary: "#4285F4"
  on-secondary: "#0D2240"
  # Surface overlays
  surface-overlay: "#0C0C12"
  surface-card: "#101621"
  surface-accent-tint: "#0A2B30"
  # Domain-specific — model brand colors
  model-gemini: "#4285F4"
  model-claude: "#D89E6C"
  model-chatgpt: "#10A37F"
  # Status colors
  status-success: "#34A853"
  status-warning: "#FBBC04"
  status-error: "#E74C3C"
  status-premium: "#7C4DFF"
  # Inverse
  inverse-surface: "#FFFFFF"
  inverse-on-surface: "#0A0A0F"
typography:
  headline-display:
    fontFamily: Inter
    fontSize: 64px
    fontWeight: 900
    lineHeight: 1.1
    letterSpacing: -0.03em
  headline-lg:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: -0.015em
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
  code-md:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
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
  section-margin: 80px
  container-padding: 24px
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.on-tertiary}"
    typography: "{typography.label-lg}"
    rounded: "{rounded.lg}"
    height: 48px
    padding: 0 28px
  button-primary-hover:
    backgroundColor: "{colors.tertiary-container}"
  button-secondary:
    backgroundColor: transparent
    textColor: "{colors.tertiary}"
    typography: "{typography.label-lg}"
    rounded: "{rounded.lg}"
    height: 48px
    padding: 0 28px
  card-feature:
    backgroundColor: "{colors.surface-card}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.lg}"
    padding: "{spacing.lg}"
  card-pricing:
    backgroundColor: "{colors.surface-card}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.xl}"
    padding: "{spacing.xl}"
  nav-bar:
    backgroundColor: "{colors.surface-overlay}"
    textColor: "{colors.on-surface}"
    height: 64px
    padding: 0 24px
  input-field:
    backgroundColor: "{colors.surface-container-low}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    height: 48px
    padding: 0 16px
  badge-accent:
    backgroundColor: "{colors.surface-accent-tint}"
    textColor: "{colors.tertiary}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    padding: 4px 12px
  badge-model-gemini:
    backgroundColor: "{colors.model-gemini}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    padding: 4px 12px
  badge-model-claude:
    backgroundColor: "{colors.model-claude}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    padding: 4px 12px
  badge-model-chatgpt:
    backgroundColor: "{colors.model-chatgpt}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    padding: 4px 12px
  status-badge-success:
    backgroundColor: "{colors.status-success}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
  status-badge-warning:
    backgroundColor: "{colors.status-warning}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
  status-badge-error:
    backgroundColor: "{colors.status-error}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
  card-premium:
    backgroundColor: "{colors.status-premium}"
    textColor: "{colors.primary}"
    rounded: "{rounded.xl}"
    padding: "{spacing.xl}"
  modal-overlay:
    backgroundColor: "{colors.surface-dim}"
    textColor: "{colors.on-surface-elevated}"
    rounded: "{rounded.lg}"
    padding: "{spacing.xl}"
  sidebar-container:
    backgroundColor: "{colors.surface-container}"
    textColor: "{colors.on-surface-variant}"
    padding: "{spacing.lg}"
  card-elevated:
    backgroundColor: "{colors.surface-container-high}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.lg}"
    padding: "{spacing.lg}"
  button-secondary-outline:
    backgroundColor: transparent
    textColor: "{colors.secondary}"
    typography: "{typography.label-lg}"
    rounded: "{rounded.lg}"
    height: 48px
  chip-inverse:
    backgroundColor: "{colors.inverse-surface}"
    textColor: "{colors.inverse-on-surface}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    padding: 4px 12px
  page-canvas:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
  link-secondary:
    backgroundColor: transparent
    textColor: "{colors.on-secondary}"
    typography: "{typography.label-lg}"
---

## Overview

> MCP-validated design system — Source: https://kovelai.web.app
> Lighthouse: Accessibility 94 | Best Practices 100 | SEO 100

KovelAI is "The Shopify for Legal AI" — a privilege-protected AI routing
platform for law firms operating in the post-*United States v. Heppner*
landscape. The interface projects **transparent authority**: immutable,
trustworthy, and hyper-modern.

The visual identity centers on a near-black void punctuated by a signature
**cyan accent (#00BCD4)** that represents active intelligence and privileged
communication. The aesthetic is dark-mode-only glassmorphism — translucent
surfaces floating over a deep canvas, creating depth through light refraction
rather than shadow.

## Colors

The palette is built on a **near-black foundation** with a single dominant
accent color and model-specific semantic indicators:

- **Surface (#0A0A0F):** The near-black void canvas — not pure black, but a
  deep blue-black that feels dimensional rather than flat.
- **Primary (#FFFFFF):** Pure white ink for maximum contrast against the dark
  canvas — headlines, primary body text, and navigation labels.
- **On-Surface-Variant (#8B949E):** Cool slate-gray for body copy, descriptions,
  and secondary information that recedes behind primary content.
- **On-Surface-Elevated (#C9D1D9):** Warm silver for secondary text that needs
  more visual weight than the variant but less than pure white.
- **Tertiary / Accent Cyan (#00BCD4):** The signature interaction color — every
  CTA, link, and active state. Used sparingly to maintain signal-to-noise ratio.
- **Model-Gemini (#4285F4):** Google blue for Gemini model branding.
- **Model-Claude (#D89E6C):** Warm amber for Claude/Anthropic model branding.
- **Model-ChatGPT (#10A37F):** Teal green for ChatGPT model branding.
- **Status-Premium (#7C4DFF):** Deep purple for enterprise tier and premium features.

## Typography

The typography uses **Inter** as the exclusive typeface family, leveraging its
geometric clarity to project institutional precision against the dark
glassmorphic surfaces. **JetBrains Mono** is reserved for legal citations,
cryptographic hashes, and code-like metadata where monospace alignment
reinforces accuracy.

- **Headlines:** Inter at weights 700–900 with tight letter-spacing (-0.02em to
  -0.03em) for compressed, authoritative headings.
- **Body:** Inter Regular (400) at 16-18px ensures contemporary professionalism
  and long-form readability against dark backgrounds.
- **Labels:** Inter Medium/SemiBold at 12-14px with positive letter-spacing
  (0.02em–0.04em) for navigation, badges, and metadata.
- **Code:** JetBrains Mono 400 at 14px for Kovel attestation hashes, legal
  citation references, and technical identifiers.

## Layout

The layout follows a centered max-width container model with generous
negative space to let the dark background breathe. An 8px base spacing grid
governs all dimensions.

- **Container:** Max-width 1200px, centered with 24px side padding.
- **Sections:** 80px vertical separation between major content blocks.
- **Cards:** Grouped in responsive CSS grids with 16-24px gaps.
- **Hero:** Full-width with vertically stacked content — H1, subheadline,
  and dual CTA buttons with 16px vertical rhythm.

## Elevation & Depth

Depth is achieved purely through **transparency and blur** rather than
shadows. The visual stack creates the illusion of frosted glass layers
floating above the void canvas:

- **Level 0 (Canvas):** `#0A0A0F` — the solid void beneath everything.
- **Level 1 (Cards):** `rgba(13, 17, 23, 0.7)` — translucent dark surfaces
  with subtle 1px borders at 10% white opacity.
- **Level 2 (Nav/Overlays):** `rgba(10, 10, 15, 0.8)` with
  `backdrop-filter: blur(12px)` — floating glass panels.
- **Level 3 (Modals):** `rgba(10, 10, 15, 0.95)` with `backdrop-filter: blur(20px)`.
- **No box-shadows.** Depth comes from alpha channels and backdrop blur only.

## Shapes

The shape language is **moderately rounded** — warm enough to feel approachable
but technical enough to project institutional trust:

- **Cards:** `1rem` (16px) corner radius — the default containment shape.
- **Buttons:** `1rem` (16px) for primary CTAs, matching card corners.
- **Badges/Pills:** `9999px` (full) for accent badges and model indicators.
- **Inputs:** `0.75rem` (12px) for form fields — slightly sharper than cards.

## Components

### Navigation
Sticky glassmorphic navbar using surface-overlay with backdrop-blur. Contains
the "K" mark + "KovelAI" wordmark, nav links (Platform, For Law Firms,
Pricing, Post-Heppner, Investors), and a cyan "Start Free Trial" CTA button.

### Hero
Two-line H1 in display weight with line break. Subheadline in on-surface-variant.
Dual CTA: primary (solid cyan) and secondary (outline/ghost).

### Feature Cards
Dark translucent cards with 1px borders. Icon + heading + description layout.
Used in Platform, Six Tools, and How It Works sections.

### Pricing Cards
Three-tier layout (Solo/Practice/Enterprise). Cards use surface-card background
with accent highlighting on the recommended tier. Enterprise tier uses
status-premium (#7C4DFF) accent.

### Lead Capture
Email input field + submit button. Input uses surface-container-low background
with outline-variant border. Submit uses primary cyan button.

### Model Indicators
Each LLM model gets its branded color: Gemini (blue), Claude (amber),
ChatGPT (teal green). Applied as background tints at 10-12.5% opacity
inside pill-shaped badges.

## Do's and Don'ts

- Do use cyan (#00BCD4) only for interactive elements — links, buttons, active states
- Do use model-specific brand colors for their respective indicators only
- Do maintain the glassmorphic depth stack (canvas → card → overlay → modal)
- Do use JetBrains Mono for all legal citations and cryptographic hashes
- Don't use pure black (#000000) — always use the near-black surface (#0A0A0F)
- Don't apply box-shadows — use alpha transparency + backdrop-blur for depth
- Don't use the cyan accent decoratively — it signals interactivity
- Don't mix Inter and JetBrains Mono within the same text element
- Don't use rounded corners larger than 1.5rem (24px) — stay technical
