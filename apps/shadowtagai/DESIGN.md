---
name: ShadowTag Omega
colors:
  surface: "#08080E"
  surface-dim: "#050508"
  surface-bright: "#1A1A28"
  surface-container-lowest: "#030306"
  surface-container-low: "#0C0C16"
  surface-container: "#10101C"
  surface-container-high: "#161624"
  surface-container-highest: "#1E1E30"
  on-surface: "#E0E0F0"
  on-surface-variant: "#9898B0"
  inverse-surface: "#E0E0F0"
  inverse-on-surface: "#141422"
  outline: "#585878"
  outline-variant: "#2C2C44"
  surface-tint: "#7B6BCF"
  primary: "#7B6BCF"
  on-primary: "#FFFFFF"
  primary-container: "#1E1440"
  on-primary-container: "#B8A8E8"
  inverse-primary: "#453A78"
  secondary: "#22B8F0"
  on-secondary: "#00243A"
  secondary-container: "#003D5C"
  on-secondary-container: "#88D8FF"
  tertiary: "#FF4081"
  on-tertiary: "#3E0020"
  tertiary-container: "#5C0030"
  on-tertiary-container: "#FFB0CB"
  error: "#FF6B6B"
  on-error: "#4A0000"
  error-container: "#8B0000"
  on-error-container: "#FFB8B8"
  primary-fixed: "#C8B8F0"
  primary-fixed-dim: "#A090D8"
  on-primary-fixed: "#140C28"
  on-primary-fixed-variant: "#4A3A80"
  secondary-fixed: "#B0E4FF"
  secondary-fixed-dim: "#70C8F0"
  on-secondary-fixed: "#001824"
  on-secondary-fixed-variant: "#1A5070"
  tertiary-fixed: "#FFD0E0"
  tertiary-fixed-dim: "#FF90B8"
  on-tertiary-fixed: "#300018"
  on-tertiary-fixed-variant: "#701040"
  background: "#08080E"
  on-background: "#E0E0F0"
  surface-variant: "#1E1E30"
  success: "#40C057"
  on-success: "#082010"
  warning: "#FAB005"
  on-warning: "#281C04"
  accent-glow: "#22B8F01F"
  accent-hot: "#FF408126"
  accent-grid: "#7B6BCF0F"
typography:
  display-xl:
    fontFamily: Inter
    fontSize: 96px
    fontWeight: "900"
    lineHeight: 96px
    letterSpacing: -0.05em
  display-lg:
    fontFamily: Inter
    fontSize: 72px
    fontWeight: "800"
    lineHeight: 76px
    letterSpacing: -0.04em
  display-md:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: "700"
    lineHeight: 52px
    letterSpacing: -0.03em
  headline-lg:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: "700"
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: "600"
    lineHeight: 36px
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
    fontWeight: "700"
    lineHeight: 20px
    letterSpacing: 0.05em
    textTransform: uppercase
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: "700"
    lineHeight: 16px
    letterSpacing: 0.08em
    textTransform: uppercase
  code-lg:
    fontFamily: JetBrains Mono
    fontSize: 16px
    fontWeight: "500"
    lineHeight: 24px
  code-md:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: "400"
    lineHeight: 22px
  mono-display:
    fontFamily: JetBrains Mono
    fontSize: 48px
    fontWeight: "300"
    lineHeight: 56px
    letterSpacing: -0.02em
rounded:
  none: 0
  xs: 0.125rem
  sm: 0.25rem
  DEFAULT: 0.375rem
  md: 0.5rem
  lg: 0.75rem
  xl: 1rem
  pill: 50px
  full: 9999px
spacing:
  unit: 4px
  container-padding: 32px
  card-gap: 12px
  section-margin: 96px
  glass-padding: 28px
  nav-height: 64px
  grid-line: 1px
