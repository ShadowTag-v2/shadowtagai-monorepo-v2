# Component Spec: Quick Links

**Source Section:** `.homeQuickAccess` (index 5)
**Extracted from:** https://www.unusualmachines.com
**Target Component:** `src/components/QuickLinks.tsx`

---

## Extracted Styles (getComputedStyle)

```css
.homeQuickAccess {
  font-size: 16px;
  font-weight: 300;
  font-family: Arial;
  color: rgb(0, 0, 0);
  background-color: rgba(26, 29, 31, 0.5); /* dark overlay */
  background-image: url("img-Quick-Links.png");
  background-repeat: no-repeat;
  background-attachment: fixed; /* parallax effect */
  background-position: 50% 50%;
  background-size: cover;
  padding: 55px 0;
  position: relative;
  z-index: 1;
  width: 100%;
  height: 449px;
}
```

## Structure

```
section.homeQuickAccess
  └── div.container
       └── (quick link items, horizontally laid out)
            ├── a → img (45×72, "icon-charts.png") + "Quotes and Charts"
            ├── a → img (45×53, "Group-40.png") + "Investor Presentation"
            ├── a → img (60×60, "feather_mail-1.png") + "Email Alerts"
            └── a → img (52×52, "Vector-33.png") + "IR Contact"
```

## Link Items (Extracted)

| Text | Icon Size | Link Width | Link Target |
|------|-----------|-----------|-------------|
| Quotes and Charts | 45×72 | 187px | /stock/ |
| Investor Presentation | 45×53 | 214px | /about-us/company-presentation/ |
| Email Alerts | 60×60 | 120px | /email-alerts/ |
| IR Contact | 52×52 | 105px | /contact-ir/ |

## Visual Pattern

- **Dark section** with background image + semi-transparent overlay
- **Parallax** (`background-attachment: fixed`) on desktop
- 4 icon-label pairs arranged horizontally
- Each item: icon above, text below, full-block link (108px tall)
- Links are unstyled (default blue `rgb(0, 0, 238)` — clearly custom CSS override needed)

## KovelAI Adaptation Notes

- Replace with KovelAI product/feature quick links
- Suggested items: "Oracle Studio", "Research Hub", "Pricing", "Book Demo"
- Keep the dark overlay + background image parallax pattern
- Use our own background image (from Veo/generated assets)
- Replace icons with Lucide icons (via shadcn/ui)
- Add hover animation: scale + glow
