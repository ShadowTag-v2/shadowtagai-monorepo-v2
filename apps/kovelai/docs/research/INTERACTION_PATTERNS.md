# Interaction Patterns — KovelAI

> Extracted from [unusualmachines.com](https://www.unusualmachines.com/) via Chrome DevTools MCP.
> Format follows [ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template) INSPECTION_GUIDE.md Phase 5.

---

## Overview

Unusual Machines' site is **interaction-minimal** — a corporate investor relations site with very few dynamic behaviors. This is notable because it means we have a clean slate to add premium interactions for KovelAI.

---

## Animations

### Detected

| Animation | Element | Trigger | Mechanism | Duration/Easing |
|---|---|---|---|---|
| Header bg transition | StickyHeader | Scroll past hero | JS scroll listener | ~200-300ms ease |
| Cookie banner appear | CookieConsentBanner | Page load (delayed) | JS timer | Immediate |

### NOT Detected (absent from source)

- ❌ No scroll-driven reveal animations (no IntersectionObserver or animation-timeline)
- ❌ No parallax effects
- ❌ No Lottie animations
- ❌ No canvas-based animations
- ❌ No CSS `@keyframes` custom animations (beyond WP defaults)
- ❌ No page transition animations
- ❌ No loading skeleton states
- ❌ No scroll-snap sections

---

## Transitions

### Header Scroll State

```
Trigger:    scroll position > ~50px (estimated)
State A:    background: transparent; box-shadow: none
State B:    background: rgba(255,255,255,0.95); box-shadow: rgba(0,0,0,0.35) 1px 2px 8px 0px
Transition: ~200ms ease (estimated from observed behavior)
Mechanism:  JavaScript scroll event listener (no CSS animation-timeline)
```

### Link Hover

```
Trigger:    :hover
State A:    color: inherit; text-decoration: none
State B:    color: --brand-purple; text-decoration: underline (presumed)
Transition: Not observed (likely instant or ~150ms)
```

### Button Hover

```
Trigger:    :hover
State A:    background: --brand-purple-accent; cursor: default
State B:    background: (slightly lighter or darker); cursor: pointer
Transition: Not explicitly observed — likely CSS instant change
```

---

## Hover States

| Element | Property | Before | After | Transition |
|---|---|---|---|---|
| Nav links | `color` | Inherit | Brand purple | Not measured |
| News buttons | `cursor` | Default | Pointer | N/A |
| Social icons (footer) | `opacity` | `1` | Likely `0.7` or scale | Not measured |
| Quick link cards | `box-shadow` | Light | Elevated | Not measured |
| "See all" links | `text-decoration` | None | Underline | Instant |

---

## Interactive Components

### 1. Navigation Dropdown Menus

- **Elements with dropdowns:** "Media & Events", "Investors", "Contact", "About Us" (inferred from DOM — `StaticText` without link = dropdown trigger)
- **Mechanism:** Click or hover → dropdown panel appears
- **Animation:** Not extracted (page had cookie consent overlay blocking interaction sweep)
- **Mobile:** Presumably hamburger menu → slide-in drawer

### 2. Stock Ticker

- **Render:** Server-side rendered values (`$14.65`, `▼ -$1.48`, `4,865,874`)
- **Update mechanism:** Page reload (no WebSocket or polling detected)
- **Animation:** None — static values on each page load

### 3. News Item Buttons

- **Interaction model:** `click → navigation` (each button links to a press release page)
- **Feedback:** Cursor change to pointer
- **No transition animation** between states

### 4. Email Alert Form

- **Required field:** First text input (email)
- **Validation:** Client-side required attribute + reCAPTCHA
- **Submit behavior:** Form POST (traditional, not AJAX)
- **Error states:** Not extracted (would require submitting invalid data)
- **Success state:** Likely page redirect or inline message

### 5. Cookie Consent Banner

- **Interaction model:** Click-driven
- **Actions:** Accept All, Decline All, Show Details, individual category toggles
- **Dismiss behavior:** Banner removed from DOM or `display: none`
- **Cookie storage:** Sets consent preferences cookies

---

## KovelAI Interaction Upgrades

### Planned Additions (not present in source site)

| Feature | Implementation | Priority |
|---|---|---|
| **Scroll-reveal sections** | IntersectionObserver + CSS transforms | High |
| **Smooth hero gradient shift** | CSS `animation-timeline: scroll()` or JS | High |
| **Hover card lift** | `transform: translateY(-4px)` + `transition: 300ms ease` | High |
| **Button press feedback** | `transform: scale(0.98)` on `:active` | Medium |
| **Navigation slide-in mobile** | CSS transform + transition on drawer | High |
| **Page load stagger** | CSS `animation-delay` cascade on hero elements | Medium |
| **Focus rings** | `outline: 2px solid var(--kovel-accent)` + `outline-offset: 2px` | High |
| **Input focus labels** | Floating label pattern with `transition: 200ms ease` | Medium |
| **Tab content switching** | `opacity` + `transform` transitions, `300ms ease` | Medium |
| **Counter animation** | Metrics count-up from 0 on scroll intersect | Low |
| **Dark mode toggle** | CSS custom properties swap + `transition: background 300ms` | Medium |
| **Cookie consent slide-up** | `transform: translateY(100%)` → `translateY(0)` + `transition: 400ms ease-out` | Low |

### Motion Design Principles for KovelAI

1. **Purposeful motion only** — every animation serves a function (draw attention, confirm action, indicate state)
2. **Fast transitions** — 200–300ms for micro-interactions, 400ms for larger layout changes
3. **Ease-out for entries, ease-in for exits** — natural motion curves
4. **Reduce motion respect** — `prefers-reduced-motion: reduce` disables all non-essential animations
5. **No parallax** — professional SaaS sites avoid it; it adds visual noise without information
