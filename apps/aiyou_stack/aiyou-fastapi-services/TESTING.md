# 🧪 Antigravity Testing Protocol

Follow this sequence to verify the "Vibe Coding" integration.

## 1. Automated System Check

Run the included verification script to check file paths and configurations:

```bash
./bin/test_antigravity.sh
```

## 2. Chrome DevTools MCP Test

**Goal:** Verify the Agent can "see" and "control" your browser.

1. **Launch Chrome in Debug Mode:**
    Paste this into your terminal (or ensure your Chrome is launched this way):

    ```bash
    /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
    ```

2. **Open a Test Page:**
    Navigate to `https://example.com` in that Chrome window.
3. **Prompt the Agent:**
    Ask Antigravity: *"Check the console logs of my active Chrome tab."*
    * **Success:** The Agent returns logs or confirms no errors.
    * **Failure:** The Agent says it cannot connect or doesn't have the tool.

## 3. Vibe Coding "Turbo Mode" Test

**Goal:** Verify the protocol is active.

1. **Check Protocol:** Open `ShadowTag-Omega/GEMINI.md`.
2. **Action:** Request a small UI change (e.g., "Change the simplified-ui button color to purple").
3. **Observation:** The Agent should cite "Turbo Mode" (implied speed) or "Agent Decides" policy if the change is minor, without asking for excessive permission.

## 4. "Beads" Memory Test

**Goal:** Verify durable context.

1. **Create a Bead:**
    Ask the Agent: *"Create a memory bead recording that we prefer standard HTML over ShadCN for this project."*
2. **Verify:**
    Check `.gemini/memory/` for a new markdown file containing this decision.
