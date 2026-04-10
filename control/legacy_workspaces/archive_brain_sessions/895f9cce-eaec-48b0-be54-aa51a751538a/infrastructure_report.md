# Infrastructure & Configuration Report

> **AUTHORITY:** The Board of Directors (IQ 160 Lock)
> **TO:** Founder CEO Erik
> **SUBJECT:** System Infrastructure & MCP Integrations

In accordance with the Grounding Protocol (K.3) and the Bourne Metric (F.1), here is the analysis of our Docker environments and MCP server configuration.

---

## 1. MCP Servers in Antigravity

You asked how to add **Chrome-Devtools**, **Grounding**, and **Developer Knowledge** MCP servers.

I have audited `~/Library/Application Support/Code/User/settings.json` and confirmed that **Antigravity natively manages these via the `"antigravity.mcp.registry"` block**.

### Current Configuration (Already Active)
Your `settings.json` already contains mappings for these! You do not need to do anything else to install them. Here is how they are operating:

*   **Chrome DevTools:** Installed locally via Node.
    ```json
    "chrome-devtools": {
        "command": "npx",
        "args": ["-y", "chrome-devtools-mcp@latest"]
    }
    ```
*   **Developer Knowledge:** Connected directly via the Google API.
    ```json
    "google-developer-knowledge": {
        "serverUrl": "https://developerknowledge.googleapis.com/mcp",
        "headers": { "X-Goog-Api-Key": "<redacted>" }
    }
    ```
*   **Grounding:** Grounding is not technically a standalone "MCP Server" in the traditional sense; rather, it is enforced via the `geminicodeassist` engine connecting to your Vertex AI data stores (the 5GB uploaded Grounding Library). It activates automatically based on your Cloud Code project (`shadowtag-omega-v4`).

**If you ever need to add new ones in the future**, simply open your VS Code Settings (JSON) and append them to the `"antigravity.mcp.registry"` -> `"mcpServers"` object.

---

## 2. Docker Environments: The "Spawning" Issue

You asked what we can delete and why Docker keeps spawning new things.

### Why does it keep spawning?
The massive accumulation (`29.4GB` of images, `19.71GB` of build cache) is caused by two overlapping systems:
1.  **VS Code Dev Containers:** Your `uphillsnowball-ag-workstation` is managed by VS Code. Every time you update a setting that affects the container environment, VS Code spins up a new intermediate layer, leaving the old, unused ones behind ("dangling images").
2.  **Buildx (Docker Buildkit):** The `buildx_buildkit_default` container caches every `NPM install` and Python package you build. As you iterate rapidly in YOLO mode, the cache grows exponentially.

### What can we delete?
Absolutely everything that isn't actively running.

> [!TIP]
> **Actionable Cleanup Command**
> Run this command in your terminal to nuke the 20GB+ of dead weight without affecting your running dev experience:
> ```bash
> docker system prune -a --volumes -f
> ```
> *Note: This will delete unused images, stopped containers, and build cache. If you restart the workstation later, it may take an extra 2 minutes to "re-warm" the cache, which is perfectly safe.*

---

## 3. "The Nag Protocol" (H.1) - CEO Action Required

As mapped by our execution mandates, I require your directive on the next strategic maneuver. Please select one (or multiple) of the following options:

1.  **[CLEAN HOUSE]:** "Have The Board execute `docker system prune` and completely flush the Docker artifacts to reclaim memory."
2.  **[VALIDATE PUSH]:** "Check the background batch git push the Board previously initiated up to GitHub to ensure the 4.6GB history synced properly."
3.  **[OMEGA LOOP STATUS]:** "Review the `finish_changes.py` linter outputs and continue executing the next block for the `transcript_to_contract.py` prototyping."
4.  **[NEW DIRECTIVE]:** Provide custom orders bypassing the above.
