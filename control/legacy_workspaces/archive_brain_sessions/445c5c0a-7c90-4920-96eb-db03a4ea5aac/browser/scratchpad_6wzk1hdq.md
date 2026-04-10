# Task: Inspect Landing Page at http://localhost:3001/

## Plan
- [x] Open `http://localhost:3001/`
- [x] Wait 5 seconds for full rendering
- [x] Check Navbar for "About Us", etc., and "CONTACT SALES" button
- [x] Check HeroContent for "HERE TO PROACTIVELY SECURE..." on the left
- [x] Check for "NYSE: SHDW" stock ticker mock on the right
- [x] Capture a screenshot of the top viewport
- [x] Report findings

## Findings
- Page title: "judge6 based uphillsnowball"
- Hero text "HERE TO PROACTIVELY SECURE..." is present and large on the left.
- Stock ticker "NYSE: SHDW" is present on the right with price information.
- Navbar links ("About Us", "Media & Events", "Investors", "Contact", "Careers") are present in the DOM but are **not visible** because their container has the Tailwind `hidden` class and remains `display: none` even at widths of 1268px and 1600px.
- "CONTACT SALES" button is also present in the DOM but **not visible** (part of the same hidden container).
- **Hydration Error**: Console logs show a React hydration mismatch: "A tree hydrated but some attributes of the server rendered HTML didn't match the client properties." This likely explains the style application failure.
- A "Next.js 1 Issue" toast is visible on the bottom left of the page.
