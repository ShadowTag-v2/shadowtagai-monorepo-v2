---
name: KovelAI Chassis
colors:
  surface: "#0F0F1A"
  surface-dim: "#0A0A14"
  surface-bright: "#1E1E32"
  surface-container-lowest: "#080812"
  surface-container-low: "#121220"
  surface-container: "#161626"
  surface-container-high: "#1C1C30"
  surface-container-highest: "#24243C"
  on-surface: "#E8E8F0"
  on-surface-variant: "#A3A5B8"
  inverse-surface: "#E8E8F0"
  inverse-on-surface: "#1A1A2E"
  outline: "#666680"
  outline-variant: "#3A3A52"
  surface-tint: "#8B7BCF"
  primary: "#8B7BCF"
  on-primary: "#FFFFFF"
  primary-container: "#291E44"
  on-primary-container: "#C4B8E8"
  inverse-primary: "#53478A"
  secondary: "#A0AED1"
  on-secondary: "#1A2540"
  secondary-container: "#2A3A5C"
  on-secondary-container: "#B8C6E0"
  tertiary: "#E8B4D0"
  on-tertiary: "#4A1A36"
  tertiary-container: "#6B3050"
  on-tertiary-container: "#F0D0E4"
  error: "#FFB4AB"
  on-error: "#690005"
  error-container: "#93000A"
  on-error-container: "#FFDAD6"
  primary-fixed: "#D4C8F4"
  primary-fixed-dim: "#B0A0DC"
  on-primary-fixed: "#1A1030"
  on-primary-fixed-variant: "#57458F"
  secondary-fixed: "#D0E4FF"
  secondary-fixed-dim: "#A0AED1"
  on-secondary-fixed: "#001D35"
  on-secondary-fixed-variant: "#304B68"
  tertiary-fixed: "#FFD8E7"
  tertiary-fixed-dim: "#FFAFD3"
  on-tertiary-fixed: "#3D0026"
  on-tertiary-fixed-variant: "#85145A"
  background: "#0F0F1A"
  on-background: "#E8E8F0"
  surface-variant: "#24243C"
  success: "#69DB7C"
  on-success: "#0A2E14"
  warning: "#FFD43B"
  on-warning: "#2E2710"
  accent-glow: "#8B7BCF26"
  accent-cyan: "#22B8F042"
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 72px
    fontWeight: "800"
    lineHeight: 76px
    letterSpacing: -0.04em
  display-md:
    fontFamily: Inter
    fontSize: 44px
    fontWeight: "700"
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: "700"
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: "600"
    lineHeight: 32px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: "400"
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: "400"
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: "400"
    lineHeight: 20px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: "600"
    lineHeight: 20px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: "600"
    lineHeight: 16px
    letterSpacing: 0.05em
  code:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: "400"
    lineHeight: 22px
    letterSpacing: 0em
rounded:
  xs: 0.125rem
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.25rem
  2xl: 1.5rem
  pill: 50px
  full: 9999px
spacing:
  unit: 8px
  container-padding: 24px
  card-gap: 16px
  section-margin: 80px
  glass-padding: 24px
  nav-height: 72px
