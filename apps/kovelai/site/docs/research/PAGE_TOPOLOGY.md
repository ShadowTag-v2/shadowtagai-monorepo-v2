# Page Topology — unusualmachines.com

**Source:** https://www.unusualmachines.com
**Extracted:** 2026-04-25T18:07:44Z
**Viewport:** 1440 × 900 (desktop)
**Total Page Height:** 2864px
**Total Sections:** 6 (header, banner, highlights, quick-access, events, contact) + footer

---

## Visual Order (Top → Bottom)

| # | Section | Class | Tag | Top (px) | Height (px) | Position | z-index |
|---|---------|-------|-----|----------|-------------|----------|---------|
| 0 | Header/Nav | `.header` | `<header>` | 0 | 95 | **fixed** | 9 |
| 1 | Hero Banner | `.homeBanner` | `<section>` | 0 | 648 | relative | — |
| 2 | Recent News / Highlights | `.homeHighlights` | `<section>` | 648 | 605 | static | — |
| 3 | Quick Links | `.homeQuickAccess` | `<section>` | 1253 | 449 | relative | 1 |
| 4 | Upcoming Events | `.homeEvents` | `<section>` | 1702 | 346 | static | — |
| 5 | Contact | `.homeContact` | `<section>` | 2048 | 756 | relative | — |
| 6 | Footer | `.footer` | `<footer>` | 2804 | 60 | static | — |

---

## Fixed/Sticky Elements

- **Header (`.header`):** `position: fixed`, `z-index: 9`, `height: 95px`, transparent background (content shows through)

---

## Background Strategy

| Section | Background Type | Value |
|---------|----------------|-------|
| Header | Transparent | `rgba(0, 0, 0, 0)` |
| Banner | Full-bleed image | `USA_FC-1-1-1.jpg`, `background-size: cover`, `background-position: 50% 50%` |
| Highlights | Solid white | `rgb(255, 255, 255)` |
| Quick Links | Image with overlay | `img-Quick-Links.png`, semi-transparent overlay `rgba(26, 29, 31, 0.5)`, `background-attachment: fixed` |
| Events | Solid white | `rgb(255, 255, 255)` |
| Contact | Image with overlay | `USA_FC-6-1-1.jpg`, dark overlay `rgba(0, 0, 0, 0.5)`, `background-size: cover` |
| Footer | Solid dark purple | `rgb(41, 30, 68)` |

---

## Container Width

All sections use Bootstrap's `.container` → `max-width: 1140px` (centered within 1440px viewport = 150px padding per side).

---

## Typography Baseline

- **Body font:** Arial, 16px, `font-weight: 300`
- **Nav links:** 18px / 700 weight, white (`rgb(255, 255, 255)`)
- **Dropdown links:** 16px / 500 weight, purple (`rgb(83, 71, 138)`)
- **Section titles:** `.sectionTitle` class, `h2` tag
- **Stock ticker label:** 25px bold (price), 19px (change/volume)