components:
  card-dark:
    backgroundColor: "{colors.surface-container}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: 24px
    border: 1px solid {colors.outline-variant}
  card-glass:
    backgroundColor: rgba(123, 107, 207, 0.05)
    textColor: "{colors.on-surface}"
    rounded: "{rounded.lg}"
    padding: "{spacing.glass-padding}"
    backdropFilter: blur(24px)
    border: 1px solid rgba(123, 107, 207, 0.10)
  card-hot:
    backgroundColor: rgba(255, 64, 129, 0.08)
    textColor: "{colors.on-surface}"
    rounded: "{rounded.lg}"
    padding: 24px
    border: 1px solid rgba(255, 64, 129, 0.15)
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-lg}"
    rounded: "{rounded.pill}"
    height: 44px
    padding: 0 24px
  button-primary-hover:
    backgroundColor: "{colors.primary-fixed-dim}"
    boxShadow: "0 0 24px rgba(123, 107, 207, 0.4)"
  button-danger:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.on-tertiary}"
    typography: "{typography.label-lg}"
    rounded: "{rounded.pill}"
    height: 44px
    padding: 0 24px
  button-ghost:
    backgroundColor: transparent
    textColor: "{colors.secondary}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.pill}"
    border: 1px solid {colors.outline-variant}
  button-ghost-hover:
    backgroundColor: "{colors.accent-glow}"
    borderColor: "{colors.secondary}"
  input-field:
    backgroundColor: "{colors.surface-container-lowest}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.DEFAULT}"
    padding: 12px 16px
    height: 44px
    border: 1px solid {colors.outline-variant}
  input-field-focus:
    border: 1px solid {colors.secondary}
    boxShadow: "0 0 0 2px rgba(34, 184, 240, 0.2)"
  nav-bar:
    backgroundColor: rgba(8, 8, 14, 0.90)
    backdropFilter: blur(16px)
    height: "{spacing.nav-height}"
    padding: 0 32px
    borderBottom: 1px solid {colors.outline-variant}
  terminal-block:
    backgroundColor: "{colors.surface-container-lowest}"
    textColor: "{colors.success}"
    typography: "{typography.code-md}"
    rounded: "{rounded.md}"
    padding: 20px
    border: 1px solid {colors.outline-variant}
  badge-product:
    backgroundColor: "{colors.primary-container}"
    textColor: "{colors.on-primary-container}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.pill}"
    padding: 4px 10px
  badge-status:
    backgroundColor: rgba(64, 192, 87, 0.15)
    textColor: "{colors.success}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.pill}"
    padding: 4px 10px
  stat-number:
    textColor: "{colors.secondary}"
    typography: "{typography.mono-display}"
  stat-label:
    textColor: "{colors.on-surface-variant}"
    typography: "{typography.label-sm}"
  hero-headline:
    textColor: "{colors.on-surface}"
    typography: "{typography.display-lg}"
    textTransform: uppercase
    letterSpacing: -0.04em
  footer:
    backgroundColor: "{colors.surface-container-lowest}"
    textColor: "{colors.on-surface-variant}"
    padding: 80px 32px 40px
    borderTop: 1px solid {colors.outline-variant}
---

## Brand & Style

ShadowTagAI is the parent technology company — the holding entity above KovelAI that represents the full AI infrastructure play. Where KovelAI is professional and legal-grade, ShadowTagAI is technical, aggressive, and uncompromising. The design language channels **military-grade technology** crossed with **hacker culture**: near-black surfaces, monospaced data displays, and hot-pink/cyan accent bursts against void-dark backgrounds.

