# Component Spec: Events Section

**Source Section:** `.homeEvents` (index 6)
**Extracted from:** https://www.unusualmachines.com
**Target Component:** `src/components/Events.tsx`

---

## Extracted Styles (getComputedStyle)

```css
.homeEvents {
  font-size: 16px;
  font-weight: 300;
  font-family: Arial;
  color: rgb(0, 0, 0);
  background-color: rgb(255, 255, 255);
  padding: 55px 0;
  display: block;
  position: static;
  width: 100%;
  height: 346px;
}
```

## Structure

```
section.homeEvents
  └── div.container
       ├── h2.sectionTitle: "Upcoming Events"
       ├── (event items — currently: "No upcoming events!")
       └── a: "See all" (link to events page)
```

## Visual Pattern

- White background section with uniform 55px vertical padding
- Section title followed by event list (or empty state)
- "See all" CTA link at bottom

## KovelAI Adaptation Notes

- Replace with "Testimonials" or "Trusted By" section
- Maintain white background, 55px padding pattern
- Use client logos or testimonial cards
- Keep the "See all" CTA pattern → "View All Testimonials"
