# Component Spec: Recent News / Highlights

**Source Section:** `.homeHighlights` (index 3)
**Extracted from:** https://www.unusualmachines.com
**Target Component:** `src/components/Highlights.tsx`

---

## Extracted Styles (getComputedStyle)

```css
.homeHighlights {
  font-size: 16px;
  font-weight: 300;
  font-family: Arial;
  color: rgb(0, 0, 0);
  background-color: rgb(255, 255, 255);
  padding: 55px 0;
  display: block;
  position: static;
  width: 100%;
  height: ~605px;
}
```

## Structure

```
section.homeHighlights
  └── div.container
       ├── h2.sectionTitle: "Recent News" (height: 53px)
       └── div#LibDiv.regulatory-news.b2iLibToolsContainer1
            ├── div.b2iLibraryItem
            │    ├── span.b2iLibraryItemDate: "April 21, 2026"
            │    └── span.b2iLibraryItemHeadline
            │         └── a.b2iLibraryHeadlineLink: "Unusual Machines Secures $5M+..."
            ├── div.b2iLibraryItem (repeat)
            └── div.b2iLibraryItem (repeat)
```

## Content Pattern

3 news items displayed in a vertical list:
1. **Date** (small, left-aligned) + **Headline** (linked)
2. Items use `.b2iLibraryItem` class (B2i Investor Relations widget)
3. Headlines are clickable (open press release viewer)

## Section Title Style

- Tag: `h2.sectionTitle`
- Height: 53px
- Implied: bold, large text, centered or left-aligned within container

## Schema.org Structured Data

The section includes structured data (`ItemList` of `PressRelease` items) — SEO-relevant.

## KovelAI Adaptation Notes

- Replace "Recent News" with "Latest Updates" or "What's New"
- Replace B2i widget with custom card layout
- Maintain white background, 55px vertical padding
- Use card components (shadcn/ui Card) for each item
- Each card: date badge + headline + "Read More" link
- Consider 3-column grid on desktop vs vertical list
