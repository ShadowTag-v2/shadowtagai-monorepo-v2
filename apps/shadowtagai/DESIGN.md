# DESIGN.md — ShadowTagAI (shadowtagai.web.app)

> MCP-validated design system extracted via Chrome DevTools MCP on 2026-04-22.
> Source: https://shadowtagai.web.app

## Identity

- **Product**: ShadowTagAI — "Sovereign AI Infrastructure"
- **Tagline**: "Autonomous Intelligence for Total Data Sovereignty"
- **Brand Position**: Enterprise-grade on-premise AI for institutions

## Color Palette

### Primary
| Token | Value | Usage |
|-------|-------|-------|
| `--bg-primary` | `rgb(9, 9, 11)` | Page background (zinc-950) |
| `--text-primary` | `rgb(238, 238, 240)` | Primary text (zinc-100) |
| `--text-secondary` | `rgb(139, 139, 158)` | Body copy, descriptions (zinc-500) |
| `--text-muted` | `rgb(95, 95, 114)` | Tertiary, deemphasized (zinc-600) |

### Accent
| Token | Value | Usage |
|-------|-------|-------|
| `--accent-violet` | `rgb(124, 58, 237)` | Primary brand, CTAs (violet-600) |
| `--accent-emerald` | `rgb(13, 242, 116)` | Status indicators, success |
| `--accent-violet-12` | `rgba(124, 58, 237, 0.12)` | Tinted backgrounds |

### Surface
| Token | Value | Usage |
|-------|-------|-------|
| `--surface-elevated` | `rgb(15, 15, 20)` | Section backgrounds |
| `--surface-card` | `rgb(22, 22, 29)` | Card backgrounds |
| `--surface-matte` | `rgb(12, 12, 18)` | Footer, deeper surfaces |
| `--surface-overlay` | `rgba(9, 9, 11, 0.8)` | Nav overlay |
| `--surface-card-translucent` | `rgba(22, 22, 29, 0.95)` | Cards with backdrop |
| `--surface-card-glass` | `rgba(22, 22, 29, 0.7)` | Glassmorphic cards |
| `--overlay-dark` | `rgba(0, 0, 0, 0.7)` | Modal/video overlays |

## Typography

| Role | Font | Weight | Usage |
|------|------|--------|-------|
| Display | Inter | 700-800 | H1, H2 headlines |
| Body | Inter | 400-500 | Paragraphs, descriptions |
| Fallback System | Arial | 400 | Sans-serif fallback |
| Fallback Serif | Times | 400 | Serif fallback |

## Component Inventory

### Navigation
- Sticky with `rgba(9,9,11,0.8)` backdrop-blur
- Minimal: logo + primary nav links
- Mobile hamburger

### Hero
- Two-line H1 with line break
- Sovereignty tagline
- Dual CTA: primary (violet), secondary (outline)

### Sections
1. **Value Props** — "Your data. Your hardware. Your intelligence."
   - 3 cards: Zero Cloud Dependency, Institutional-Grade Intelligence, Compliance by Architecture
2. **Platform** — UphillSnowball technical showcase
   - 3 cards: Zero-Trust Architecture, Sovereign Inference, Autonomous Operations
3. **Enterprise Intelligence** — Capability showcase
   - Document Intelligence, Autonomous Research, Risk Assessment
4. **Contact** — Contact form section

### Design Patterns
- Dark mode only (zinc-950 foundation)
- Violet as brand accent (distinct from KovelAI's cyan)
- Emerald green as status/online indicator
- Cards use `rgb(22,22,29)` with 1px border at ~10% white
- Glassmorphism with `backdrop-filter: blur()`
- Consistent `border-radius: 12-16px` on cards
- No shadows — relies on surface elevation hierarchy

## Lighthouse Scores (2026-04-22)

| Category | Score |
|----------|-------|
| Accessibility | 95 |
| Best Practices | 100 |
| SEO | 100 |
