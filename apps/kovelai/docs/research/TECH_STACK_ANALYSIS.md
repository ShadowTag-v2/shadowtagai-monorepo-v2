# Tech Stack Analysis — KovelAI

> Extracted from [unusualmachines.com](https://www.unusualmachines.com/) via Chrome DevTools MCP.
> Format follows [ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template) INSPECTION_GUIDE.md Phase 5.

---

## Source Site Stack

| Category | Technology | Evidence |
|---|---|---|
| **CMS** | WordPress | CSS custom properties `--wp--preset--*`, WP block patterns |
| **Hosting** | MZ Group CDN | Asset URLs: `cdn-sites-assets.mziq.com` |
| **Theme** | `mziq_unusual_machines` (custom) | Footer CSS references to theme path |
| **CSS Framework** | None | No Tailwind, Bootstrap, or other framework classes detected |
| **JS Framework** | None (vanilla + jQuery presumed) | No React, Vue, Angular indicators |
| **Font Loading** | System fonts (self-hosted) | No Google Fonts `<link>` tags detected |
| **Analytics** | Not extracted | Likely Google Analytics or similar |
| **Form Handling** | Server-side PHP (WordPress) | Traditional form POST, reCAPTCHA integration |
| **Anti-spam** | Google reCAPTCHA v3 | IframePresentational "reCAPTCHA" in DOM |
| **Cookie Consent** | Custom or CookieBot-style | Alert overlay with category-based opt-in |
| **CDN** | MZ Group CDN | All assets served from `cdn-sites-assets.mziq.com` |
| **SSL** | Standard Let's Encrypt / CloudFlare | HTTPS active |

---

## Asset Inventory

### Images Detected (from DOM)

| Asset | URL | Usage |
|---|---|---|
| Logo | `cdn-sites-assets.mziq.com/.../logo.png` | Header logo |
| Charts icon | `cdn-sites-assets.mziq.com/.../icon-charts.png` | Quick Links |
| Presentation icon | `cdn-sites-assets.mziq.com/.../Group-40.png` | Quick Links |
| Mail icon | `cdn-sites-assets.mziq.com/.../feather_mail-1.png` | Quick Links |
| Contact icon | `cdn-sites-assets.mziq.com/.../Vector-33.png` | Quick Links |
| Facebook icon | `cdn-sites-assets.mziq.com/.../icon-facebook.png` | Footer social |
| Instagram icon | `cdn-sites-assets.mziq.com/.../icon-instagram.png` | Footer social |
| LinkedIn icon | `cdn-sites-assets.mziq.com/.../icon-linkedin.png` | Footer social |
| Twitter icon | `cdn-sites-assets.mziq.com/.../icon-twitter.png` | Footer social |

### Videos
- None detected

### SVGs
- 0 inline SVGs detected (all icons are raster PNGs hosted on CDN)

### Fonts (loaded)
- `Arial` (system font, no download needed)
- `"Open Sans"` (system stack fallback, no explicit loading)
- `"Trebuchet MS"` (system font)

---

## KovelAI Target Stack

| Category | Technology | Rationale |
|---|---|---|
| **Framework** | Next.js 15 (App Router) | SSR + ISR for SEO, React Server Components |
| **Styling** | Tailwind CSS v4 + CSS Modules | Rapid development, design token integration |
| **UI Components** | shadcn/ui + Radix Primitives | Accessible, unstyled, composable |
| **Fonts** | Inter (headings/body) + JetBrains Mono (code) | Modern, Google Fonts, variable weights |
| **Icons** | Lucide React | Consistent style, tree-shakeable |
| **Animations** | CSS transitions + IntersectionObserver | No heavy animation library needed |
| **Forms** | React Hook Form + Zod validation | Type-safe, performant form handling |
| **Anti-spam** | Cloudflare Turnstile | Privacy-respecting alternative to reCAPTCHA |
| **Analytics** | Google Analytics 4 (via gtag) or Plausible | Privacy-first option available |
| **Cookie Consent** | Custom React component | GDPR/CCPA compliant, matches brand |
| **CMS** | None (static) or Contentlayer | Content in MDX files for blog posts |
| **Hosting** | Firebase Hosting | Existing infra, kovelai.web.app |
| **CDN** | Firebase Hosting CDN | Automatic with Firebase |
| **SSL** | Firebase managed | Automatic HTTPS |
| **Image Optimization** | Next.js `<Image>` + sharp | WebP/AVIF auto-conversion |
| **Email** | Resend or Firebase Extensions | Transactional email for alerts |

---

## Dependency Versions (Recommended)

```json
{
  "next": "^15.3.0",
  "react": "^19.0.0",
  "react-dom": "^19.0.0",
  "tailwindcss": "^4.0.0",
  "@tailwindcss/vite": "^4.0.0",
  "lucide-react": "^0.500.0",
  "class-variance-authority": "^0.7.0",
  "clsx": "^2.1.0",
  "tailwind-merge": "^3.0.0",
  "react-hook-form": "^7.55.0",
  "zod": "^3.25.0",
  "@hookform/resolvers": "^5.0.0"
}
```

---

## Code Quality Tools

| Tool | Purpose | Config |
|---|---|---|
| `biome` | Lint + format (TS/JS) | `biome.json` |
| `typescript` | Type checking | `tsconfig.json` strict mode |
| `lighthouse` | Performance/a11y auditing | Chrome DevTools MCP |
| `next lint` | Next.js-specific rules | `.eslintrc.json` (if biome insufficient) |

---

## Migration Notes (UMAC → KovelAI)

| UMAC Feature | KovelAI Equivalent | Effort |
|---|---|---|
| WordPress CMS | Next.js Static / MDX | High (ground-up) |
| PHP form handling | API Routes + Firebase Functions | Medium |
| MZ Group CDN assets | `public/` + Next.js Image | Low |
| reCAPTCHA v3 | Cloudflare Turnstile | Low |
| jQuery interactions | React hooks + CSS | Medium |
| System fonts (Arial) | Google Fonts (Inter) | Low |
| WordPress block editor | React components | N/A (different paradigm) |
| Server-side stock ticker | Client-side API call or SSR | Medium |
