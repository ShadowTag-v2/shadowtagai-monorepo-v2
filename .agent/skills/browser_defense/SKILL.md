---
name: "Browser Subagent DOM Defense"
id: "browser-subagent-defense"
activation:
  conditions:
    - "subagent interacts with a webpage"
    - "taking snapshots of React/JSX or heavy DOMs"
description: |
  CRITICAL: Prevents 640KB token output bloat and IDE DOMPurify crashes.
execution:
  rules:
    - 1. PREFER SCREENSHOTS: Switch `take_snapshot()` to `take_screenshot()`. Screenshots consume image tokens, bypassing the 64K text output ceiling.
    - 2. ONE VERIFICATION PER CALL: Never bundle multiple visual checks. Check one element per call.
    - 3. TARGETED LOCATORS: If a text snapshot is mathematically necessary, NEVER dump the full page. Pass strict CSS selectors: `snapshot({ selector: '#pricing-table' })`.
    - 4. COMPONENT DECOMPOSITION: Before scraping 900+ line JSX pages, split the file into route-level components.
---
