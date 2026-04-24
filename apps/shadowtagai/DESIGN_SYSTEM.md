# ShadowTag AI — DESIGN_SYSTEM.md
# Generated via Google Design MCP + Live CSS Extraction
# Design Language: "Kinetic Void"
# Source: https://shadowtagai.web.app/ (2026-04-24)

---

## Color Palette (Tokens = Roles)

### Semantic Roles

| Role | Hex | RGB | Usage |
|------|-----|-----|-------|
| **bg-primary** | `#09090b` | `rgb(9, 9, 11)` | Page canvas, deepest void |
| **bg-secondary** | `#0f0f14` | `rgb(15, 15, 20)` | Section backgrounds, alternating |
| **bg-tertiary** | `#16161d` | `rgb(22, 22, 29)` | Elevated surfaces |
| **bg-card** | `rgba(22, 22, 29, 0.7)` | — | Card backgrounds (glassmorphic) |
| **bg-card-hover** | `rgba(22, 22, 29, 0.9)` | — | Card hover state |
| **surface-lowest** | `#0c0c12` | `rgb(12, 12, 18)` | Lowest elevation surfaces |
| **accent-violet** | `#7c3aed` | `rgb(124, 58, 237)` | Primary accent, CTA, brand identity |
| **accent-violet-dim** | `rgba(124, 58, 237, 0.12)` | — | Subtle violet backgrounds |
| **accent-violet-glow** | `rgba(124, 58, 237, 0.25)` | — | Glow effects, hover halos |
| **accent-green** | `#0df274` | `rgb(13, 242, 116)` | Secondary accent, success, live indicators |
| **accent-green-dim** | `rgba(13, 242, 116, 0.12)` | — | Subtle green backgrounds |
| **accent-green-glow** | `rgba(13, 242, 116, 0.25)` | — | Green glow effects |
| **text-primary** | `#eeeef0` | `rgb(238, 238, 240)` | Headings, primary body text |
| **text-secondary** | `#8b8b9e` | `rgb(139, 139, 158)` | Labels, secondary descriptions |
| **text-muted** | `#5f5f72` | `rgb(95, 95, 114)` | Disabled, tertiary text |
| **border-subtle** | `rgba(255, 255, 255, 0.06)` | — | Default border (barely visible) |
| **border-hover** | `rgba(124, 58, 237, 0.25)` | — | Hover-state borders (violet glow) |
| **glass-nav** | `rgba(9, 9, 11, 0.8)` | — | Navigation glassmorphism |

### CSS Custom Properties (Live)
```css
:root {
  --bg-primary: #09090b;
  --bg-secondary: #0f0f14;
  --bg-tertiary: #16161d;
  --bg-card: rgba(22, 22, 29, 0.7);
  --bg-card-hover: rgba(22, 22, 29, 0.9);
  --surface-lowest: #0c0c12;
  --accent-violet: #7c3aed;
  --accent-violet-dim: rgba(124, 58, 237, 0.12);
  --accent-violet-glow: rgba(124, 58, 237, 0.25);
  --accent-green: #0df274;
  --accent-green-dim: rgba(13, 242, 116, 0.12);
  --accent-green-glow: rgba(13, 242, 116, 0.25);
  --text-primary: #eeeef0;
  --text-secondary: #8b8b9e;
  --text-muted: #5f5f72;
  --border-subtle: rgba(255, 255, 255, 0.06);
  --border-hover: rgba(124, 58, 237, 0.25);
  --glass-nav: rgba(9, 9, 11, 0.8);
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --section-pad: clamp(4rem, 8vw, 8rem) clamp(1.5rem, 4vw, 3rem);
  --max-w: 1200px;
  --ease-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

---

## Typography

| Role | Font | Weight | Size Range |
|------|------|--------|------------|
| **Primary** | Inter | 300–800 | 14px–72px |
| **Fallback** | -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif | — | — |

### Type Scale
| Element | Size | Weight | Line Height | Letter Spacing |
|---------|------|--------|-------------|----------------|
| H1 | clamp(36px, 6vw, 72px) | 800 | 1.05 | -0.03em |
| H2 | clamp(24px, 4vw, 48px) | 700 | 1.15 | -0.02em |
| H3 | clamp(18px, 2.5vw, 28px) | 600 | 1.3 | -0.01em |
| Body | 16px | 400 | 1.7 | 0em |
| Label | 11px | 700 | 1.4 | 0.15em (uppercase) |
| Micro | 10px | 500 | 1.3 | 0.1em |

---

## Gradients

| Name | CSS | Usage |
|------|-----|-------|
| **Brand Primary** | `linear-gradient(90deg, #7c3aed, #0df274)` | Hero highlight, CTA buttons |
| **Brand Diagonal** | `linear-gradient(135deg, #7c3aed, #0df274)` | Badge backgrounds, accent lines |
| **Vignette** | `linear-gradient(rgba(9,9,11,0.5) 0%, rgba(9,9,11,0.2) 30%, rgba(9,9,11,0.6) 70%, rgba(9,9,11,0.97) 100%)` | Hero image overlays |

---

## Shape & Border

| Token | Value | Usage |
|-------|-------|-------|
| **border-radius-sm** | 8px | Buttons, inline badges |
| **border-radius-md** | 16px | Cards |
| **border-radius-lg** | 24px | Hero containers, modal |
| **border-radius-pill** | 9999px | Status pills |
| **border-width** | 1px | Default, barely visible |

---

## Motion & Easing

| Token | Value | Usage |
|-------|-------|-------|
| **ease-out** | `cubic-bezier(0.4, 0, 0.2, 1)` | Standard transitions |
| **ease-spring** | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Bouncy entrance animations |
| **duration-fast** | 150ms | Hover states |
| **duration-normal** | 300ms | Card transitions |
| **duration-slow** | 600ms | Section reveals |

---

## Appearance

| Property | Value |
|----------|-------|
| **Mode** | Dark only |
| **Background** | `#09090b` (pure void black with zinc undertone) |
| **Glass Effect** | `backdrop-filter: blur(24px) saturate(180%)` on nav |
| **Section Padding** | `clamp(4rem, 8vw, 8rem) clamp(1.5rem, 4vw, 3rem)` |
| **Max Content Width** | `1200px` |

---

## WCAG Contrast Audit

| Pair | Ratio | Grade |
|------|-------|-------|
| `#eeeef0` on `#09090b` | 19.1:1 | AAA ✅ |
| `#7c3aed` on `#09090b` | 4.6:1 | AA ✅ |
| `#0df274` on `#09090b` | 10.5:1 | AAA ✅ |
| `#8b8b9e` on `#09090b` | 5.4:1 | AA ✅ |
| `#5f5f72` on `#09090b` | 3.2:1 | ⚠️ Large text only |

---

## Design DNA

- **Language:** "Kinetic Void" — sovereign AI power emerging from absolute darkness
- **Atmosphere:** Pure black void, violet-to-green gradient energy, glassmorphic surfaces
- **Motion:** Spring-bounce entrances, subtle card hovers, gradient-line animations
- **Character:** Assertive, sovereign, zero-trust aesthetic, bleeding-edge technology
- **Duality:** Violet = intelligence/compute, Green = execution/results
