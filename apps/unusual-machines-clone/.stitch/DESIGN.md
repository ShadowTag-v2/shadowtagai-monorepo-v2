# Design System: Kinetic Foundry — Unusual Machines Clone

## Creative North Star
**Precision Engineering meets Minimalist Authority.**
Clean, industrial, yet editorial aesthetic — like a high-end technical dossier.

---

## Color Tokens

| Role | Hex | Usage |
|------|-----|-------|
| `--color-primary` | `#0d082a` | Near-black text, maximum weight |
| `--color-primary-container` | `#231f41` | Hero backgrounds, footer, dark sections |
| `--color-secondary` | `#0054cd` | Links, CTAs, accent |
| `--color-secondary-container` | `#316ee9` | Hover states, active accents |
| `--color-surface` | `#f8f9fb` | Page background |
| `--color-surface-low` | `#f3f4f6` | Section backgrounds |
| `--color-surface-lowest` | `#ffffff` | Card backgrounds |
| `--color-surface-high` | `#e7e8ea` | Subtle borders, separators |
| `--color-on-surface` | `#191c1e` | Body text |
| `--color-on-surface-variant` | `#48464e` | Secondary text |
| `--color-outline` | `#78767e` | Form borders |
| `--color-outline-variant` | `#c9c5ce` | Ghost borders (15% opacity) |
| `--color-error` | `#ba1a1a` | Error states |

## Typography Scale (Inter)

| Token | Size | Weight | Transform | Letter-Spacing |
|-------|------|--------|-----------|----------------|
| `display-lg` | 57px | 700 | uppercase | -0.02em |
| `display-md` | 45px | 700 | uppercase | -0.02em |
| `headline-lg` | 32px | 700 | uppercase | -0.02em |
| `headline-md` | 28px | 700 | uppercase | -0.01em |
| `title-lg` | 22px | 500 | none | 0 |
| `title-md` | 16px | 500 | none | 0.01em |
| `body-lg` | 16px | 400 | none | 0.05em |
| `body-md` | 14px | 400 | none | 0.025em |
| `label-lg` | 14px | 600 | uppercase | 0.1em |
| `label-md` | 12px | 600 | uppercase | 0.1em |

## Spacing Scale

| Token | Value |
|-------|-------|
| `--space-xs` | 4px |
| `--space-sm` | 8px |
| `--space-md` | 16px |
| `--space-lg` | 24px |
| `--space-xl` | 32px |
| `--space-2xl` | 48px |
| `--space-3xl` | 64px |
| `--space-4xl` | 96px |

## Corner Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | 2px | Chips, technical elements |
| `--radius-md` | 4px | Default containers |
| `--radius-lg` | 8px | Cards |
| `--radius-xl` | 12px | Buttons |

## Elevation

- No drop shadows on cards — use tonal layering
- Floating elements: `box-shadow: 0 20px 40px rgba(27, 23, 57, 0.06)`
- Ghost borders: `outline-variant` at 15% opacity

## Component Specs

### Buttons
- Primary: `#0054cd` fill, white text, 12px radius
- Secondary: Ghost, 15% outline-variant border, `#0054cd` text
- Tertiary: Underline text link, expands on hover

### Cards
- No divider lines — vertical whitespace separation
- `#ffffff` background on `#f3f4f6` section
- Critical data cards: 4px `#0d082a` top-border

### Navigation
- White background, sticky
- Navy text, hover → `#0054cd`
- Mega-dropdown with navy tint shadow

## Rules
- No 100% black — use `#0d082a` or `#191c1e`
- No 1px solid borders for section separation
- All headlines: ALL-CAPS, Inter Bold, tight letter-spacing
- Thin-stroke icons (1.5px) — never filled
