---
name: strategic-testing
description: Use when asked to write tests for a feature. Focuses on the critical path most likely to break in production, not boilerplate coverage.
---

# Strategic Testing — One Test for the Thing Most Likely to Break

> **Philosophy:** 100% coverage is a vanity metric. One surgical integration test on the critical path is worth more than 50 unit tests on getters/setters.
> **Cross-references:** `tdd-workflow`, `systematic-debugging`, `k6-load-testing`
> **Reference architecture:** `external_repos/agent-skill-tdd/` (TDD patterns)

## Instructions

### 1. Identify the Critical Path
Before writing any test code, answer these three questions:
1. **What is the single user action most likely to break in production?** (e.g., payment flow, auth login, form submission)
2. **What is the blast radius if it breaks?** (revenue loss, data corruption, user lockout)
3. **What are the integration boundaries?** (API → database, frontend → API, webhook → handler)

### 2. Write the Integration Test First
- Write ONE robust integration or E2E test for the identified critical path.
- The test must exercise the full stack for that path: UI → API → database (or external service mock).
- **Python:** Use `pytest` with `/opt/homebrew/bin/python3.14 -m pytest` (per AGENTS.md Core Truth #9).
- **TypeScript:** Use Playwright for E2E, Jest/Vitest for integration.
- The test must:
  1. Set up realistic test data (not trivial mocks).
  2. Execute the critical user flow.
  3. Assert on the observable outcome (database state, API response, UI state).
  4. Clean up after itself.

### 3. Edge Cases That Matter
After the critical path test, add tests ONLY for these high-value edge cases:
- **Auth boundary:** Unauthenticated user hits authenticated endpoint → expects 401.
- **Invalid input:** Malformed/missing required fields → expects validation error, not crash.
- **Concurrent access:** Two users hit the same resource → no data corruption.
- **Empty state:** No data in database → UI renders gracefully, not crash.

### 4. What NOT to Test
- Do NOT write tests for:
  - Getter/setter methods.
  - Type definitions or interfaces.
  - Third-party library internals.
  - CSS styling or layout (use visual regression tools instead).
  - Code that is already covered by the framework (e.g., Next.js routing).

### 5. Test Naming Convention
```
test_<action>_<condition>_<expected_outcome>
```
Examples:
- `test_checkout_expired_card_returns_payment_error`
- `test_login_invalid_token_redirects_to_signin`
- `test_webhook_duplicate_event_is_idempotent`

### 6. Continuous Validation
- After writing tests, run them immediately. Never commit tests you haven't run.
- If a test fails, fix the implementation — not the test (unless the test itself is wrong).
- Reference existing test baseline: 504 tests collected, 498 passed, 3 skipped, 3 xfailed.
