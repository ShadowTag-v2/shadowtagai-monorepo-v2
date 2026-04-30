# Task: Verify localhost:3001 dashboard and fix pathway issues

## Plan

1. [x] Navigate to <http://localhost:3001/>
2. [x] Wait for page to load and check for "useAgent" or "CONNECTION_REFUSED" errors.
3. [x] Take a screenshot of the dashboard.
4. [x] Check browser console logs for errors.
5. [x] Reporting back findings.

## Discoveries

- **CONNECTION_REFUSED** is gone. The backend at `localhost:8080` is responding.
- **useAgent** error is not explicitly seen, but `connectAgent` is failing with a **404 Not Found** for `http://localhost:8080/api/v1/copilotkit/`.
- The dashboard at `http://localhost:3001/` is showing a **Next.js hydration error** overlay ("A tree hydrated but some attributes...").
- A request to `http://localhost:3001/api/v1/omniscience/radar` also returns a **404 Not Found**.
- The static integrated UI at `http://localhost:3001/luminina.html` displays correctly without errors, but the main dashboard does not.