Visual DNA from [Unusual Machines](https://www.unusualmachines.com/) is present but pushed to its limit:
- UMAC's deep purple (#291E44) darkens further to near-void `#1E1440`
- UMAC's blue-mist accent (#A0AED1) sharpens to full cyan `#22B8F0`
- UMAC's stock ticker → becomes a real-time system health dashboard
- UMAC's corporate hero → becomes a dense, data-rich command center
- UMAC's pill buttons → preserved, but with glow shadows on hover

The emotional register is **competence under pressure** — the interface of an organization that builds AI infrastructure at scale and is not afraid of complexity.

## Colors

The palette is near-monochromatic dark with two accent system: **cyan** for data/information and **hot pink** for actions/alerts. The purple primary serves as the bridge — present everywhere but never overwhelming.

- **Surface Stack:** Darker than KovelAI. The base `#08080E` is nearly black with a blue-violet micro-tint. 6 surface tokens provide granular elevation ordering.
- **Primary Purple:** `#7B6BCF` — slightly darker than KovelAI's `#8B7BCF`. Used for primary CTAs and links, never for backgrounds.
- **Secondary Cyan:** `#22B8F0` — the operational color. Data readouts, active states, terminal prompts, system-healthy indicators. Directly evolved from UMAC's `rgba(34,184,240,0.26)` accent.
- **Tertiary Hot Pink:** `#FF4081` — the attention color. Alerts, destructive actions, important badges, live indicators. Not present in UMAC; added for visual intensity.
- **Grid Lines:** Ultra-subtle `rgba(123,107,207,0.06)` — used for background grid patterns suggesting a control room / command center aesthetic.

## Typography

Like KovelAI, **Inter** is the primary face, but usage is more aggressive:
- Weights skew heavier (700–900 for headlines vs. KovelAI's 600–800)
- Label text uses `text-transform: uppercase` and wide letter-spacing (`0.05–0.08em`) — a military-technical convention
- **JetBrains Mono** has elevated status here: a dedicated `mono-display` style at 48px for statistics/dashboards, plus `code-lg` and `code-md` for terminal blocks

Type treatment:
- Headlines are ALWAYS uppercase with negative tracking (`-0.04em`) for a compressed, urgent feel
- Body text remains Normal case for readability
- Labels are small, loud, and spaced: `11px / 700 / uppercase / 0.08em tracking`

## Layout & Spacing

The layout is tighter and denser than KovelAI. ShadowTagAI shows more information per viewport.

- **Base unit:** 4px (half of KovelAI's 8px) — enabling finer-grained alignment for data-dense UIs
- **Container padding:** 32px (wider than KovelAI's 24px — more breathing room at extremes)
- **Card gap:** 12px (tighter than KovelAI's 16px — denser grid)
- **Section margin:** 96px (larger than KovelAI's 80px — dramatic section breaks)
- **Grid overlay:** An optional ultra-subtle grid pattern using `accent-grid` color creates a "command center" aesthetic in hero and dashboard sections

## Elevation & Depth

Similar glass system to KovelAI but colder and harder:

- **Level 1:** Near-void surface with optional grid overlay pattern
- **Level 2 (Card Dark):** `surface-container` with `outline-variant` border. No transparency — solid dark surfaces suggest physical hardware panels.
- **Level 3 (Card Glass):** Lower blur than KovelAI (`blur(24px)` vs `blur(20px)`) with lower opacity purple tint (`0.05` vs `0.08`). More transparent = more dangerous energy showing through.
- **Level 4 (Card Hot):** Hot pink tinted glass — `rgba(255, 64, 129, 0.08)` with pink border. Used for alert states, active processes, live data.
- **Glow effects:** Primary buttons gain `box-shadow: 0 0 24px rgba(123, 107, 207, 0.4)` on hover — a diffuse neon glow.

## Shapes

Sharper than KovelAI. The default radius is `0.375rem` (6px) — tight, mechanical corners. Only CTAs get the pill treatment.

- **Cards:** `md` (0.5rem / 8px) — barely rounded, industrial.
- **Buttons:** `pill` (50px) — UMAC heritage. The rounded CTA against sharp containers creates visual tension.
- **Inputs:** `DEFAULT` (0.375rem) — functional, not decorative.
- **Terminal blocks:** `md` (0.5rem) — code containers look like actual terminal windows.
- **No soft edges** — every surface is either sharp or pill. No in-between.

## Components

### Terminal Blocks

A unique component not present in KovelAI. Dark `surface-container-lowest` background with green text (success color), monospaced font, 1px border. Simulates actual terminal output for technical credibility.

### Navigation

Darker and tighter than KovelAI: `rgba(8,8,14,0.90)` with `blur(16px)`. 64px height (compact). Bottom border only — no shadow in default state. Shadow appears only on scroll.

### Hero

Dense, information-rich hero. Background uses animated grid lines or particle field. Stats rendered in `mono-display` (JetBrains Mono 48px) with cyan `secondary` color. Labels in `label-sm` uppercase. The hero is the command center — not a marketing billboard.

### Cards

Three tiers: Dark (data display), Glass (feature highlights), Hot (alerts/live). Each has distinct border treatment and background opacity. Hover states add subtle border brightening, never background lightening.

### Footer

Ultra-minimal. Single `outline-variant` top border separating it from content. `surface-container-lowest` background — the darkest usable surface. Copyright and links in `on-surface-variant` (muted). No heavy multi-column grid — ShadowTagAI's footer is a single line with essentials.

## Motion

Motion is restrained and purposeful — more subtle than KovelAI. ShadowTagAI's interface should feel stable, not animated.

- **Entry:** `opacity: 0 → 1` only (no translateY). Duration: `300ms ease-out`. Minimal stagger: `50ms`.
- **Hover:** Glow shadow addition only. No translation. Duration: `200ms ease`.
- **Active:** `scale(0.97)` — tighter compression than KovelAI's `0.98`. Duration: `80ms ease`.
- **Focus:** Ring appears instantly — no animation. Solid 2px.
- **Data updates:** Counter rolls use monospace font to prevent layout shift. `tabular-nums` for all numeric data.
- **Reduced motion:** All motion removed entirely (not softened) — this is a professional tool.