components:
  card-standard:
    backgroundColor: "{colors.surface-container}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.lg}"
    padding: 24px
    border: 1px solid {colors.outline-variant}
  card-elevated:
    backgroundColor: "{colors.surface-container-high}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.xl}"
    padding: 24px
    boxShadow: "0 8px 32px rgba(0, 0, 0, 0.25)"
  card-glass:
    backgroundColor: rgba(139, 123, 207, 0.08)
    textColor: "{colors.on-surface}"
    rounded: "{rounded.xl}"
    padding: "{spacing.glass-padding}"
    backdropFilter: blur(20px)
    border: 1px solid rgba(139, 123, 207, 0.15)
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-lg}"
    rounded: "{rounded.pill}"
    height: 48px
    padding: 0 28px
  button-primary-hover:
    backgroundColor: "{colors.primary-fixed-dim}"
    transform: translateY(-1px)
    boxShadow: "0 4px 16px rgba(139, 123, 207, 0.35)"
  button-secondary:
    backgroundColor: transparent
    textColor: "{colors.primary}"
    typography: "{typography.label-lg}"
    rounded: "{rounded.pill}"
    border: 1.5px solid {colors.primary}
    height: 48px
    padding: 0 28px
  button-ghost:
    backgroundColor: rgba(139, 123, 207, 0.08)
    textColor: "{colors.primary}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.pill}"
  input-field:
    backgroundColor: "{colors.surface-container-low}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: 16px 20px
    height: 52px
    border: 1px solid {colors.outline-variant}
  input-field-focus:
    border: 2px solid {colors.primary}
    boxShadow: "0 0 0 3px rgba(139, 123, 207, 0.15)"
  nav-bar:
    backgroundColor: rgba(15, 15, 26, 0.85)
    backdropFilter: blur(20px)
    height: "{spacing.nav-height}"
    padding: 0 24px
    borderBottom: 1px solid {colors.outline-variant}
  nav-bar-scrolled:
    backgroundColor: rgba(15, 15, 26, 0.95)
    boxShadow: "0 4px 20px rgba(0, 0, 0, 0.3)"
  badge:
    backgroundColor: "{colors.primary-container}"
    textColor: "{colors.on-primary-container}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.pill}"
    padding: 4px 12px
  metric-display:
    textColor: "{colors.primary}"
    typography: "{typography.display-lg}"
  metric-label:
    textColor: "{colors.on-surface-variant}"
    typography: "{typography.label-sm}"
  hero-headline:
    textColor: "{colors.on-surface}"
    typography: "{typography.display-md}"
    textTransform: uppercase
  section-title:
    textColor: "{colors.on-surface}"
    typography: "{typography.headline-lg}"
  footer:
    backgroundColor: "{colors.primary-container}"
    textColor: "{colors.on-primary-container}"
    padding: 64px 24px 32px
---

## Brand & Style

