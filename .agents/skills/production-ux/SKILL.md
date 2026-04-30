---
name: production-ux
description: Physical demands for Next.js Frontend Components.
---
# Instructions
1. **No Blank Screens:** You MUST scaffold a global `not-found.tsx` and `error.tsx` page. A user who clicks a broken link and gets a white screen never comes back.
2. **Explicit Loading States:** The app didn't freeze; the user thinks it did. All async forms MUST use `useFormStatus` (`<SubmitButton disabled={pending}>`) or `<Suspense>`.
3. **The 30-Second Rule:** If a user cant figure out the core action in 30 seconds, its broken. Ugly ships. Confusing dies.
