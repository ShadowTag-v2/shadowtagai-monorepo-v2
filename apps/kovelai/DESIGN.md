# DESIGN.md — KovelAI (kovelai.web.app)

> MCP-validated design system extracted via Chrome DevTools MCP on 2026-04-22.
> Source: https://kovelai.web.app

## Identity

- **Product**: KovelAI — "The Shopify for Legal AI"
- **Tagline**: "Privilege-Protected AI For Every Client Query"
- **Brand Position**: Post-Heppner privileged AI routing for law firms

## Color Palette

### Primary
| Token | Value | Usage |
|-------|-------|-------|
| `--bg-primary` | `rgb(10, 10, 15)` | Page background (near-black) |
| `--text-primary` | `rgb(255, 255, 255)` | Primary text |
| `--text-secondary` | `rgb(139, 148, 158)` | Body copy, descriptions |
| `--text-tertiary` | `rgb(201, 209, 217)` | Elevated secondary text |
| `--accent-cyan` | `rgb(0, 188, 212)` | Primary CTA, links, highlights |

### Semantic
| Token | Value | Usage |
|-------|-------|-------|
| `--google-blue` | `rgb(66, 133, 244)` | Gemini/Google branding |
| `--warm-amber` | `rgb(216, 158, 108)` | Claude/Anthropic branding |
| `--teal-green` | `rgb(16, 163, 127)` | Success states, verification |
| `--coral-red` | `rgb(231, 76, 60)` | Error, danger, privilege warning |
| `--google-green` | `rgb(52, 168, 83)` | Validation, checkmarks |
| `--google-yellow` | `rgb(251, 188, 4)` | Caution, pending states |
| `--deep-purple` | `rgb(124, 77, 255)` | Premium tier, enterprise |

### Surface
| Token | Value | Usage |
|-------|-------|-------|
| `--surface-overlay` | `rgba(10, 10, 15, 0.8)` | Nav overlay, modals |
| `--surface-card` | `rgba(13, 17, 23, 0.7)` | Card backgrounds |
| `--surface-accent-10` | `rgba(0, 188, 212, 0.1)` | Accent tint backgrounds |

## Typography

| Role | Font | Weight | Usage |
|------|------|--------|-------|
| Display | Inter | 700-900 | H1, hero headlines |
| Body | Inter | 400-500 | Paragraphs, descriptions |
| Code | JetBrains Mono | 400 | Legal citations, hashes |
| Fallback | Times | 400 | Serif fallback |

## Component Inventory

### Navigation
- Sticky glassmorphic navbar with `rgba(10,10,15,0.8)` backdrop
- Logo: "K" mark + "KovelAI" wordmark
- Links: Platform, For Law Firms, Pricing, Post-Heppner, Investors
- CTA: "Start Free Trial" (cyan accent)

### Hero
- Two-line H1 with line break
- Subheadline with meta description copy
- Dual CTA buttons

### Sections
1. **Platform** — Feature grid with icon cards
2. **How It Works** — 4-step process (Sign In → Choose Model → Get Paid → Privilege)
3. **Six Tools** — Tool showcase grid
4. **Pricing** — 3-tier cards (Solo/Practice/Enterprise)
5. **Early Access** — Lead capture form
6. **Post-Heppner** — Legal explainer section

### Design Patterns
- Dark mode only (no light mode)
- Glassmorphism on cards and nav
- Cyan accent as primary interactive color
- Model-specific brand colors (blue=Gemini, amber=Claude, green=ChatGPT, red=warning)
- Cards use `rgba(13,17,23,0.7)` with subtle borders
- Accent backgrounds at 10-12.5% opacity for pill/badge shapes

## Lighthouse Scores (2026-04-22)

| Category | Score |
|----------|-------|
| Accessibility | 94 |
| Best Practices | 100 |
| SEO | 100 |
