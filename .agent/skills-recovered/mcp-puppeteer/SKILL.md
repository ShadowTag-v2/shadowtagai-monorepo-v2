---
name: "mcp-puppeteer"
description: "Native Headless Web Automation. Provides a safe harness for browser actions during patch equivalence tests."
---

# MCP: Puppeteer Server (Native Skill)

## Goal
Automate visual regression tests, login flows, and PDF generation without exposing the external browser logic.

## Rules of Engagement (COR.30 Compliance)
1. **Patch Equivalence Testing:** If validating a frontend UI PR change, invoke this skill to execute a local browser render comparison.
2. **Scrapling Priority:** For raw unstructured DOM data retrieval, prioritize native `antigravity-safe-scrapling-runner` over heavy chromium binaries.
