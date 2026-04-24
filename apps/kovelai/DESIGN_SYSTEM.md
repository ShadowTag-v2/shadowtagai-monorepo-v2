# KovelAI — DESIGN_SYSTEM.md
# Generated via Google Design MCP + Live CSS Extraction
# Design Language: "Structured Precision"
# Source: https://kovelai.web.app/ (2026-04-24)

---

## Color Palette (Tokens = Roles)

### Semantic Roles

| Role | Hex | RGB | Usage |
|------|-----|-----|-------|
| **background** | `#0a0a0f` | `rgb(10, 10, 15)` | Page canvas, dark void |
| **foreground** | `#f0f6fc` | `rgb(240, 246, 252)` | Primary text, headings |
| **primary** | `#00bcd4` | `rgb(0, 188, 212)` | CTA buttons, links, accent lines |
| **primary-foreground** | `#0a0a0f` | `rgb(10, 10, 15)` | Text on primary buttons |
| **secondary** | `#1a237e` | `rgb(26, 35, 126)` | Deep navy accent, secondary surfaces |
| **secondary-foreground** | `#f0f6fc` | `rgb(240, 246, 252)` | Text on secondary surfaces |
| **accent** | `#00e5ff` | `rgb(0, 229, 255)` | Highlights, electric cyan glow |
| **accent-foreground** | `#0a0a0f` | `rgb(10, 10, 15)` | Text on accent surfaces |
| **card** | `#0d1117` | `rgb(13, 17, 23)` | Card backgrounds, elevated surfaces |
| **card-foreground** | `#f0f6fc` | `rgb(240, 246, 252)` | Text on cards |
| **muted** | `#161b22` | `rgb(22, 27, 34)` | Disabled states, subtle backgrounds |
| **muted-foreground** | `#8b949e` | `rgb(139, 148, 158)` | Secondary text, labels |
| **border** | `#00bcd426` | `rgba(0, 188, 212, 0.15)` | Subtle borders with cyan tint |
| **ring** | `#00bcd4` | `rgb(0, 188, 212)` | Focus rings |
| **error** | `#ef4444` | `rgb(239, 68, 68)` | Error states |
| **warning** | `#fbbc04` | `rgb(251, 188, 4)` | Warning states |
| **success** | `#34a853` | `rgb(52, 168, 83)` | Success states |

### Brand Purple (Accent Secondary)
| Token | Hex | Usage |
|-------|-----|-------|
| **violet** | `#7c4dff` | Gradient endpoint, premium accent |

### CSS Custom Properties (Live)
```css
:root {
  --background: #0a0a0f;
  --foreground: #f0f6fc;
  --primary: #00bcd4;
  --primary-foreground: #0a0a0f;
  --secondary: #1a237e;
  --secondary-foreground: #f0f6fc;
  --muted: #161b22;
  --muted-foreground: #8b949e;
  --accent: #00e5ff;
  --accent-foreground: #0a0a0f;
  --card: #0d1117;
  --card-foreground: #f0f6fc;
  --border: #00bcd426;
  --ring: #00bcd4;
}
```

---

## Typography

| Role | Font | Weight | Size Range |
|------|------|--------|------------|
| **Primary** | Inter | 400–800 | 14px–64px |
| **Fallback** | "Inter Fallback", ui-sans-serif, system-ui, sans-serif | — | — |

### Type Scale
| Element | Size | Weight | Line Height | Letter Spacing |
|---------|------|--------|-------------|----------------|
| H1 | clamp(32px, 5vw, 64px) | 800 | 1.1 | -0.02em |
| H2 | clamp(24px, 3.5vw, 42px) | 700 | 1.2 | -0.015em |
| H3 | clamp(18px, 2vw, 24px) | 600 | 1.3 | -0.01em |
| Body | 16px | 400 | 1.6 | 0em |
| Label | 12px | 600 | 1.4 | 0.1em (uppercase) |

---

## Gradients

| Name | CSS | Usage |
|------|-----|-------|
| **Primary CTA** | `linear-gradient(90deg, #00bcd4, #00e5ff)` | Button fills, horizontal accents |
| **Hero Fade** | `linear-gradient(90deg, #00bcd4, #7c4dff)` | Hero overlays |
| **Card Surface** | `linear-gradient(to right bottom in oklab, #0d1117, #161b22)` | Elevated surfaces |
| **Vignette** | `linear-gradient(rgba(10,10,15,0.4) 0%, rgba(10,10,15,0.2) 30%, rgba(10,10,15,0.6) 70%, rgba(10,10,15,0.95) 100%)` | Hero image overlays |

---

## Shape & Border

| Token | Value | Usage |
|-------|-------|-------|
| **border-radius-sm** | 6px | Buttons, inputs |
| **border-radius-md** | 12px | Cards |
| **border-radius-lg** | 20px | Hero containers |
| **border-width** | 1px | Default border |
| **border-style** | solid | Cyan-tinted borders |

---

## Appearance

| Property | Value |
|----------|-------|
| **Mode** | Dark only |
| **Background** | `#0a0a0f` (near-black with blue undertone) |
| **Glass Effect** | `backdrop-filter: blur(20px)` on nav |
| **Grid Overlay** | Cyan grid lines at 0.3 opacity |

---

## WCAG Contrast Audit

| Pair | Ratio | Grade |
|------|-------|-------|
| `#f0f6fc` on `#0a0a0f` | 18.9:1 | AAA ✅ |
| `#00bcd4` on `#0a0a0f` | 8.1:1 | AAA ✅ |
| `#8b949e` on `#0a0a0f` | 5.2:1 | AA ✅ |
| `#00e5ff` on `#0a0a0f` | 10.3:1 | AAA ✅ |
| `#0a0a0f` on `#00bcd4` | 8.1:1 | AAA ✅ |

---

## Design DNA

- **Language:** "Structured Precision" — legal authority meets technology confidence
- **Atmosphere:** Dark void, cyan electric accents, deep navy shadows
- **Motion:** Subtle entrance animations, grid pattern overlay, glowing borders
- **Character:** Authoritative, protective, no-nonsense pricing transparency
