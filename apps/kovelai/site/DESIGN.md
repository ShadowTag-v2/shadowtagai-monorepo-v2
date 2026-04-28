# DESIGN.md — KovelAI "Sovereign Architect" Design System

> **Status:** Active | **Version:** 1.0 | **Stitch Asset:** `assets/16076fab918644088a3d948067760e83`

## 1. Creative North Star: "The Digital Vault"

An environment that feels fortified yet weightless. The **Sovereign Architect** aesthetic
prioritizes editorial-grade white space, intentional asymmetry, and tonal depth. We avoid
the "boxed-in" feel of traditional dashboards by using overlapping elements and high-contrast
typography scales that guide the eye with the authority of a legal brief.

## 2. Color Tokens

### Foundation
| Token | Value | Role |
|-------|-------|------|
| `--color-ink` | `#071325` | Background "Ink" — deep near-black navy |
| `--color-surface` | `#071325` | Main surface |
| `--color-surface-lowest` | `#030e20` | Deepest layer |
| `--color-surface-low` | `#101c2e` | Primary content "Nest" |
| `--color-surface-container` | `#142032` | Default container |
| `--color-surface-high` | `#1f2a3d` | Nested cards "Detail" |
| `--color-surface-highest` | `#2a3548` | Floating elements |
| `--color-gold` | `#e6c487` | Primary "Seal" — authority |
| `--color-gold-container` | `#c9a96e` | Gold gradient endpoint |
| `--color-gold-on` | `#412d00` | Text on gold surfaces |
| `--color-blue` | `#aac7ff` | Secondary "Current" — AI/data |
| `--color-blue-container` | `#3e90ff` | Blue interactive accent |
| `--color-lavender` | `#b8c8f2` | Tertiary accent |
| `--color-primary-text` | `#d7e3fc` | Primary text (never #FFF) |
| `--color-secondary-text` | `#d0c5b5` | Secondary text |
| `--color-outline` | `#998f81` | Outline visible |
| `--color-outline-variant` | `#4d463a` | Ghost borders (15% opacity only) |
| `--color-error` | `#ffb4ab` | Error states |

### The "No-Line" Rule
> **Prohibition:** No `1px solid` borders for sectioning or layout containment.
> Boundaries MUST use: background color shifts, tonal transitions, or negative space.
> **Exception:** Ghost borders at ≤15% opacity for accessibility fallbacks.

## 3. Typography

| Scale | Size | Weight | Tracking | Usage |
|-------|------|--------|----------|-------|
| Display-LG | 3.5rem | 700 | -0.02em | Hero statements |
| Headline-MD | 1.75rem | 700 | -0.01em | Section headings |
| Body-MD | 0.875rem | 400 | normal | Body text (line-height: 1.6) |
| Label-SM | 0.6875rem | 500 | 0.05em | Metadata, uppercase |

- Font: **Inter** (heading, body, label)
- Never use browser defaults. Always import Inter from Google Fonts.

## 4. Shape & Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | 0.25rem | Small pills |
| `--radius-md` | 0.375rem | Buttons, inputs |
| `--radius-lg` | 0.5rem | Cards, modals |
| `--radius-xl` | 0.75rem | Feature cards |
| `--radius-full` | 9999px | Badges, avatars |

## 5. Elevation & Depth

### Ambient Occlusion (No drop shadows)
```css
/* Floating components */
box-shadow:
  0 4px 20px rgba(0, 0, 0, 0.4),
  0 0 1px rgba(170, 199, 255, 0.1);

/* Ghost border fallback */
border: 1px solid rgba(77, 70, 58, 0.15);
```

### Glassmorphism
```css
background: rgba(42, 53, 72, 0.7);
backdrop-filter: blur(24px);
```

## 6. Gradient Signatures

```css
/* Gold CTA */
background: linear-gradient(135deg, #e6c487, #c9a96e);

/* Scroll progress */
background: linear-gradient(90deg, #e6c487, #aac7ff);
```

## 7. Spacing Scale

Based on Stitch `spacingScale: 2`:
- `4px → 8px → 16px → 24px → 32px → 48px → 64px → 96px`

## 8. Component Rules

### Buttons
- **Primary:** Gold gradient, `--color-gold-on` text, `--radius-md`, glow hover
- **Ghost:** Transparent, `--color-blue` text, ghost border, `--radius-md`

### Cards
- No dividers between items — use 16px spacing + background shift on hover
- Glass cards: `surface_highest` at 70% opacity + 24px backdrop-blur

### Inputs
- Background: `--color-surface-lowest`
- Focus: border transitions to `--color-blue` with 2px outer glow

## 9. Do's and Don'ts

### Do
- Use `on_surface` (#d7e3fc) — never pure white (#FFFFFF)
- Use `on_surface_variant` (#d0c5b5) for secondary text
- Allow generous padding — if you think it's enough, add 8px more
- Use intentional asymmetry for editorial layouts

### Don't
- Use `1px solid` borders for sectioning
- Use pure white (#FFFFFF)
- Use standard drop shadows
- Use sharp corners — minimum `--radius-md`
