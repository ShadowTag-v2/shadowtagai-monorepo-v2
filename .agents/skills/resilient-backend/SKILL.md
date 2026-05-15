---
name: resilient-backend
description: Native ops constraints for Next.js API Routes, Server Actions, and Auth logic.
---
# Instructions
1. **Day 1 Rate Limiting:** All API routes MUST be wrapped in Upstash Redis rate limiters. A refreshed page should never cost a $200 AWS bill.
2. **Strict Session Timeouts:** When configuring NextAuth or Clerk, enforce strict `maxAge` session expirations (e.g., 4 hours). Defend the cafe-laptop user.
3. **Zero Silent Failures:** Wrap all mutations in `safe-action.ts` utilizing `Resend`. If a form fails at 2 AM, it must email the engineering team.
