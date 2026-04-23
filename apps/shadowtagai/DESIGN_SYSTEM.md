# ShadowTag AI — "Kinetic Void" Design System
> Version 1.0 | Status: CANONICAL | Developer-First Asymmetric Aesthetic

## Brand Philosophy
**Kinetic Void** — the interface is a weightless digital environment. Think spacesuit HUD meets terminal aesthetics. Brutal asymmetry, magenta accent + cyan signal, and endless depth through translucent layers.

---

## Color Palette

### Core Surface Tokens
| Token | Hex | Usage |
|-------|-----|-------|
| `--surface` | `#0d0d1a` | Base void / background |
| `--surface-dim` | `#0d0d1a` | Reduced emphasis areas |
| `--surface-container-low` | `#121220` | Structural sections |
| `--surface-container` | `#181828` | Mid-level cards |
| `--surface-container-high` | `#1e1e2f` | Elevated cards |
| `--surface-container-highest` | `#242437` | Interactive cards |
| `--surface-bright` | `#2a2a3f` | Highlighted sections |
| `--surface-variant` | `#242437` | Muted backgrounds |

### Primary (Magenta)
| Token | Hex | Usage |
|-------|-----|-------|
| `--primary` | `#f183ff` | Headlines, primary accent |
| `--primary-container` | `#ec6aff` | Active states, CTAs |
| `--primary-dim` | `#eb65ff` | Hover dimmed |
| `--primary-fixed` | `#ec6aff` | Fixed brand marks |
| `--primary-fixed-dim` | `#e64dff` | Gradient end |

### Secondary (Violet)
| Token | Hex | Usage |
|-------|-----|-------|
| `--secondary` | `#a68cff` | Supporting accent |
| `--secondary-container` | `#591adc` | Secondary CTA |

### Tertiary (Cyan)
| Token | Hex | Usage |
|-------|-----|-------|
| `--tertiary` | `#81ecff` | Signal color, data viz |
| `--tertiary-container` | `#00e3fd` | Active data elements |

### Text
| Token | Hex | Usage |
|-------|-----|-------|
| `--on-surface` | `#e9e6f9` | Primary text |
| `--on-surface-variant` | `#aba9bb` | Secondary text |
| `--outline` | `#757485` | Borders, dividers |
| `--outline-variant` | `#474656` | Ghost borders |

### Error
| Token | Hex | Usage |
|-------|-----|-------|
| `--error` | `#ff6e84` | Error states |
| `--error-container` | `#a70138` | Error backgrounds |

### Gradient Recipes
```css
--gradient-primary: linear-gradient(135deg, #f183ff, #ec6aff);
--gradient-primary-hover: linear-gradient(135deg, #ec6aff, #e64dff);
--gradient-secondary: linear-gradient(135deg, #a68cff, #7e51ff);
--gradient-cyan: linear-gradient(135deg, #81ecff, #00e3fd);
```

### Glass
```css
--glass-bg: rgba(13, 13, 26, 0.7);
--glass-blur: blur(24px);
--ghost-border: rgba(71, 70, 86, 0.15);
```

---

## Typography

| Role | Family | Weight | Size | Tracking |
|------|--------|--------|------|----------|
| Headline | Space Grotesk | 600–700 | `clamp(1.5rem, 3vw + 0.5rem, 4rem)` | `-0.02em` |
| Body | Manrope | 400–500 | `0.9rem – 1rem` | `0` |
| Label / Eyebrow | Manrope | 600 | `0.7rem` | `+0.15em` |
| Code | JetBrains Mono | 400 | `0.8rem` | `0` |

```html
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Manrope:wght@300;400;500;600;700&display=swap"
      rel="stylesheet" media="print" onload="this.media='all'" />
```

---

## Spacing Scale (rem)
`0.25 · 0.5 · 0.75 · 1 · 1.5 · 2 · 3 · 4 · 6 · 8 · 12`

---

## Border Radius
| Component | Value |
|-----------|-------|
| Button | `0.5rem` |
| Card | `0.75rem – 1rem` |
| Badge / Pill | `999px` |
| Input | `0.5rem` |

---

## Shadows & Glow
```css
/* Primary glow */
--glow-primary: 0 0 16px rgba(236, 106, 255, 0.3);
--glow-primary-strong: 0 0 32px rgba(236, 106, 255, 0.4);

/* Cyan glow */
--glow-cyan: 0 0 16px rgba(0, 227, 253, 0.3);

/* Card shadow */
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5),
            0 0 24px rgba(236, 106, 255, 0.05);
```

---

## Motion & Animation
| Property | Value |
|----------|-------|
| Duration base | `200ms` |
| Duration emphasis | `400ms` |
| Easing standard | `cubic-bezier(0.4, 0, 0.2, 1)` |
| Easing decelerate | `cubic-bezier(0, 0, 0.2, 1)` |

**Rule:** Animations serve information hierarchy, not delight. No bounce. No spring.

---

## Component Library

### Primary Button
```css
.btn-primary {
  padding: 0.75rem 2rem;
  background: var(--gradient-primary);
  color: var(--on-primary);
  font-weight: 700;
  font-size: 0.9rem;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.2s;
}
.btn-primary:hover {
  background: var(--gradient-primary-hover);
  transform: translateY(-1px);
}
```

### Glass Card
```css
.card-glass {
  background: var(--glass-bg);
  border: 1px solid var(--ghost-border);
  border-radius: 0.75rem;
  backdrop-filter: var(--glass-blur);
  box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}
```

---

## Accessibility
- All text on dark surfaces: min contrast ratio ≥ 4.5:1 (WCAG AA)
- Focus states: magenta outline, 2px offset
- Interactive elements: min 44×44px tap target
- `prefers-reduced-motion`: disable GPU transforms, keep opacity fades only

---

## Anti-Patterns (FORBIDDEN)
- ❌ Pure black `#000000` or pure white `#FFFFFF`
- ❌ Consumer-friendly rounded corners (24px+)
- ❌ Bouncy/spring animations
- ❌ Material Design elevation shadows
- ❌ Generic sans-serif fallbacks (must load Space Grotesk + Manrope)
- ❌ 1px solid horizontal dividers between list items
