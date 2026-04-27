# KOSMOS DUAL-WIELD STRATEGY
> **CLASSIFICATION**: TIER 20 // INTERNAL
> **DATE**: 2026-02-03
> **PHILOSOPHY**: "Speed First. Action Second."

## 1. The Operational Problem
Traditional "Browser Agents" are blunt instruments. They spin up a full Chromium instance (1GB+ RAM, 5s+ boot) just to check a text status code or read a Wikipedia paragraph. This is:
*   **Slow**: ~5-10s latency per interaction.
*   **Loud**: High fingerprint surface (Canvas, WebGL, AudioContext).
*   **Expensive**: High compute cost (Cloud Run Gen 2).

## 2. The Solution: Dual-Wield Swarm
We separate concerns into two specialized agents:

### 🦅 The Hunter (Speed Lead)
*   **Engine**: `requests`, `BeautifulSoup`, `DuckDuckGo`, `Google Search API`.
*   **Cost**: Micro-cents.
*   **Latency**: Milliseconds (200-500ms).
*   **Profile**: Invisible (Standard User-Agent).
*   **Mandate**: "Read the world. Find the door."

### 🏄 The Jetski (Heavy Hand)
*   **Engine**: `Playwright` (Headless Chromium), `Computer Use` (Vision).
*   **Cost**: Dollars.
*   **Latency**: Seconds (2-5s).
*   **Profile**: Distinct (Browser automation signatures).
*   **Mandate**: "Kick the door. Sign the papers."

## 3. The Protocol: "Kickoff & Handoff"
The system operates on an escalation ladder:

1.  **Level 1 (Hunter)**: Task enters. Hunter executes search/scrape.
    *   *Result*: "Here is the stock price." (Done. Cost: $0.00).
2.  **Level 2 (Barrier Detected)**: Hunter sees `401 Unauthorized` or a Login Form.
    *   *Action*: Hunter returns `status: HANDOFF`, `context: "Login to AWS"`.
3.  **Level 3 (Jetski)**: Swarm boots Jetski. Jetski inherits context, logs in, and performs the heavy action.
    *   *Result*: "Instance Deployed." (Done. Cost: $0.05).

## 4. Why This Wins
*   **90/10 Rule**: 90% of tasks are *informational*. 10% are *transactional*. We only pay the "Browser Tax" on the 10%.
*   **Stealth**: Reconnaissance is silent. We only reveal our "Agentic Face" when necessary.
*   **Resilience**: If Chrome crashes, Hunter still delivers Intel.

*“The Hunter spots the target. The Jetski takes the shot.”*
