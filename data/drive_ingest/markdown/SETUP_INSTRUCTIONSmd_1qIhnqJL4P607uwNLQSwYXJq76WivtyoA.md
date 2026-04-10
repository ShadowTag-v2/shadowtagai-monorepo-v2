# Antigravity Tools Setup Instructions

## 1. Antigravity Quota Watcher (VS Code Extension)
The extension has been built and packaged.
**Location:** `~/ShadowTag-v2-stack/antigravity-tools/AntigravityQuotaWatcher/antigravity-quota-watcher-0.7.1.vsix`

**To Install:**
1. Open Antigravity (VS Code).
2. Go to Extensions view (`Cmd+Shift+X`).
3. Click "..." (Views and More Actions) > "Install from VSIX...".
4. Select the file above.

## 2. Antigravity Proxy (License/Key Management)
The proxy intercepts requests to Google's API and injects your key.
**Location:** `~/ShadowTag-v2-stack/antigravity-tools/antigravity-proxy`

**Setup:**
1. Edit the `.env` file:
   ```bash
   nano ~/ShadowTag-v2-stack/antigravity-tools/antigravity-proxy/.env
   ```
   Set `GEMINI_API_KEY=your-actual-key`.

2. Start the proxy:
   ```bash
   mitmproxy -s ~/ShadowTag-v2-stack/antigravity-tools/antigravity-proxy/mitmproxy-addon.py --listen-port 8080
   ```

3. Launch Antigravity with proxy settings:
   ```bash
   HTTP_PROXY=http://localhost:8080 HTTPS_PROXY=http://localhost:8080 /Applications/Antigravity.app/Contents/MacOS/Antigravity
   ```

## 3. Antigravity Workspace Template
A ready-to-use agentic workspace.
**Location:** `~/ShadowTag-v2-stack/antigravity-tools/antigravity-workspace-template`

**Usage:**
Open this folder in Antigravity to start a new project with MCP and Swarm support pre-configured.