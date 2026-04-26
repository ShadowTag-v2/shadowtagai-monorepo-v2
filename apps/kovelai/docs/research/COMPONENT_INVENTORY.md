# Component Inventory — KovelAI

> Extracted from [unusualmachines.com](https://www.unusualmachines.com/) via Chrome DevTools MCP DOM snapshot.
> Adapted for KovelAI site architecture.
> Format follows [ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template) INSPECTION_GUIDE.md Phase 5.

---

## 1. StickyHeader

- **DOM:** `banner` → `link (logo)` + `button (A-, A+, Contrast)` + `link (Accessibility, CTA)` + `nav`
- **Variants:** Default (transparent over hero), Scrolled (white glass bg `rgba(255,255,255,0.95)`)
- **States:** Default, Scrolled (gains bg + shadow)
- **Responsive:** Desktop = full nav. Mobile = hamburger (not visible but implied by responsive CSS)
- **Interactions:** Scroll-triggered background change. Hover on nav items.
- **Animations:** Background transition on scroll

### Sub-components:
- `Logo` — Image link to homepage
- `AccessibilityBar` — Font size controls (A-, A+, Contrast button)
- `ContactSalesCTA` — Purple pill button `border-radius: 50px`
- `MainNav` — Products, Media & Events, Investors, Contact, Careers, About Us

### KovelAI Adaptation:
- Replace accessibility bar with AI-specific controls (e.g., language selector, dark mode toggle)
- Nav items: Products, Use Cases, Pricing, Docs, About, Blog
- Keep CTA pill style with `--kovel-accent` background

---

## 2. HeroSection

- **DOM:** Full-width dark section with background image + overlay
- **Structure:** Background image/video → dark overlay `rgba(0,0,0,0.5)` or `rgba(26,29,31,0.5)` → content
- **Content:**
  - H2: "HERE TO SERVE THE AMERICAN DRONE INDUSTRY." (uppercase, 44px, weight 600, white)
  - Live stock ticker: NYSE: UMAC, $14.65, ▼-$1.48
  - Volume: 4,865,874
  - Date/time stamp
- **Variants:** N/A (single state)
- **States:** Static
- **Responsive:** Full-width at all breakpoints, text scales down
- **Interactions:** Stock ticker potentially auto-refreshes (server-side)

### KovelAI Adaptation:
- Replace stock ticker with AI metrics dashboard (model accuracy, cases processed, uptime)
- Tagline: "AI-Powered Legal Intelligence" or similar
- Background: abstract mesh gradient or particle animation instead of static image
- Keep the uppercase H2 hero treatment

---

## 3. RecentNewsSection

- **DOM:** H2 "Recent News" → 3x clickable buttons (news items) + "See all" link
- **Structure:**
  - Section heading (H2, white text on dark bg)
  - 3 news item buttons (full text as button content, styled as cards)
  - "See all" link → press releases page
- **Content (verbatim):**
  1. "Unusual Machines Secures $5M+ Order from Powerus for Counter-UAS Systems"
  2. "Unusual Machines Appoints Chadd Cole as Vice President of FP&A"
  3. "Unusual Machines Accelerates Motor Factory Output at Orlando Campus"
- **Variants:** Default (3 items visible)
- **States:** Hover (cursor pointer, likely bg or shadow change)
- **Responsive:** Likely stacks vertically on mobile
- **Interactions:** Click → opens news article

### KovelAI Adaptation:
- "Latest Updates" or "News & Insights"
- Replace with blog/announcement cards with image thumbnails
- Add date badges and category tags

---

## 4. QuickLinksGrid

- **DOM:** H2 "Quick Links" → 4x link cards in grid
- **Structure:** Each card = image icon + text label
- **Content:**
  1. "Quotes and Charts" (icon: charts.png)
  2. "Investor Presentation" (icon: Group-40.png)
  3. "Email Alerts" (icon: mail.png)
  4. "IR Contact" (icon: Vector-33.png)
- **Variants:** N/A
- **States:** Hover (likely scale or shadow increase)
- **Responsive:** 4-column → 2-column → 1-column stack
- **Interactions:** Click → navigates to sub-page

### KovelAI Adaptation:
- Replace investor links with product links: "Documentation", "API Reference", "Case Studies", "Support"
- Keep the icon + label card pattern
- Use Lucide icons instead of downloaded PNGs

---

## 5. UpcomingEventsSection

- **DOM:** H2 "Upcoming Events" → Empty state: "No upcoming events!" → "See all" link
- **Structure:** Section heading + empty state message + link
- **Variants:** Empty state (current), Events loaded (for future)
- **States:** Default
- **Responsive:** Simple text layout, no responsive break needed

### KovelAI Adaptation:
- "Upcoming Webinars" or "Events"
- Empty state with illustration/CTA to register
- When populated: card list with date, title, register CTA

---

## 6. ContactSection

- **DOM:** H2 "Contact" → 2 sub-sections
- **Sub-sections:**
  - **InvestorContact** (H3): Name, email, phone, company
  - **MediaInquiries** (H3): Email, phone
- **Structure:** Two-column layout (side by side on desktop)
- **Content (verbatim):**
  - Email: investors@unusualmachines.com
  - Christine Petraglia, CS Investor Relations
  - IR & Market Strategies
  - T: 917-633-8980
  - Media: media@unusualmachines.com / 917-771-7693
- **Variants:** N/A
- **States:** Static
- **Responsive:** 2-col → stacked

### KovelAI Adaptation:
- "Get in Touch" with Sales and Support columns
- Replace investor contacts with sales team / support channels
- Add contact form embedded

---

## 7. EmailAlertsSection

- **DOM:** H2 "Email Alerts" → Form with 4 text inputs + checkbox + submit button
- **Structure:**
  - Required text field (email)
  - 3 optional text fields (name, company, etc.)
  - Checkbox "Press Releases"
  - "Reload form" button (captcha/anti-spam)
- **Variants:** N/A
- **States:** Default, Validation error, Success
- **Interactions:** Form submission with reCAPTCHA
- **Responsive:** Full-width stacked inputs

### KovelAI Adaptation:
- "Stay Updated" newsletter signup
- Simplify to: email + name + checkbox for "Product Updates" and "Blog Posts"
- Use modern floating labels pattern

---

## 8. Footer

- **DOM:** `contentinfo` → Copyright + social links (4) + powered by
- **Structure:**
  - Copyright: "Unusual Machines - All Rights Reserved"
  - Social icons: Facebook, Instagram, LinkedIn, Twitter (as image links)
  - "Powered by MZ" attribution link
- **Background:** `rgb(41, 30, 68)` — deep purple
- **Text color:** White
- **Padding:** `20px`
- **Variants:** N/A
- **States:** Hover on social icons and links
- **Responsive:** Simple — no layout break needed

### KovelAI Adaptation:
- Multi-column footer: Product, Resources, Company, Legal
- Social links using Lucide icons
- Remove "Powered by" — replace with ShadowTagAI subsidiary note
- Keep deep purple background

---

## 9. CookieConsentBanner

- **DOM:** Overlay alert with `live="assertive"`
- **Structure:**
  - Close button
  - Title: "This website uses cookies"
  - Description text with privacy policy link
  - 4 category checkboxes: Strictly Necessary (disabled), Performance, Targeting, Functionality
  - 3 action buttons: Show Details, Accept All, Decline All
- **Variants:** N/A
- **States:** Open (default), Closed (after user action)
- **Interactions:** Click Accept All / Decline All / individual toggles
- **Responsive:** Full-width bottom/overlay

### KovelAI Adaptation:
- Keep same pattern — required for GDPR/CCPA
- Restyle to match kovelai brand
- Simplify to Accept/Decline with link to full policy

---

## Component Count Summary

| # | Component | Complexity | Sub-components |
|---|---|---|---|
| 1 | StickyHeader | High | Logo, AccessibilityBar, NavMenu, CTA |
| 2 | HeroSection | Medium | StockTicker, HeroText |
| 3 | RecentNewsSection | Medium | NewsCard (×3) |
| 4 | QuickLinksGrid | Low | LinkCard (×4) |
| 5 | UpcomingEventsSection | Low | EmptyState |
| 6 | ContactSection | Medium | ContactCard (×2) |
| 7 | EmailAlertsSection | Medium | AlertForm |
| 8 | Footer | Low | SocialLinks |
| 9 | CookieConsentBanner | Medium | ConsentToggles |

**Total: 9 sections, ~20 sub-components**
