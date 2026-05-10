# Component Spec: Contact Section

**Source Section:** `.homeContact` (index 8)
**Extracted from:** https://www.unusualmachines.com
**Target Component:** `src/components/Contact.tsx`

---

## Extracted Styles (getComputedStyle)

```css
.homeContact {
  font-size: 16px;
  font-weight: 300;
  font-family: Arial;
  color: rgb(0, 0, 0);
  background-color: rgba(0, 0, 0, 0.5); /* dark overlay */
  background-image: url("USA_FC-6-1-1.jpg");
  background-repeat: no-repeat;
  background-position: 50% 50%;
  background-size: cover;
  padding: 55px 0;
  position: relative;
  width: 100%;
  height: 756px;
}
```

## Structure

```
section.homeContact
  └── div.container
       ├── h2.sectionTitle.sectionTitle--white: "Contact"
       └── (contact content layout)
            ├── Investor Contact block
            │    ├── "Investor Contact" label
            │    ├── "You can talk to our IR team..."
            │    ├── Email: investors@unusualmachines.com
            │    ├── Christine Petraglia, CS Investor Relations
            │    └── T: 917-633-8980
            └── Media Inquiries block
                 ├── media@unusualmachines.com
                 └── 917-771-7693
```

## Visual Pattern

- Full-bleed background image with dark overlay (50% black)
- White section title (`.sectionTitle--white`)
- Two-column contact info on white/light text over dark background
- Contains a contact form (likely in a separate sub-component)

## KovelAI Adaptation Notes

- Replace with KovelAI contact form + info
- Maintain dark overlay + background image pattern
- Use our generated background imagery
- Two-column: Contact form left, contact info right
- Section title: "Get in Touch" or "Contact Us"
- Include: email, phone, social links
- Add form fields: Name, Email, Company, Message (shadcn/ui Input + Textarea)
