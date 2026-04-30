---
name: production-ux
description: Use when building frontend components, pages, routing, and user-facing interactions to prevent dead ends and silent UX failures.
---

# Production UX — No Blank Screens, No Dead Ends

> **Philosophy:** A user should never see a blank white screen, a stuck spinner, or a dead-end route.
> **Cross-references:** `design-taste-frontend`, `tacsop0-building-websites`, `cor-meatbridge-eviction`

## Instructions

### 1. Loading States (Mandatory)
- Every async action (form submissions, AI generation, data fetches) MUST have an explicit loading state.
- Acceptable patterns:
  - Disabled buttons with spinner during submission.
  - Skeleton screens during data loading.
  - React `<Suspense>` with meaningful fallback UI.
  - `useFormStatus` / `useTransition` for Server Actions.
- **NEVER** leave a button clickable during an async operation. Duplicate submissions = duplicate charges, duplicate records, duplicate emails.

### 2. Error Boundaries (Non-Negotiable)
- Scaffold a global `error.tsx` (Next.js) or equivalent error boundary at the app root.
- Every route segment should have its own `error.tsx` to prevent cascade failures.
- Error boundaries must:
  1. Show a user-friendly message (not a stack trace).
  2. Provide a "Try Again" action.
  3. Log the error to the console for debugging.

### 3. 404 / Not Found (The Dead End Fix)
- A global `not-found.tsx` MUST exist.
- It must provide:
  1. A clear "Page Not Found" message.
  2. A link back to the homepage or dashboard.
  3. Optionally, a search bar or suggested links.
- **NEVER** leave a user staring at a browser's default error page.

### 4. Mobile Viewport (The iPhone 5S Rule)
- All UI must be functional at 320px viewport width.
- Primary CTAs must be tap-targetable (minimum 44x44px).
- Navigation must not overflow or break at small viewports.
- Before declaring UI complete, verify with Chrome DevTools MCP at 320px width.
- Reference: `pre-deploy` workflow for automated mobile viewport testing.

### 5. Optimistic UI & Feedback
- User actions should provide immediate visual feedback.
- For mutations: show optimistic state, then reconcile with server response.
- For destructive actions (delete, cancel subscription): require confirmation dialog.
- Toast notifications for success/failure states.

### 6. Accessibility Baseline
- All interactive elements must be keyboard-navigable.
- Images must have alt text.
- Form inputs must have associated labels.
- Color contrast must meet WCAG AA (4.5:1 for normal text).
- Run Lighthouse accessibility audit before shipping (target: >90).
