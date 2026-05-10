# Page Topology — unusualmachines.com

> Source map for adapted KovelAI and ShadowTagAI page structures.
> Extracted 2026-04-25 via Chrome DevTools MCP.

---

## Section Order (top → bottom)

| # | Section | Height (est.) | Position | Interaction Model | Z-Layer |
|---|---|---|---|---|---|
| 0 | **StickyHeader** | 80–100px | `fixed/sticky` | Scroll-responsive | Z: 1000 |
| 1 | **HeroSection** | 60–80vh | Flow | Static + live data | Z: 0 |
| 2 | **RecentNewsSection** | ~400px | Flow | Click-to-navigate | Z: 0 |
| 3 | **QuickLinksGrid** | ~250px | Flow | Click-to-navigate | Z: 0 |
| 4 | **UpcomingEventsSection** | ~150px | Flow | Static (empty state) | Z: 0 |
| 5 | **ContactSection** | ~350px | Flow | Static | Z: 0 |
| 6 | **EmailAlertsSection** | ~300px | Flow | Form input | Z: 0 |
| 7 | **Footer** | ~100px | Flow | Click (social links) | Z: 0 |
| OV | **CookieConsentBanner** | ~300px | Fixed overlay | Click-to-dismiss | Z: 9999 |
| OV | **reCAPTCHA Badge** | 28px | Fixed overlay | Auto | Z: max |

---

## Visual Zones

```
┌──────────────────────────────────────────────────────────────┐
│ ZONE 1: DARK THEME (purple/dark bg)                          │
│ ├─ StickyHeader (transparent bg → glass on scroll)           │
│ └─ HeroSection (dark overlay on bg image)                    │
│    ├─ Hero Headline (white, uppercase, 44px)                 │
│    ├─ Stock Ticker (NYSE: UMAC, $14.65, ▼-$1.48)            │
│    └─ Volume + Date                                          │
├──────────────────────────────────────────────────────────────┤
│ ZONE 2: MIXED THEME (alternating light/dark sections)        │
│ ├─ RecentNews (dark bg with purple tint)                     │
│ │   └─ 3x news item buttons + "See all" link                │
│ ├─ QuickLinks (light bg)                                     │
│ │   └─ 4x icon+label cards in grid                          │
│ ├─ UpcomingEvents (light bg)                                 │
│ │   └─ Empty state: "No upcoming events!"                    │
│ ├─ Contact (light bg, 2-column)                              │
│ │   ├─ Investor Contact (left)                               │
│ │   └─ Media Inquiries (right)                               │
│ └─ EmailAlerts (light bg)                                    │
│     └─ 4-field form + checkbox + reCAPTCHA                   │
├──────────────────────────────────────────────────────────────┤
│ ZONE 3: FOOTER (deep purple bg #291E44)                      │
│ └─ Copyright + Social Icons + MZ Attribution                 │
└──────────────────────────────────────────────────────────────┘

OVERLAYS (independent z-layer):
  ├─ CookieConsentBanner (modal overlay, z: 9999)
  └─ reCAPTCHA badge (corner, z: max)
```

---

## Dependencies Between Sections

| Dependency | From | To | Nature |
|---|---|---|---|
| Header overlay | StickyHeader | All sections | Z-index above content |
| Hero bg bleed | HeroSection | Header | Header starts transparent over hero |
| Cookie overlay | CookieConsentBanner | All | Blocks interaction until dismissed |

---

## Color Zone Transitions

| Transition | From | To | Boundary |
|---|---|---|---|
| Dark → Dark/Purple | Hero | RecentNews | Hard edge (no gradient) |
| Dark → Light | RecentNews | QuickLinks | Hard edge |
| Light → Light | QuickLinks | Events → Contact → Email | No visible boundary |
| Light → Dark Purple | EmailAlerts | Footer | Hard edge (#291E44 bg starts) |

---

## Responsive Layout Changes

### Desktop (1440px)
- Full nav visible in header
- Hero: large text, stock ticker inline
- QuickLinks: 4-column grid
- Contact: 2-column side-by-side

### Tablet (768px)
- Nav may condense (fewer items visible)
- QuickLinks: 2×2 grid
- Contact: still 2-column (narrower)

### Mobile (390px)
- Hamburger menu
- QuickLinks: 2×1 or 1-column stack
- Contact: stacked single column
- All sections full-width
