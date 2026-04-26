# Page Topology — unusualmachines.com

## Section Map (top to bottom)

| # | Section | Height | Top | Class | Interaction |
|---|---------|--------|-----|-------|-------------|
| 0 | Header | 95px | 0 | `.header` (fixed/sticky) | Nav links, dropdown menus |
| 1 | Hero Banner | 648px | 0 | `.homeBanner` | zoom-in animation on load |
| 2 | Highlights (News + Stock) | 605px | 648 | `.homeHighlights` | Click news items to expand |
| 3 | Quick Links | 449px | 1253 | `.homeQuickAccess` | Hover cards, bg image |
| 4 | Events | 346px | 1702 | `.homeEvents` | Static list |
| 5 | Contact | 756px | 2048 | `.homeContact` | Form inputs, bg image |
| 6 | Footer | 60px | 2804 | `.footer` | Social links |

## Visual Stack

- Header overlays hero banner (position: absolute/fixed)
- Hero has background image with text overlay
- Quick Links has full background image (drone aerial shot)
- Contact has background image (drone operator)
- Cookie consent dialog overlays entire page

## Background Images

1. Hero: `USA_FC-1-1-1.jpg` (American flag/drone imagery)
2. Quick Links: `img-Quick-Links.png`
3. Contact: `USA_FC-6-1-1.jpg`

## Typography

- Primary fontFamily: Times (serif) — used across page
- Secondary: Arial (sans-serif) — headings may use Arial

## Color Tokens (from CSS custom properties)

- WordPress preset colors (standard WP palette)
- Primary site color appears to be dark/military theme
- Background: white sections alternating with image-backed sections

## Key Assets

- Logo: `logo.png` (166x41)
- Social icons: Facebook, Instagram, LinkedIn, Twitter
- Quick link icons: Charts, Presentation, Email, IR Contact
- Favicons: 6 sizes from 16x16 to 180x180
