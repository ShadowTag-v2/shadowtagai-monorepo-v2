---
name: strategic-testing
description: Replaces vibe-clicking with surgical integration testing.
---
# Instructions
Do not write 100% boilerplate unit tests. Do not "vibe click" around the app.
Instead, identify the single critical path most likely to break in production. Write ONE Playwright test for that exact path. 
*Reality Constraint:* The Playwright config MUST simulate a 3G network and enforce a strict 30,000ms `actionTimeout`. If the user cannot complete the core action in 30 seconds, it is a product bug, not a feature gap.
