# Layout Architecture — KovelAI

> Extracted from [unusualmachines.com](https://www.unusualmachines.com/) via Chrome DevTools MCP.
> Format follows [ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template) INSPECTION_GUIDE.md Phase 5.

---

## Grid System

- **No CSS Grid** detected — layout is entirely Flexbox + floats (WordPress legacy)
- **No CSS framework** — custom theme CSS
- **Container:** Implicit max-width containers, not standardized
- **Layout approach:** Vertical stack of full-width sections

---

## Column Layout

| Breakpoint | Columns | Notes |
|---|---|---|
| Desktop (≥1200px) | Mixed: 1-col sections, 2-col contact, 4-col quick links | No consistent grid |
| Tablet (~768px) | 2-col → 1-col transitions | Quick links condense |
| Mobile (≤480px) | 1-col throughout | Everything stacks |

---

## Max-Width

| Element | Max-Width |
|---|---|
| Main content area | Not explicitly constrained (full viewport) |
| Text content blocks | ~1200px effective (inferred from padding) |
| Hero section | Full viewport width |
| Footer | Full viewport width |

---

## Page Flow (Top to Bottom)

```
┌─────────────────────────────────────────────────┐
│ StickyHeader (z-index: high, position: fixed/   │
│ sticky with transparent → white glass bg)       │
├─────────────────────────────────────────────────┤
│ HeroSection (full-width, dark bg, stock ticker) │
│ Height: ~60vh to ~80vh                          │
├─────────────────────────────────────────────────┤
│ RecentNewsSection (purple-tinted bg)            │
│ 3 news buttons in vertical stack                │
├─────────────────────────────────────────────────┤
│ QuickLinksGrid (light bg)                       │
│ 4 icon cards in 2x2 or 4x1 row                 │
├─────────────────────────────────────────────────┤
│ UpcomingEventsSection (minimal)                 │
│ Empty state or event list                       │
├─────────────────────────────────────────────────┤
│ ContactSection (2-column)                       │
│ Investor Contact | Media Inquiries              │
├─────────────────────────────────────────────────┤
│ EmailAlertsSection (form area)                  │
│ 4 text fields + checkbox + button               │
├─────────────────────────────────────────────────┤
│ Footer (deep purple bg #291E44)                 │
│ Copyright + social icons + attribution          │
├─────────────────────────────────────────────────┤
│ CookieConsentBanner (overlay, z-top)            │
│ Fixed position, bottom or center of viewport    │
└─────────────────────────────────────────────────┘
```

---

## Sticky Elements

| Element | Position | Z-Index | Notes |
|---|---|---|---|
| Header/Nav | `position: fixed` or `sticky` | High (above content) | Glass bg on scroll |
| Cookie banner | `position: fixed` | Highest (above everything) | Dismissible |
| reCAPTCHA iframe | `position: fixed` | High (corner overlay) | Google badge |

---

## Z-Index Layers

| Layer | Z-Index (estimated) | Elements |
|---|---|---|
| Base content | `0` | All page sections |
| Sticky header | `100–1000` | Header/nav bar |
| Dropdowns/menus | `1000–5000` | Nav sub-menus |
| Cookie consent | `9999+` | Cookie banner overlay |
| reCAPTCHA | `2147483647` (max) | Google recaptcha badge |

---

## Scroll Behavior

- **No smooth scroll library** detected (no `.lenis`, `.locomotive-scroll` classes)
- **No scroll-snap** on any container
- **No parallax** effects detected
- **Standard browser scrolling** throughout
- **No infinite scroll** — all content loaded on page
- **No virtual scrolling** — simple DOM rendering

---

## Responsive Breakpoints (Observed)

| Breakpoint | Width | Changes |
|---|---|---|
| Desktop | ≥1200px | Full layout, all columns visible |
| Tablet | ~768px | Quick links → 2-col, contact stacks |
| Mobile | ≤480px | Single column, hamburger nav |

---

## KovelAI Layout Adaptation

### Proposed Changes:

1. **Grid system:** Adopt CSS Grid for main layout, Flexbox for component internals
2. **Max-width:** `max-width: 1280px` centered container with `padding: 0 24px`
3. **Breakpoints:** `640px` (sm), `768px` (md), `1024px` (lg), `1280px` (xl), `1536px` (2xl) — Tailwind defaults
4. **Sticky header:** Keep — works well for SaaS landing pages
5. **Add scroll-driven animations:** `IntersectionObserver` for section reveal animations
6. **Add smooth scroll:** CSS `scroll-behavior: smooth` on `html` (no dependency needed)
7. **Hero:** Full-viewport height (`100svh`) with gradient background instead of static image
8. **Footer:** Multi-column grid footer (4 columns: Product, Resources, Company, Legal)
