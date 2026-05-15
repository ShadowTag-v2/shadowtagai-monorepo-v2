---
name: production-ux
description: Physical demands for Next.js Frontend Components.
---
# Instructions
1. **No Blank Screens:** You MUST scaffold a global `not-found.tsx` and `error.tsx` page. A user who clicks a broken link and gets a white screen never comes back.
2. **Explicit Loading States:** The app didn't freeze; the user thinks it did. All async forms MUST use `useFormStatus` (`<SubmitButton disabled={pending}>`) or `<Suspense>`.
3. **The 30-Second Rule:** If a user cant figure out the core action in 30 seconds, its broken. Ugly ships. Confusing dies.

## The Cryptographic Spinner Protocol
A spinner is not a decoration; it is a DOM lock.
1. **Never use `useState` for loading.** ALL forms MUST use React 19 `<form action={...}>` and `useActionState`.
2. **The DOM Lock:** ALL submit buttons MUST be wrapped in the `<SubmitButton>` component utilizing `useFormStatus()`, rendering a `lucide-react` `<Loader2>` icon.
3. **The Physics Lock:** For destructive mutations (payments, orders), the Server Action MUST extract a hidden `idempotencyKey` and validate it against `checkIdempotency()` via Upstash Redis before writing to the database.
