# Implementation Plan - CopilotKit Translation & Stripe Finalization

## Goal
Fully flesh out the two major technical debts left on the table:
1. **CopilotKit Proxy Structure Match**: Resolve the 422 Error and "Cannot convert undefined or null to object" by implementing the exact structural match between the Next.js Proxy and the Judge 6 Sentinel backend.
2. **Stripe Webhook Binding**: Set up an active listener endpoint in the Next.js application to process `checkout.session.completed` events and bind licenses/access back to users natively using the `<USER_KEY_PROVIDED>` live key.

## Proposed Changes

### 1. CopilotKit Exact Structure Match

#### [MODIFY] [apps/shadowtag-web/app/api/copilotkit/\[\[...handle\]\]/route.ts]
- Implement bidirectional streaming capabilities if the SDK expects Server-Sent Events (SSE).
- Ensure that the `/info` object explicitly matches the GraphQL/REST schema expected by CopilotKit React Core 1.51.x, which demands strict properties: `models`, `tools`, etc.

#### [MODIFY] [apps/judge-sentinel/judge6_sentinel.py]
- Ensure the backend FastAPI application accepts `POST /copilotkit_remote` conforming either to the native `copilotkit` Python SDK standards, or properly formats the manual override to return `data` streams properly.

### 2. Stripe Webhook Implementation

#### [NEW] [apps/shadowtag-web/app/api/webhook/stripe/route.ts]
- Create the Stripe Webhook handler to parse incoming Stripe events.
- Requires `stripe` npm context and `stripe.webhooks.constructEvent` verification.
- Persist the transaction into the `Memory` database or Firestore to validate user access after `checkout.session.completed` triggers.

#### [MODIFY] [apps/shadowtag-web/package.json]
- Add `stripe` exactly to the dependency tree to ensure the server-side environment can decode and fulfill the Webhook securely.

## Verification Plan
1. **Validation of Proxy**: Mock a direct `POST` to `/api/copilotkit/info` and observe if it produces the expected CopilotKit initialization dictionary.
2. **Webhook Integrity**: Create a placeholder mock webhook event and simulate posting it to `/api/webhook/stripe` to ensure the 200 OK route fires and handles the logic appropriately.
