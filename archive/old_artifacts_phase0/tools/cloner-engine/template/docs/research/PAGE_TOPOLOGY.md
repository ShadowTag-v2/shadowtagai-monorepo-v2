# Unusual Machines — Page Topology

**Source:** https://www.unusualmachines.com/
**Extracted:** 2026-04-25 via Chrome DevTools MCP
**Page Height:** 2864px @ 1440px viewport

## Section Map (Top → Bottom)

| # | Section | Class | Y-Start | Height | Layout | BG | Interaction |
|---|---------|-------|---------|--------|--------|-----|-------------|
| 1 | Header (fixed) | `.header` | 0 | 95px | fixed, z-9 | transparent | Sticky nav |
| 2 | Hero Banner | `.homeBanner` | 0 | 648px | flex center, relative | BG image (USA flag drone), `cover` | Zoom-in animation |
| 3 | Recent News / Highlights | `.homeHighlights` | 648 | 605px | block, container maxW-1170 | white `#fff` | Click-driven news accordion |
| 4 | Quick Links | `.homeQuickAccess` | 1253 | 449px | block, container maxW-1170 | BG image overlay `rgba(26,29,31,0.5)` | Static icon grid |
| 5 | Upcoming Events | `.homeEvents` | 1702 | 346px | block, container maxW-1170 | white `#fff` | Static |
| 6 | Contact | `.homeContact` | 2048 | 756px | block, container maxW-1170 | BG image overlay `rgba(0,0,0,0.5)` | Email form |
| 7 | Footer | `.footer` | 2804 | 60px | block, pad-20 | deep purple `rgb(41,30,68)` | Social links |

## Global Design Tokens

### Colors
| Role | Value |
|------|-------|
| Header BG (scrolled) | `rgba(255,255,255,0.95)` |
| Body BG | `rgb(255,255,255)` |
| Deep Purple (footer/brand) | `rgb(41,30,68)` / `#291E44` |
| Accent Purple | `rgb(83,71,138)` / `#53478A` |
| Muted Blue | `rgb(160,174,209)` / `#A0AED1` |
| Dark overlay | `rgba(26,29,31,0.5)` |
| Text primary | `rgb(33,29,50)` / `#211D32` |
| Text white | `rgb(255,255,255)` |

### Typography
- **Font family:** Arial (system font — no Google Fonts loaded)
- **Hero heading:** 44px, weight 600, uppercase, line-height 40px, white
- **Section titles:** sectionTitle class
- **Body:** 16px, weight 300

### Layout
- **Container:** `max-width: 1170px`, `margin: 0 auto`, `padding: 0 15px`
- **Sections:** Full-width with 55px vertical padding
- **Hero:** 600px min-height, flex center, overflow hidden

### Assets
| Asset | URL |
|-------|-----|
| Logo | `cdn-sites-assets.mziq.com/.../logo.png` (166x41) |
| Hero BG | `cdn-sites-assets.mziq.com/.../USA_FC-1-1-1.jpg` |
| Quick Links BG | `cdn-sites-assets.mziq.com/.../img-Quick-Links.png` |
| Contact BG | `cdn-sites-assets.mziq.com/.../USA_FC-6-1-1.jpg` |
| Charts icon | 45x72 |
| Investor Pres icon | 45x53 |
| Email icon | 60x60 |
| IR Contact icon | 52x52 |
| Social: FB, IG, LinkedIn, Twitter | 18-20px icons |

### Structural Pattern
7-section vertical scroll layout:
1. **Fixed header** (transparent → white on scroll)
2. **Full-bleed hero** with background image + text overlay
3. **Alternating sections**: white BG ↔ image BG with dark overlay
4. **Container-constrained content** (1170px max)
5. **Deep purple footer** (brand color)

This is a classic investor relations / corporate site structure.
The layout pattern maps directly to the Cinematic Legal-Tech chassis:
- Hero BG image → `<video>` with atmospheric glass
- Alternating sections → dark/darker section bands
- Container constraint → maintained at 1170px
- Purple brand → replaced with legal-tech neutrals
