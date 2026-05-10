# Design Tokens — KovelAI

> Extracted from [unusualmachines.com](https://www.unusualmachines.com/) via Chrome DevTools MCP `getComputedStyle()`.
> Adapted for KovelAI brand identity (AI-first legal technology platform).
> Format follows [ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template) INSPECTION_GUIDE.md Phase 5.

## Source Analysis

- **Target:** https://www.unusualmachines.com/ (WordPress, custom MZ Group theme)
- **Tech stack:** WordPress + custom PHP, no CSS framework, no smooth-scroll library
- **Color model:** Hex/RGB (we convert to oklch for Tailwind v4 compatibility)
- **Font loading:** System fonts + self-hosted (no Google Fonts CDN detected)

---

## Colors

### Primary Palette (from getComputedStyle)

| Token Name | Hex | RGB | oklch | Usage |
|---|---|---|---|---|
| `--brand-deep-purple` | `#291E44` | `rgb(41, 30, 68)` | `oklch(0.22 0.06 285)` | Footer bg, dark sections |
| `--brand-purple` | `#53478A` | `rgb(83, 71, 138)` | `oklch(0.39 0.10 285)` | Primary brand, headings text |
| `--brand-purple-accent` | `#57458F` | `rgb(87, 69, 143)` | `oklch(0.40 0.11 285)` | CTA backgrounds, interactive |
| `--brand-blue-mist` | `#A0AED1` | `rgb(160, 174, 209)` | `oklch(0.74 0.06 260)` | Secondary accent, subtle bg |
| `--brand-blue-mist-alt` | `#9DAED4` | `rgb(157, 174, 212)` | `oklch(0.74 0.07 260)` | Gradient endpoints |

### Neutral Palette

| Token Name | Hex | RGB | oklch | Usage |
|---|---|---|---|---|
| `--neutral-black` | `#000000` | `rgb(0, 0, 0)` | `oklch(0 0 0)` | Body text default |
| `--neutral-dark` | `#1A1D1F` | `rgb(26, 29, 31)` | `oklch(0.18 0.005 250)` | Dark overlay bg (50% opacity) |
| `--neutral-charcoal` | `#444444` | `rgb(68, 68, 68)` | `oklch(0.37 0 0)` | Secondary text |
| `--neutral-gray` | `#545454` | `rgb(84, 84, 84)` | `oklch(0.43 0 0)` | Muted text |
| `--neutral-gray-mid` | `#666666` | `rgb(102, 102, 102)` | `oklch(0.49 0 0)` | Tertiary text, labels |
| `--neutral-gray-light` | `#A3A5A5` | `rgb(163, 165, 165)` | `oklch(0.70 0.003 200)` | Placeholder text |
| `--neutral-white` | `#FFFFFF` | `rgb(255, 255, 255)` | `oklch(1 0 0)` | Backgrounds, hero text |
| `--neutral-white-glass` | `rgba(255,255,255,0.95)` | — | `oklch(1 0 0 / 95%)` | Header bg (sticky state) |

### Semantic Colors

| Token Name | Hex | RGB | Usage |
|---|---|---|---|
| `--color-danger` | `#DF0000` | `rgb(223, 0, 0)` | Stock price down indicator |
| `--color-link` | `#0000EE` | `rgb(0, 0, 238)` | Default browser blue (unvisited links) |
| `--color-overlay-dark` | `rgba(0,0,0,0.5)` | — | Hero overlay |
| `--color-overlay-brand` | `rgba(26,29,31,0.5)` | — | Section overlays |
| `--color-accent-glow` | `rgba(34,184,240,0.26)` | — | Highlight accent bg |

### WordPress Preset Colors (from CSS custom properties)

These are WordPress defaults but present in the site's stylesheet:

| Variable | Value | Notes |
|---|---|---|
| `--wp--preset--color--black` | `#000000` | WP default |
| `--wp--preset--color--white` | `#ffffff` | WP default |
| `--wp--preset--color--vivid-purple` | `#9b51e0` | Close to brand purple |
| `--wp--preset--color--vivid-cyan-blue` | `#0693e3` | Accent blue |

---

## Typography

### Font Families (from getComputedStyle)

| Token | Value | Usage |
|---|---|---|
| `--font-primary` | `Arial` | Body text, nav, buttons, labels |
| `--font-secondary` | `"Open Sans", Arial, "Trebuchet MS", "Segoe UI", Helvetica, sans-serif` | Extended content |
| `--font-tertiary` | `"Trebuchet MS", Arial, sans-serif` | Specific UI elements |

### Type Scale (from getComputedStyle)

| Element | Font Size | Weight | Line Height | Letter Spacing | Text Transform |
|---|---|---|---|---|---|
| `h2` (hero) | `44px` | `600` | `40px` | `normal` | `uppercase` |
| `h3` | `32px` | `700` | `41.6px` | `normal` | `none` |
| `h4` | inherited | — | — | — | — |
| `body` | `16px` | `300` | `normal` | `normal` | — |
| `nav` | `16px` | `300` | `normal` | `normal` | — |
| `button` | `14px` | `700` | `21px` | `normal` | — |
| `link` | `16px` | `300` | `0px` (inline) | `normal` | — |

### WordPress Preset Font Sizes

| Size | Value |
|---|---|
| `--wp--preset--font-size--small` | `13px` |
| `--wp--preset--font-size--medium` | `20px` |
| `--wp--preset--font-size--large` | `36px` |
| `--wp--preset--font-size--x-large` | `42px` |

---

## Spacing

### WordPress Spacing Scale

| Variable | Value |
|---|---|
| `--wp--preset--spacing--20` | `0.44rem` (~7px) |
| `--wp--preset--spacing--30` | `0.67rem` (~11px) |
| `--wp--preset--spacing--40` | `1rem` (16px) |
| `--wp--preset--spacing--50` | `1.5rem` (24px) |
| `--wp--preset--spacing--60` | `2.25rem` (36px) |
| `--wp--preset--spacing--70` | `3.38rem` (~54px) |
| `--wp--preset--spacing--80` | `5.06rem` (~81px) |

### Observed Padding Patterns

| Element | Padding |
|---|---|
| Footer | `20px` |
| Link items | `5px 0px` |
| Card containers | ~`16px–24px` |
| Section containers | ~`40px–80px` vertical |

---

## Border Radius

| Value | Usage |
|---|---|
| `50px` | Pill buttons, tags, badges |
| `20px` | Large cards, hero containers |
| `6px` | Input fields, small cards |
| `5px` | Buttons, form elements |
| `3px` | Small badges, compact elements |
| `2px` | Subtle rounding, borders |

---

## Shadows / Elevation

| Token | Value | Usage |
|---|---|---|
| `--shadow-sm` | `rgba(0, 0, 0, 0.25) 0px 4px 4px 0px` | Card elevation |
| `--shadow-md` | `rgb(128, 128, 128) 0px 0px 5px 0px` | Glow/focused state |
| `--shadow-lg` | `rgba(0, 0, 0, 0.35) 1px 2px 8px 0px` | Dropdowns, elevated modals |

### WordPress Preset Shadows

| Name | Value |
|---|---|
| `natural` | `6px 6px 9px rgba(0, 0, 0, 0.2)` |
| `deep` | `12px 12px 50px rgba(0, 0, 0, 0.4)` |
| `sharp` | `6px 6px 0px rgba(0, 0, 0, 0.2)` |
| `outlined` | `6px 6px 0px -3px rgba(255, 255, 255, 1), 6px 6px rgba(0, 0, 0, 1)` |
| `crisp` | `6px 6px 0px rgba(0, 0, 0, 1)` |

---

## Aspect Ratios (from WordPress presets)

| Name | Value |
|---|---|
| `square` | `1` |
| `4:3` | `4/3` |
| `16:9` | `16/9` |
| `3:2` | `3/2` |
| `9:16` | `9/16` (mobile video) |

---

## Gradients (from WordPress presets)

| Name | Value |
|---|---|
| `vivid-cyan-to-purple` | `linear-gradient(135deg, rgba(6,147,227,1) 0%, rgb(155,81,224) 100%)` |
| `midnight` | `linear-gradient(135deg, rgb(2,3,129) 0%, rgb(40,116,252) 100%)` |
| `cool-to-warm` | `linear-gradient(135deg, rgb(74,234,220) 0%, rgb(151,120,209) 20%, rgb(207,42,186) 40%, rgb(238,44,130) 60%, rgb(251,105,98) 80%, rgb(254,248,76) 100%)` |

---

## KovelAI Adaptation Notes

### Colors → KovelAI Brand Mapping

| Unusual Machines Token | KovelAI Equivalent | Rationale |
|---|---|---|
| `--brand-deep-purple` (#291E44) | `--kovel-deep` | Keep — sophisticated, legal-grade |
| `--brand-purple` (#53478A) | `--kovel-primary` | Adjust slightly cooler for AI feel |
| `--brand-purple-accent` (#57458F) | `--kovel-accent` | Keep for CTAs |
| `--brand-blue-mist` (#A0AED1) | `--kovel-surface` | Keep — professional, calming |
| `--color-danger` (#DF0000) | `--kovel-danger` | Keep — standard error |
| White/Black neutrals | Keep as-is | Standard contrast ratios |

### Typography → KovelAI

- Replace `Arial` with `Inter` or `DM Sans` for modern AI aesthetic
- Keep the weight hierarchy (300 body, 600–700 headings)
- Maintain uppercase h2 hero treatment
- Add monospace variant (`JetBrains Mono`) for code/data displays

### Spacing → KovelAI

- Adopt the WP spacing scale values but normalize to 4px-base grid
- Increase section padding for more premium breathing room (60–100px vertical)
