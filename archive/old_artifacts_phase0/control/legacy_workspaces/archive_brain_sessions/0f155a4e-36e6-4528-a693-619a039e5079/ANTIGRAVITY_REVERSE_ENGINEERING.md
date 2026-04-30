# Reverse Engineering Google Antigravity 'Jetski' Browser Automation
Source: Alok Bishoyi / Daniel Strebel / Lucía Subatin

## 1. The Core Discovery
Antigravity's browser automation is not a simple library. It is a sophisticated multi-agent system codenamed **"Jetski"**.

- **The Trigger**: The user tool `browser_subagent`.
- **The Execution**: A dedicated Chrome instance running with `--remote-debugging-port=9222`.
- **The Brain**: A "Sub-Agent" running in the Language Server (Port 53410) with a specialized persona ("You are operating within the Jetski Browser context").

## 2. The Architecture (6 Layers)
1.  **The Trigger**: User asks "Go to Google".
2.  **The Coordinator**: Language Server (Port 53410) spins up "Jetski" Sub-Agent.
3.  **The Brain**: Sub-Agent plans action using "Jetski Browser" system prompt.
4.  **The Tool**: Calls `navigate()`, which goes to the MCP Server.
5.  **The Bridge**: MCP Server (`@agentdeskai/browser-tools-mcp`) sends HTTP POST to the **Antigravity Browser Connector Extension** (Port 3025).
6.  **The Execution**: Extension translates to Chrome DevTools Protocol (CDP) on Port 9222.

## 3. The Docker Integration (Uphillsnowball)
To run this in a Cloud Workstation (Headless), specific configuration is required to support the "Visual" aspect:

**Dockerfile Requirements**:
- `google-chrome-stable`
- `chrome-remote-desktop`
- `xvfb` (Virtual Framebuffer)
- `--no-sandbox` flag hack for Chrome in Docker.

**Startup Script**:
- Must initialize `chrome-remote-desktop` session.
- Must execute `/opt/google/chrome-remote-desktop/chrome-remote-desktop --start`.

## 4. The Jetski Toolset
The binary contains 19 ToolConverters, exposing 12 core tools to the agent:
1.  `browser_navigate` (Open URL/Reload)
2.  `read_browser_page` (Get DOM Tree)
3.  `browser_click_element` (Click by Index)
4.  `browser_select_option`
5.  `browser_press_key`
6.  `browser_scroll` / `scroll_up` / `scroll_down`
7.  `browser_resize_window`
8.  `capture_browser_screenshot`
9.  `execute_browser_javascript`
10. `list_browser_pages`

## 5. The System Prompt (Reconstructed)
* "You are operating within the 'Jetski Browser' context."
* "Act as if the tool calls will be executed immediately..."
* "Elements are indexed for interaction - use the index from the DOM tree response."
* "All browser interactions are automatically recorded and saved as WebP videos."

## 6. Enterprise "Add-Ons" (Productization)
To sell this as "Managed Agentic Workspaces":
1.  **Compliance Sidecar**: Log tailing on Port 9222 (Audit Trail).
2.  **Hybrid Access**: Toggle between CRD (UDP) and noVNC (HTTPS).
3.  **Secure Perimeter**: VPC Service Controls blocking public GitHub.
4.  **Agent Personas**: Pre-injected System Prompts ("QA Bot", "Refactor Bot").
