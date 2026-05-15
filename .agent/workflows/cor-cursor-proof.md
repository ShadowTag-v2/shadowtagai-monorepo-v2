# Cor.Cursor Proof — Meatbridge Eviction Verification

Prove that the agent can autonomously navigate, interact with, and verify frontend UI
without human intervention (Cor.Meatbridge Eviction Protocol).

## Doctrine
- Skill: `.agents/skills/cor-meatbridge-eviction/SKILL.md`
- The human is the ASYNCHRONOUS REVIEWER, never the manual UI router.
- Asking the user to "open localhost" or "check the UI" is a PROTOCOL VIOLATION.

## Steps

1. **Start Dev Server** — Launch the frontend dev server:
   ```bash
   cd apps/kovelai && npm run dev
   ```

// turbo
2. **Wait for Ready** — Confirm the dev server is running via port check.

3. **Navigate** — Use `chrome-devtools-mcp` to navigate to the dev server URL:
   - `navigate_page` to `http://localhost:3000` (or appropriate port)

4. **Snapshot** — Take a DOM snapshot via `take_snapshot` to verify page structure.

5. **Screenshot** — Capture visual proof via `take_screenshot`.

6. **Interact** — Demonstrate autonomous UI interaction:
   - Click a navigation element
   - Verify state change via new snapshot
   - Test responsive behavior via `resize_page`

7. **Lighthouse** — Run `lighthouse_audit` for accessibility and SEO validation.

8. **Console Check** — Run `list_console_messages` to verify no JS errors.

9. **Evidence** — Log the proof to `.agent/evidence/index.ndjson`:
   ```json
   {"timestamp":"<ISO>","action":"meatbridge_proof","url":"<url>","lighthouse":{"a11y":N,"seo":N},"console_errors":0}
   ```

## Completion Criteria
- Page loads without errors
- DOM snapshot captured
- Screenshot captured as visual proof
- At least one UI interaction demonstrated
- Lighthouse scores recorded
- Zero console errors (or all explained)
- Evidence logged
