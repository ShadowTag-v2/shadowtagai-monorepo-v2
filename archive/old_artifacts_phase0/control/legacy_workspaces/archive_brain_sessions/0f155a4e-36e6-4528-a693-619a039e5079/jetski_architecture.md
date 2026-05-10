# Declassifying Jetski: Building a "Clean" Browser Agent

Based on the reverse-engineering analysis you provided, the "Jetski" architecture relies on a **Custom Chrome Extension** (`eeijfnjmjelapkebgockoeaadonbchdd`) acting as a bridge between the MCP Server and the Chrome DevTools Protocol (CDP).

## 1. The Bottleneck: Why "This App is Blocked" happens
Google's security systems likely detect the specific **Extension ID** or the **User-Agent** modified by the Antigravity Browser environment. The "Extension-as-Middleware" pattern, while powerful for capturing DOM/Screenshots efficiently, leaves a distinct fingerprint.

## 2. The Solution: A "Non-Antigravity" Implementation (Vanilla)
To bypass this, you need an agent that drives a **Standard Browser** (like Brave or Stock Chrome) without injecting a custom extension that modifies the runtime environment.

### Architecture Comparison

| Component | **Antigravity Jetski** | **Clean / Vanilla** |
| :--- | :--- | :--- |
| **Orchestrator** | Language Server (Go/Binary) | Python/Node Script or `langchain` |
| **Protocol** | proprietary `jetski` -> MCP | Standard MCP |
| **Bridge** | **Chrome Extension (HTTP Server)** | **Playwright / Puppeteer (Direct CDP)** |
| **Target** | Antigravity Chrome Profile | Existing User Profile (Brave/Chrome) |

### 3. How to Build It (The "Clean" Jetski)

Instead of writing a Chrome Extension to talk to CDP, use **Playwright** to connect to an existing browser instance.

#### Step A: Launch Brave with Debugging Port
Launch your daily driver (Brave) with a remote debugging port open. This allows the Agent to control your *logged-in* session (solving auth cookies).

```bash
# MacOS
/Applications/Brave\ Browser.app/Contents/MacOS/Brave\ Browser \
  --remote-debugging-port=9222 \
  --no-first-run \
  --no-default-browser-check \
  --user-data-dir="/Users/$USER/Library/Application Support/BraveSoftware/Brave-Browser"
```

#### Step B: The MCP Server (Python/Playwright)
Create a simple MCP server that tools can call. This server connects to Brave on port 9222.

```python
# clean_jetski.py
from mcp.server import Server
from playwright.sync_api import sync_playwright

def navigate(url):
    with sync_playwright() as p:
        # Connect to the EXISTING Brave instance
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        page.goto(url)
        return "Navigated to " + url

def click_element(selector):
    # ... implementation using standard Playwright selectors
    pass
```

### 4. Why this works
*   **No Extension ID**: You are just "Brave Browser" to Google.
*   **Shared Cookies**: You use your actual profile, so you are likely already logged into Google (no `gcloud login` flows needed if utilizing REST APIs, or easier bypass if needed).
*   **Undetectable**: Playwright connected over CDP is very hard to distinguish from normal usage if `headless=False` is set (which it is, since you're watching it).

## Summary
The "Antigravity" signature comes from the **Extension ID** and the isolated **`antigravity-browser-profile`**. By shifting the control layer from an *Extension* to *External CDP Control* (Playwright) over your *Main Profile*, you eliminate the variables triggering the block.
