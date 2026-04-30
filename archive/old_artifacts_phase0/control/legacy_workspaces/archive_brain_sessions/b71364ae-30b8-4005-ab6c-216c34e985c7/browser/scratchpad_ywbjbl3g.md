# Browser Task: ShadowTag Dashboard Verification

## Plan

- [x] Go to <http://localhost:3001>
- [x] Perform hard reload (bypass cache)
- [x] Wait 3-5 seconds
- [x] Capture screenshot
- [x] Check console logs for "useAgent: Agent default not found"
- [x] Report findings

## Progress

- Navigated to <http://localhost:3001>.
- Performed hard reload using `window.location.reload(true)`.
- Waited 5 seconds.
- Captured screenshot `shadowtag_dashboard_error_1772414058366.png`.
- Verified that the error **"useAgent: Agent 'default' not found after runtime sync"** still persists.
- Noticed additional 404 errors in console for `/api/v1/copilotkit` and `/api/v1/omniscience/radar`.
