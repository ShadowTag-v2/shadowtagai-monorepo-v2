# Pitch Deck Implementation Plan (The Pickle Rick Protocol)

**Status:** DRAFT
**Persona:** Pickle Rick 🥒

## 🥒 The Gist
You want a Pitch Deck. The codebase has no Pitch Deck. I'm going to put the Pitch Deck in the codebase.
The browser subagent failed because there was nothing to find. Standard issue reality.

## ⚠️ User Review Required
**Discrepancy Detected:**
You asked for **$229** and **95%**.
The source of truth (`pitch/INVESTOR_DECK_ROI.md`) says:
- **ROI:** 11,636% (Not 95%)
- **Payback:** 4.6 Days
- **Total Value:** $3.6M
- **Gross Margin:** 92% (Close to 95%, maybe?)
- **Cost:** $30,663 / $870 mo.

I will implement using the **MD file's data** unless you tell me otherwise. If you want "$229" and "95%", you better show me where you hid them.

## 🛠️ Proposed Changes

### Frontend (`frontend/src/app/`)
#### [NEW] `pitch/page.tsx`
- **Route:** `/pitch`
- **Content:** Parse/Render `INVESTOR_DECK_ROI.md` (or hardcode the key metrics if MD parsing is too slow/heavy for this sprint).
- **Style:** "Void" aesthetic (Dark mode, neon highlights, `bg-void`, `text-starlight`).
- **Components:**
    - `MetricCard` for the big numbers.
    - `ThesisSection` for the "First Principles" breakdown.

### Components (`frontend/src/components/`)
#### [MODIFY] `ReactorCore.tsx`
- Wire the "IGNITE REACTOR" button (or add a secondary button) to navigate to `/pitch`.

## ✅ Verification Plan

### Automated
1.  **Browser Subagent:**
    - Navigate to `/pitch`.
    - Check for "11,636%" and "$30,663" (or your specific numbers if you correct them).
    - Verify no console errors.

### Manual
1.  Open `http://localhost:3000/pitch`.
2.  Bask in the glory of high ROI.
