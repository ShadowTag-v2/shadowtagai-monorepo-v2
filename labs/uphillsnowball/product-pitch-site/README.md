# ShadowTag AI — Product Pitch Site

> **Unusual Machines–inspired** product pitch page for ShadowTag AI's legal AI infrastructure.

## Stack

- **HTML5** — semantic, SEO-optimized, `<h1>` hierarchy
- **Vanilla CSS** — dark glassmorphism, cyan neon accents, responsive grid
- **Vanilla JS** — scroll-driven fade-in, particle system, counter animation, smooth scroll

## Local Dev

```bash
cd site/
python3 -m http.server 8889
# → http://localhost:8889
```

## Sections

| Section | Content |
|---------|---------|
| Hero | Privilege-Preserving AI tagline, STAI metrics card |
| Latest Developments | Date-stamped news items |
| Products | Oracle Studio, Judge #6, CounselConduit |
| Platform Architecture | 3-tier Google Cloud stack |
| Key Metrics | Counter-animated operational stats |
| Business Model | Dual-billing, pricing tiers |
| Contact | Early access request form |
| Footer | Heppner citation, nav links |

## Design System

- **Primary**: `#00e5ff` (cyan neon)
- **Background**: `#0a0a1a` → `#0d1117` gradient
- **Font**: Inter (Google Fonts)
- **Cards**: glassmorphism with `backdrop-filter: blur(20px)`
- **Animations**: scroll-driven IntersectionObserver

## Source Files

```
site/
├── index.html     # Full page structure
├── style.css      # Design system + responsive
└── main.js        # Animations + interactivity
clone.js           # Puppeteer scraper (Unusual Machines reference)
package.json       # Dependencies
```

## Deployment

```bash
# Preview channel
npx -y firebase-tools@latest hosting:channel:deploy pitch-site --project shadowtag-omega-v4

# Production (shadowtagai.web.app)
npx -y firebase-tools@latest deploy --only hosting --project shadowtag-omega-v4
```

## Legal

Protected under *United States v. Heppner* (S.D.N.Y., Feb. 10, 2026).
© 2026 ShadowTag AI. All rights reserved.
