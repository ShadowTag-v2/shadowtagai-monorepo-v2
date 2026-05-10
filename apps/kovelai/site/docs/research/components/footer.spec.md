# Component Spec: Footer

**Source Section:** `.footer` (index 10)
**Extracted from:** https://www.unusualmachines.com
**Target Component:** `src/components/Footer.tsx`

---

## Extracted Styles (getComputedStyle)

```css
.footer {
  font-size: 16px;
  font-weight: 300;
  font-family: Arial;
  color: rgb(0, 0, 0);
  background-color: rgb(41, 30, 68); /* deep purple */
  padding: 20px;
  display: block;
  position: static;
  width: 100%;
  height: 60px;
}
```

## Structure

```
footer.footer
  └── (container)
       ├── "Unusual Machines - All Rights Reserved"
       └── Social media icons (inline)
            ├── img: facebook (20×21)
            ├── img: instagram (19×19)
            ├── img: linkedin (18×19)
            └── img: twitter (18×19)
```

## Visual Pattern

- Compact footer (60px height, 20px padding)
- Deep purple background (`rgb(41, 30, 68)`)
- Copyright text + social media icon row
- Minimal, single-row layout

## Social Icons

| Platform | Icon Size | Source |
|----------|-----------|-------|
| Facebook | 20×21 | `icon-facebook.png` |
| Instagram | 19×19 | `icon-instagram.png` |
| LinkedIn | 18×19 | `icon-linkedin.png` |
| Twitter/X | 18×19 | `icon-twitter.png` |

## KovelAI Adaptation Notes

- Keep compact footer pattern (60-80px)
- Use our design system dark color (`#071325`) instead of deep purple
- Replace copyright: "© 2026 KovelAI. All rights reserved."
- Add: Privacy Policy, Terms of Service, Status links
- Social icons: use Lucide icons instead of PNGs
- Platforms: LinkedIn, Twitter/X, GitHub (for dev credibility)
