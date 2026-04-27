# Architecture: Native Jetski (The "No-Extension" Approach)

The user correctly identified that Antigravity uses a **Chrome Extension** as a translator (HTTP -> CDP). This creates a fingerprint.
To avoid this, we use the browser's **Native Interface** directly.

## 1. The Core Concept
The `brave-core` repository (and Chromium) includes a built-in server called **CDP (Chrome DevTools Protocol)**.
*   **Antigravity**: Adds an extra "Server" (The Extension) to make it easier to talk to.
*   **Native Jetski**: Talks directly to the Browser's internal "Server" (CDP).

## 2. Implementation Steps

### A. Launch Brave "Open" (Server Mode)
We need to start Brave so it listens for instructions on a specific port (9222).

**File**: `scripts/launch_brave_debug.sh`
```bash
#!/bin/bash
# MacOS Path for Brave
BRAVE_PATH="/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"

# Launch with Remote Debugging (The "Native Server")
"$BRAVE_PATH" \
  --remote-debugging-port=9222 \
  --user-data-dir="/tmp/brave-automation-profile" \
  --no-first-run \
  &
echo "Brave launched on Port 9222. Waiting for CDP..."
```

### B. The Controller (Python + Playwright)
Instead of sending HTTP requests to an extension, we send WebSocket messages to Port 9222. Playwright handles the complex CDP protocol for us.

**File**: `scripts/clean_jetski.py`
```python
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        print("Connecting to Brave Native CDP...")
        # Connect directly to the browser (No Extension needed)
        browser = p.chromium.connect_over_cdp("http://localhost:9222")

        # Get the first context (window)
        context = browser.contexts[0]
        page = context.pages[0]

        print("Navigating to GCloud (Native)...")
        page.goto("https://console.cloud.google.com")

        print(f"Page Title: {page.title()}")
        print("Native Control Established. No Extension Middleware detected.")

if __name__ == "__main__":
    main()
```

## 3. Why `brave-core` matters
You mentioned the `brave-core` git repo. You *could* modify the C++ source to add a new "Agent Protocol" directly into the binary. However, **CDP is already that protocol**. It is baked into `brave-core`. By using it, you are using the "native rails" of the browser, which is exactly why it is harder to detect than an extension.
