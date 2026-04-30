# Unusual Machines (UMAC) — Design System Specification

> Generated via Design MCP at `design.googleapis.com/mcp`
> Source: Live scrape of https://www.unusualmachines.com/ (2026-04-24)

---

## Brand Identity

- **Company**: Unusual Machines, Inc.
- **Ticker**: NYSE American: UMAC
- **Tagline**: "HERE TO SERVE THE AMERICAN DRONE INDUSTRY."
- **Sector**: FPV Drones, Military/Commercial UAV Components
- **Brand**: Fat Shark (subsidiary)

---

## Color System (Material Design 3)

### Source Keys (from computed styles)
| Role       | Hex       | RGB                | Usage                      |
|------------|-----------|--------------------|-----------------------------|
| Primary    | `#291E44` | `rgb(41, 30, 68)`  | Header, CTA buttons, nav bg |
| Secondary  | `#5B4B93` | `rgb(91, 75, 147)` | Quick Links gradient, accents |
| Tertiary   | `#A9A2C0` | `rgb(169, 162, 192)` | Lavender gradient stops    |
| Background | `#FFFFFF` | `rgb(255, 255, 255)` | Page background           |

### Light Theme (Material Design 3 — Generated)
| Token                    | Hex       | Usage                           |
|--------------------------|-----------|----------------------------------|
| `primary`                | `#291E44` | Primary actions, key surfaces    |
| `on_primary`             | `#AA9CCA` | Text/icons on primary surfaces   |
| `primary_container`      | `#34294F` | Emphasis surfaces                |
| `on_primary_container`   | `#B6A8D7` | Text on emphasis surfaces        |
| `secondary`              | `#5B4B93` | Secondary actions                |
| `on_secondary`           | `#EEE6FF` | Text on secondary surfaces       |
| `secondary_container`    | `#6757A0` | Secondary emphasis surfaces      |
| `tertiary`               | `#615B76` | Tertiary color role              |
| `tertiary_container`     | `#A9A2C0` | Tertiary emphasis surfaces       |
| `surface`                | `#F9F9F9` | Page surfaces                    |
| `on_surface`             | `#313333` | Body text                        |
| `on_surface_variant`     | `#5E5F60` | Secondary text, labels           |
| `outline`                | `#797B7B` | Borders, dividers                |
| `outline_variant`        | `#B1B2B2` | Subtle borders                   |
| `error`                  | `#87504C` | Error states                     |

### Dark Theme (Material Design 3 — Generated)
| Token                    | Hex       | Usage                           |
|--------------------------|-----------|----------------------------------|
| `primary`                | `#9A8CBA` | Primary in dark mode             |
| `on_primary`             | `#170C32` | Text on primary dark             |
| `primary_container`      | `#291E44` | Same brand anchor                |
| `secondary`              | `#9988D5` | Secondary dark                   |
| `on_secondary`           | `#16004A` | Text on secondary dark           |
| `surface`                | `#120920` | Dark backgrounds                 |
| `surface_bright`         | `#312840` | Elevated dark surfaces           |
| `surface_container`      | `#1E152C` | Card backgrounds dark            |
| `on_surface`             | `#EFE0FF` | Body text dark                   |
| `on_surface_variant`     | `#B3A5C4` | Secondary text dark              |
| `outline`                | `#7C708D` | Dark borders                     |

---

## Typography

### Primary Font
- **Family**: Arial (system fallback detected via computed styles)
- **Likely intended**: A geometric sans-serif (e.g., Inter, Montserrat)
- **Body size**: 16px
- **H2 size**: 44px (hero heading)
- **H2 color**: `#FFFFFF` (white on dark backgrounds)

### Recommended Replacement (via Design MCP `describe_font`)
- **Primary**: Inter Variable (wght 100–900, opsz 14–32)
  - Body font optimized for screens
  - Tall x-height for mixed-case readability
  - Designed by Rasmus Andersson
- **Accent/Headings**: Roboto Variable (wght 100–900, wdth 75–100)
  - Dual nature: geometric skeleton + humanist curves
  - Superfamily with Slab and Mono variants

### Type Scale
| Element    | Size  | Weight | Line Height |
|------------|-------|--------|-------------|
| H1 (Hero)  | 64px  | 900    | 1.1         |
| H2         | 44px  | 700    | 1.2         |
| H3         | 32px  | 600    | 1.3         |
| Body       | 16px  | 400    | 1.5         |
| Caption    | 14px  | 400    | 1.4         |
| CTA Button | 16px  | 700    | 1.0         |

---

## Iconography (Material Symbols via Design MCP)

### Matched Icons
| Usage               | Material Symbol Name    |
|---------------------|------------------------|
| Drone/UAV           | `drone`                |
| Shopping/Cart       | `shopping_cart`        |
| Add to Cart         | `add_shopping_cart`    |
| Store               | `storefront`           |
| Payments            | `payments`             |
| Checkout            | `shopping_cart_checkout`|
| Mall/Products       | `local_mall`           |
| Charts/Stocks       | `bar_chart`            |
| Email               | `mail`                 |
| Phone/Contact       | `call`                 |

### Implementation
```html
<!-- Google Symbols Variable Font (Recommended) -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />

<span class="material-symbols-outlined">drone</span>
```

---

## Layout

### Grid
- **Max width**: ~1200px (content container)
- **Columns**: 12-column responsive grid
- **Gutter**: 24px
- **Margin**: 40px (desktop), 16px (mobile)

### Sections (Top to Bottom)
1. **Accessibility Bar** — Font size, contrast controls (dark bg)
2. **Navigation** — Logo + 7 menu items + CONTACT SALES CTA (dark purple `#291E44`)
3. **Hero** — Full-width image, drone imagery, stock ticker overlay
4. **Recent News** — Card list with arrows (white bg)
5. **Quick Links** — Purple gradient card with 4 icon links
6. **Upcoming Events** — Centered text section
7. **Contact** — Dark bg with drone imagery, investor info + email form
8. **Footer** — Dark bar, social icons (Facebook, Instagram, LinkedIn, X)

### Border Radius
- **Buttons**: 3px (sharp, corporate)
- **Cards**: 0px (sharp edges throughout)
- **Form inputs**: 0px

---

## Component Inventory

### Buttons
| Variant       | Background | Text Color | Border Radius | Padding        |
|--------------|------------|------------|---------------|----------------|
| Primary CTA  | `#291E44`  | `#FFFFFF`  | 3px           | 12px 24px      |
| Ghost/A11y   | transparent| `#FFFFFF`  | 0px           | 8px            |

### Cards
- News items: White bg, bottom border divider, arrow icon right
- Quick Links: Purple gradient card, white icon + text inside

### Forms
- Input fields: White bg, gray border, no radius
- Subscribe button: `#291E44` bg, white text, 3px radius

---

## Lighthouse Baseline (2026-04-24)
| Category        | Score |
|-----------------|-------|
| Accessibility   | 94    |
| Best Practices  | 100   |
| SEO             | 67    |

---

## Source Assets
- Full-page screenshot: `unusual_machines_fullpage.png`
- Design MCP schemas: `design_mcp_schemas.json`
- Material icons: `drone`, `shopping_cart`, `add_shopping_cart`, `storefront`
