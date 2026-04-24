---
version: alpha
name: The Sovereign Architect
description: >
  Engineered to evoke the gravitas of a high-end legal chambers fused with
  the surgical precision of advanced AI. The Digital Vault aesthetic.
colors:
  primary: "#d7e3fc"
  secondary: "#d0c5b5"
  tertiary: "#e6c487"
  neutral: "#071325"
  on-primary: "#071325"
  on-secondary: "#071325"
  on-tertiary: "#412d00"
  surface: "#071325"
  surface-container: "#142032"
  surface-container-low: "#101c2e"
  surface-container-high: "#1f2a3d"
  surface-container-highest: "#2a3548"
  surface-container-lowest: "#030e20"
  error: "#ffb4ab"
  on-error: "#690005"
  outline: "#998f81"
  outline-variant: "#4d463a"
  accent-gold: "#e6c487"
  accent-gold-container: "#c9a96e"
  accent-blue: "#aac7ff"
  accent-blue-container: "#3e90ff"
  accent-lavender: "#b8c8f2"
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 3.5rem
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 1.75rem
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: -0.01em
  body-md:
    fontFamily: Inter
    fontSize: 0.875rem
    fontWeight: 400
    lineHeight: 1.6
  body-sm:
    fontFamily: Inter
    fontSize: 0.8125rem
    fontWeight: 400
    lineHeight: 1.5
  label-sm:
    fontFamily: Inter
    fontSize: 0.6875rem
    fontWeight: 500
    letterSpacing: 0.05em
  label-md:
    fontFamily: Inter
    fontSize: 0.875rem
    fontWeight: 500
rounded:
  sm: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 48px
components:
  button-primary:
    backgroundColor: "linear-gradient(135deg, {colors.accent-gold}, {colors.accent-gold-container})"
    textColor: "{colors.on-tertiary}"
    typography: "{typography.label-md}"
    rounded: "{rounded.md}"
    padding: "12px 24px"
  button-primary-hover:
    boxShadow: "0 0 30px rgba(230, 196, 135, 0.25)"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.accent-blue}"
    border: "1px solid {colors.outline-variant}"
    rounded: "{rounded.md}"
    padding: "12px 24px"
  card-glass:
    backgroundColor: "rgba(42, 53, 72, 0.7)"
    backdropFilter: "blur(24px)"
    border: "1px solid rgba(77, 70, 58, 0.15)"
    rounded: "{rounded.xl}"
    padding: "{spacing.lg}"
  card-surface:
    backgroundColor: "{colors.surface-container-high}"
    rounded: "{rounded.xl}"
    padding: "{spacing.lg}"
  nav-glass:
    backgroundColor: "rgba(7, 19, 37, 0.8)"
    backdropFilter: "blur(20px)"
    border: "0 0 1px rgba(230, 196, 135, 0.08)"
  shadow-ambient:
    shadow1: "0 4px 20px rgba(0, 0, 0, 0.4)"
    shadow2: "0 0 1px rgba(170, 199, 255, 0.1)"
---

# Design System Document: The Sovereign Architect

## 1. Overview & Creative North Star

**The Creative North Star: "The Digital Vault"**

This design system is engineered to evoke the gravitas of a high-end legal chambers fused with the surgical precision of advanced AI. We are moving beyond the "SaaS template" look. Our goal is to create an environment that feels fortified yet weightless.

To achieve this, we employ **The Sovereign Architect** aesthetic: a philosophy that prioritizes editorial-grade white space, intentional asymmetry, and tonal depth. We avoid the "boxed-in" feel of traditional dashboards by using overlapping elements and high-contrast typography scales that guide the eye with the authority of a legal brief.

---

## 2. Colors & Atmospheric Depth

The color palette is rooted in a deep, nocturnal foundation, punctuated by accents that suggest heritage and digital intelligence.

### The Palette
- **Neutral / Background (`#071325`):** The "Ink." A deep, near-black navy that serves as the canvas.
- **Primary / Text (`#d7e3fc`):** The main ink color for headlines and body text on dark surfaces.
- **Tertiary / Gold (`#e6c487`):** The "Seal." Used for CTAs, high-priority actions, and symbols of authority.
- **Accent Blue (`#aac7ff`):** The "Current." Represents AI processing, data flows, and interactive elements.
- **Secondary / Warm Slate (`#d0c5b5`):** Supporting text, metadata, secondary descriptions.
- **Surface Tiers:** 6-level depth scale from `surface-container-lowest` (#030e20) to `surface-container-highest` (#2a3548).

### The "No-Line" Rule
Designers are prohibited from using 1px solid borders for sectioning. Boundaries are defined through:
1. **Background Color Shifts** — surface tier transitions
2. **Subtle Tonal Transitions** — dark-on-dark layering
3. **Negative Space** — the spacing scale creates "invisible" borders

### The "Glass & Gradient" Rule
- **Glassmorphism:** Floating elements use `surface-container-highest` at 70% opacity with `24px` backdrop-blur.
- **Signature Gradients:** Primary CTAs use `linear-gradient(135deg, #e6c487, #c9a96e)` for metallic luster.

---

## 3. Typography: Editorial Authority

**Inter** is used not just for readability, but as a structural element.

- **Display-LG (3.5rem / -0.02em):** Statement screens, hero sections. Bold, commanding.
- **Headline-MD (1.75rem / -0.01em):** Section headings. The "Title of the Brief."
- **Body-MD (0.875rem / 1.6 lh):** Workhorse. Legal text must remain approachable.
- **Label-SM (0.6875rem / 0.05em):** All-caps metadata. "Technical blueprint" feel.

---

## 4. Elevation & Depth: Tonal Layering

No traditional drop shadows. We use **Ambient Occlusion.**

- **Ambient Shadows:** Dual-shadow: `0 4px 20px rgba(0,0,0,0.4)` + `0 0 1px rgba(170,199,255,0.1)`.
- **Ghost Border Fallback:** `outline-variant` at 15% opacity. Felt, not seen.
- **Grid Patterns:** Subtle 24px dot-grid in hero sections for "Precision Engineering" feel.

---

## 5. Components

### Buttons
- **Primary:** Gradient `#e6c487` → `#c9a96e`. Label: `#412d00`. Glow on hover.
- **Secondary:** Transparent + ghost border. Text: `#aac7ff`.

### Cards
- **Surface Card:** `surface-container-high` background, `xl` roundness, `lg` padding.
- **Glass Card:** 70% opacity `surface-container-highest`, 24px blur, ghost-border top-edge highlight.

### Navigation
- **Glass Nav:** 80% opacity base + 20px backdrop-blur. Gold accent underline on active.

---

## 6. Do's and Don'ts

### Do:
- Use intentional asymmetry
- Use `secondary` (#d0c5b5) for secondary text
- Allow content to "breathe" — when in doubt, add 8px more padding

### Don't:
- Use pure white (#FFFFFF) — use `primary` (#d7e3fc)
- Use 1px borders for list separation — use tonal shifts
- Use sharp corners — stick to `md` (0.375rem) or `lg` (0.5rem)