KovelAI is the AI-first legal intelligence platform operating under the ShadowTagAI umbrella. The design language draws visual DNA from [Unusual Machines](https://www.unusualmachines.com/) — a corporate/investor-relations aesthetic built on deep purples and authoritative typography — but evolves it into a modern dark-mode SaaS experience befitting an AI technology company.

The visual personality is **authoritative yet approachable**: deep enough to convey legal gravitas, modern enough to signal cutting-edge AI. Where Unusual Machines uses Arial on a WordPress stack, KovelAI uses Inter on Next.js. Where UMAC uses static rendered pages, KovelAI uses scroll-driven animations and glassmorphic depth.

The design reference extraction from unusualmachines.com yielded these foundational principles:
- **Deep purple brand hierarchy** (#291E44 → #53478A → #57458F) mapped to `primary-container` → `inverse-primary` → `primary-fixed-variant`
- **Stock ticker hero pattern** → adapted to AI metrics dashboard
- **Simple vertical page flow** → enhanced with IntersectionObserver reveals
- **Pill-shaped CTAs (50px radius)** → preserved as `rounded-pill`
- **Two-tier header** (utility bar + main nav) → simplified to single sticky nav

## Colors

The color strategy is dark-mode-first with purple as the dominant brand hue. The M3-inspired palette extracts from UMAC's deep purple (#291E44, #53478A, #57458F) and blue-mist accent (#A0AED1, #9DAED4) as secondary.

- **Surface Colors:** A monochromatic dark blue-black range (`#0F0F1A` base) with purple undertones. No pure black — the darkest value is `#080812`.
- **Primary:** Muted lavender-purple `#8B7BCF` — softer than UMAC's `#57458F` for screen readability at small sizes. The UMAC purple lives in `primary-container` (#291E44) for dark bg sections.
- **Secondary:** Blue-mist `#A0AED1` from UMAC's accent palette. Professional, calming tone for secondary CTAs and info surfaces.
- **Accent Glow:** Translucent primary at 15% for ambient hover/focus effects. UMAC's `rgba(34,184,240,0.26)` cyan accent preserved as `accent-cyan` for subtle highlights.
- **Semantic:** Standard error (red), success (green), warning (amber). UMAC's stock-ticker red (#DF0000) informed the error palette.
- **WCAG:** All foreground-on-background combinations target AA minimum (4.5:1 ratio). `on-surface` (#E8E8F0) on `surface` (#0F0F1A) clears 15:1.

## Typography

The type system upgrades from UMAC's system font stack (Arial) to **Inter** — the industry-standard for data-dense SaaS interfaces. Inter's optical sizing and extensive weight range (100–900) enable clear hierarchies without fallback rendering differences.

- **Display:** 72px/800 for hero numerics (AI metrics, key stats). UMAC's hero was 44px/600 — we scale up for impact.
- **Headline:** 32px/700 for section titles, preserving UMAC's `h3` weight.
- **Body:** 16px/400 base — slightly heavier apparent weight than UMAC's 300 body weight, improving readability.
- **Code:** JetBrains Mono for code snippets, API references, and technical data. Not present in UMAC; added for AI/developer audience.
- **Treatment:** UMAC's uppercase `text-transform` on hero headings is preserved for the `hero-headline` component. All other headings use sentence case.

## Layout & Spacing

The layout evolves from UMAC's WordPress-generated flexbox-and-floats page into a CSS Grid + Flexbox hybrid appropriate for a Next.js 15 single-page app.

- **Rhythm:** 8px base unit (UMAC used WP's 0.44rem–5.06rem spacing scale; we normalize to 8px grid).
- **Container:** `max-width: 1280px`, centered with 24px horizontal padding. UMAC had no explicit max-width.
- **Section vertical spacing:** 80px between major sections (UMAC had inconsistent ~40–80px). Generous negative space signals premium.
- **Nav height:** 72px — slightly taller than UMAC's compact header, accommodating a mobile-first touch target zone.

## Elevation & Depth

UMAC's elevation was minimal — three basic shadows (sm: `0 4px 4px`, md: `0 0 5px`, lg: `1px 2px 8px`). KovelAI introduces a glass-based depth system for the dark theme.

- **Level 1 (Base):** Dark surface with purple-tinted gradient undertones.
- **Level 2 (Standard Card):** `surface-container` with 1px `outline-variant` border. No blur.
- **Level 3 (Glass Card):** `backdrop-filter: blur(20px)`, `background: rgba(139, 123, 207, 0.08)` with 1px purple-tint border. Used for feature highlights.
- **Level 4 (Elevated):** `surface-container-high` with `box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25)`. Modals, dropdowns.
- **Edge definition:** All glassmorphic surfaces carry a 1px border at `rgba(139, 123, 207, 0.15)` — the primary color at very low opacity.

## Shapes

The shape language blends UMAC's pill-button aesthetic with modern card UI. UMAC used six distinct radii (2px, 3px, 5px, 6px, 20px, 50px) without clear purpose. KovelAI rationalizes to a semantic scale.

- **Cards/Containers:** `md` (0.75rem / 12px) to `xl` (1.25rem / 20px). Not square, not bubble — professional.
- **Buttons/CTAs:** `pill` (50px) — directly from UMAC's CTA button radius. Distinctive, brand-level shape.
- **Inputs:** `md` (0.75rem) — slightly softer than UMAC's 5–6px inputs.
- **Badges/Tags:** `pill` — consistent with CTAs for visual cohesion.
- **Icons:** No border radius — icons are transparent on their background.

## Components

### Navigation

The sticky navbar inherits UMAC's scroll-responsive header pattern (transparent → opaque on scroll) but implements it with `backdrop-filter: blur(20px)` and a subtle bottom border instead of UMAC's opaque white. The transition is `300ms ease` for background and shadow properties.

### Hero Section

UMAC's hero combined a dark background image with an overlay and stock ticker data. KovelAI replaces this with an animated mesh gradient background (CSS `@property` animated gradients or canvas) and AI metrics dashboard (model accuracy, cases processed, uptime). The `hero-headline` displays in uppercase, preserving UMAC's typographic treatment at a larger `display-md` scale.

### Cards

Standard cards use the solid `surface-container` approach for content-heavy layouts (news, documentation). Glass cards with backdrop blur are reserved for feature highlights and hero-adjacent metrics. Both share the same padding and gap values for visual consistency.

### Footer

UMAC's footer was a simple single-row with copyright, social links, and attribution on deep purple (#291E44). KovelAI expands to a full multi-column footer grid (Product, Resources, Company, Legal) using the same `primary-container` background, maintaining brand continuity while adding information density.

## Motion

UMAC had almost no motion design — only the header scroll transition and potential link hover states. KovelAI adds purposeful, performance-conscious motion.

- **Entry animations:** `opacity: 0 → 1` + `translateY(20px → 0)` on viewport intersection. Duration: `500ms ease-out`. Stagger: `100ms` between siblings.
- **Hover feedback:** `translateY(-2px)` + shadow increase on cards and CTAs. Duration: `200ms ease`.
- **Active press:** `scale(0.98)` on buttons. Duration: `100ms ease`.
- **Focus rings:** `outline: 2px solid var(--primary)` + `outline-offset: 2px`. No animation.
- **Page load:** Hero content stagger — heading, then subtext, then CTA, each `150ms` delayed.
- **Reduced motion:** All non-essential animations gated behind `prefers-reduced-motion: no-preference`.
