# KovelAI Design System
> Version 1.0 | Status: CANONICAL | Legal-Tech Precision Aesthetic

## Brand Philosophy
**Structured Precision** — not creative fluidity. Every visual decision must signal order, security, and the ability to process massive amounts of privileged legal data instantly. The aesthetic is the interior of a digital vault inside a white-shoe law firm.

---

## Color Palette

### Core Tokens
| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| `--navy` | `#0a0f1e` | `10, 15, 30` | Primary background, hero void |
| `--navy-mid` | `#131c31` | `19, 28, 49` | Card surfaces, elevated layers |
| `--navy-light` | `#1e2a3a` | `30, 42, 58` | Borders, dividers, slate layer |
| `--gold` | `#c9a96e` | `201, 169, 110` | Primary accent, CTA, nodes |
| `--gold-dim` | `rgba(201,169,110,0.15)` | — | Borders, glass panels |
| `--gold-glow` | `rgba(201,169,110,0.35)` | — | Box shadows, halos |
| `--warm-white` | `#f5ede0` | `245, 237, 224` | Body text, on-dark headings |
| `--slate` | `#8da3be` | `141, 163, 190` | Secondary text, labels |
| `--danger` | `#e05252` | — | Error states only |
| `--success` | `#4caf80` | — | Confirmation states only |

### Gradient Recipes
```css
/* Hero CTA button */
background: linear-gradient(135deg, #c9a96e 0%, #a07840 100%);

/* Gold text shimmer */
background: linear-gradient(135deg, #c9a96e, #f5ede0 60%, #c9a96e);
-webkit-background-clip: text; -webkit-text-fill-color: transparent;

/* Card glass */
background: rgba(19, 28, 49, 0.7);
backdrop-filter: blur(24px);
border: 1px solid rgba(201, 169, 110, 0.15);
```

---

## Typography

| Role | Family | Weight | Size | Tracking |
|------|--------|--------|------|----------|
| Headline | Inter | 800 | `clamp(1.75rem, 3.5vw + 0.5rem, 4.5rem)` | `-0.04em` |
| Sub-headline | Inter | 600 | `1.5rem – 2rem` | `-0.02em` |
| Body | Inter | 400 | `0.9rem – 1rem` | `0` |
| Label / Eyebrow | Inter | 700 | `0.65rem – 0.75rem` | `+0.2em` |
| Code | system mono | 400 | `0.8rem` | `0` |

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
      rel="stylesheet" media="print" onload="this.media='all'" />
```

---

## Spacing Scale (rem)
`0.25 · 0.5 · 0.75 · 1 · 1.5 · 2 · 3 · 4 · 6 · 8 · 12`

---

## Border Radius
| Component | Value |
|-----------|-------|
| Button | `0.5rem` (8px) |
| Card | `1rem – 1.25rem` |
| Badge / Pill | `999px` |
| Input | `0.5rem` |

---

## Shadows
```css
/* Card glow */
box-shadow: 0 0 40px rgba(201, 169, 110, 0.06), 0 8px 32px rgba(0, 0, 0, 0.4);

/* CTA button hover */
box-shadow: 0 4px 20px rgba(201, 169, 110, 0.35);

/* Focus ring */
outline: 2px solid rgba(201, 169, 110, 0.6);
outline-offset: 2px;
```

---

## Motion & Animation
| Property | Value |
|----------|-------|
| Duration base | `200ms` |
| Duration emphasis | `400ms` |
| Duration hero | `8s loop` |
| Easing standard | `cubic-bezier(0.4, 0, 0.2, 1)` |
| Easing decelerate | `cubic-bezier(0, 0, 0.2, 1)` |

```css
/* Standard interactive transition */
transition: opacity 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;

/* Hover lift */
transform: translateY(-2px);
```
**Rule:** No bouncy easing. No spring physics. Precision motion only — every animation serves information, not delight.

---

## Hero Background Spec
→ See `.stitch/kovelai-hero-video-spec.md` for the complete Veo 3.1 generation spec.

---

## Component Library

### Primary Button
```html
<button class="btn-primary">Schedule Demo</button>
```
```css
.btn-primary {
  padding: 0.75rem 2rem;
  background: linear-gradient(135deg, #c9a96e 0%, #a07840 100%);
  color: #0a0f1e;
  font-weight: 700;
  font-size: 0.9rem;
  border-radius: 0.5rem;
  letter-spacing: 0.04em;
  border: none;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.2s;
}
.btn-primary:hover { opacity: 0.88; transform: translateY(-1px); }
```

### Glass Card
```css
.card-glass {
  background: rgba(19, 28, 49, 0.7);
  border: 1px solid rgba(201, 169, 110, 0.15);
  border-radius: 1rem;
  backdrop-filter: blur(24px);
  box-shadow: 0 0 40px rgba(201, 169, 110, 0.06),
              0 8px 32px rgba(0,0,0,0.4);
}
```

### Gold Eyebrow Label
```css
.label-eyebrow {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: #c9a96e;
}
```

---

## Accessibility
- All text on `--navy` / `--navy-mid`: min contrast ratio ≥ 4.5:1 (WCAG AA)
- Focus states: gold outline, 2px offset
- Interactive elements: min 44×44px tap target
- `prefers-reduced-motion`: disable all GPU transforms, keep opacity fades only

---

## Anti-Patterns (FORBIDDEN)
- ❌ Bright white backgrounds
- ❌ Consumer blue/purple gradients
- ❌ Bouncy/spring animations
- ❌ Generic sans-serif fallbacks (must load Inter)
- ❌ Decorative elements that don't encode data meaning
- ❌ More than 2 accent colors per section
