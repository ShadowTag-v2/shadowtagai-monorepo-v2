# Component Spec: Header / Navigation

**Source Section:** `.header` (index 0)
**Extracted from:** https://www.unusualmachines.com
**Target Component:** `src/components/Header.tsx`

---

## Extracted Styles (getComputedStyle)

```css
.header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 95px;
  background-color: rgba(0, 0, 0, 0); /* transparent */
  z-index: 9;
  padding: 0;
  display: block;
}
```

## Structure

```
header.header
  └── div.container
       └── div.row.no-gutters.align-items-center.justify-content-between
            ├── div.header__logo
            │    └── a.logo → img (166×41, "logo.png")
            └── div.header__content
                 ├── div.header__content__links (top utility bar)
                 └── nav.header__content__mainMenu (main nav)
```

## Navigation Items (Extracted)

| Text | Font Size | Weight | Color | Text Transform |
|------|-----------|--------|-------|----------------|
| Products | 18px | 700 | `rgb(255, 255, 255)` | none |
| Media & Events | 18px | 700 | `rgb(255, 255, 255)` | none |
| Investors | 18px | 700 | `rgb(255, 255, 255)` | none |

### Dropdown Items
| Text | Font Size | Weight | Color |
|------|-----------|--------|-------|
| Media Coverage | 16px | 500 | `rgb(83, 71, 138)` |
| Events | 16px | 500 | `rgb(83, 71, 138)` |
| Stock Information | 16px | 500 | `rgb(83, 71, 138)` |
| Press Releases | 16px | 500 | `rgb(83, 71, 138)` |
| Investor Deck | 16px | 500 | `rgb(83, 71, 138)` |

## Logo

- **Source:** `https://cdn-sites-assets.mziq.com/wp-content/uploads/sites/1374/2024/06/logo.png`
- **Natural size:** 166 × 41px
- **Alt text:** "Unusual Machines"

## KovelAI Adaptation Notes

- Replace logo with KovelAI wordmark
- Replace nav items with: Platform, Pricing, About, Contact
- Retain transparent header over hero pattern
- Add CTA button ("Get Started") on the right side
- Nav font: maintain 18px/700 for top-level items
