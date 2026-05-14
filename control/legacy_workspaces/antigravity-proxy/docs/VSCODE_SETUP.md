# VS Code / Antigravity Setup Guide

How to configure VS Code or Antigravity to use the proxy.

## Method 1: Launch with Environment Variables (Recommended)

This is the **simplest and most reliable** method for Electron-based apps like Antigravity and VS Code.

### For Antigravity

Use the provided launch script:

```bash
cd ~/dev/personal/antigravity-proxy
npm run launch
```

Or manually:
```bash
HTTP_PROXY=http://localhost:8080 \
HTTPS_PROXY=http://localhost:8080 \
NODE_TLS_REJECT_UNAUTHORIZED=0 \
/Applications/Antigravity.app/Contents/MacOS/Antigravity
```

### For VS Code

```bash
HTTP_PROXY=http://localhost:8080 \
HTTPS_PROXY=http://localhost:8080 \
NODE_TLS_REJECT_UNAUTHORIZED=0 \
/Applications/Visual\ Studio\ Code.app/Contents/MacOS/Electron
```

Or create an alias in `~/.zshrc` or `~/.bashrc`:

```bash
alias vscode-proxy='HTTP_PROXY=http://localhost:8080 HTTPS_PROXY=http://localhost:8080 NODE_TLS_REJECT_UNAUTHORIZED=0 code'
```

Then use:
```bash
vscode-proxy
```

---

## Method 2: VS Code Settings (Less Reliable)

Add to VS Code settings (doesn't always work for all extensions):

### Option A: User Settings UI

1. Open VS Code
2. Press `Cmd+,` (Settings)
3. Search for "proxy"
4. Set:
   - **Http: Proxy**: `http://localhost:8080`
   - **Http: Proxy Strict SSL**: `false`

### Option B: settings.json

```bash
# Open settings.json
code ~/.vscode/settings.json
```

Add:
```json
{
  "http.proxy": "http://localhost:8080",
  "http.proxyStrictSSL": false,
  "http.proxySupport": "on"
}
```

**Limitation:** This only affects VS Code's built-in HTTP client. Extensions that make direct API calls may bypass this.

---

## Method 3: System-Wide Proxy (macOS)

Set proxy for **all applications** on your Mac:

### Temporary (Current Shell)

```bash
export HTTP_PROXY=http://localhost:8080
export HTTPS_PROXY=http://localhost:8080
export NODE_TLS_REJECT_UNAUTHORIZED=0
```

Then launch apps from this terminal.

### Permanent (All Shells)

Add to `~/.zshrc` or `~/.bashrc`:

```bash
echo 'export HTTP_PROXY=http://localhost:8080' >> ~/.zshrc
echo 'export HTTPS_PROXY=http://localhost:8080' >> ~/.zshrc
echo 'export NODE_TLS_REJECT_UNAUTHORIZED=0' >> ~/.zshrc
```

**Reload shell:**
```bash
source ~/.zshrc
```

**⚠️ Warning:** This affects ALL applications! Only use for development.

### macOS Network Settings (GUI)

1. Open **System Settings** → **Network**
2. Select your active network (Wi-Fi or Ethernet)
3. Click **Details** → **Proxies**
4. Check **Web Proxy (HTTP)** and **Secure Web Proxy (HTTPS)**
5. Set both to:
   - **Server**: `localhost`
   - **Port**: `8080`
6. Click **OK**

**⚠️ Warning:** This routes **all web traffic** through the proxy!

---

## Method 4: Launch Script (Automated)

Create a custom launcher for Antigravity/VS Code with proxy pre-configured.

### Create Application Wrapper

<function_calls>
<invoke name="bash">
<parameter name="command">cat > ~/dev/personal/antigravity-proxy/scripts/create-app-launcher.sh << 'EOF'
#!/bin/bash

# Create macOS app launcher with proxy settings

APP_NAME="Antigravity-Proxy"
ANTIGRAVITY_PATH="/Applications/Antigravity.app/Contents/MacOS/Antigravity"
PROXY_PORT=8080

# Create app bundle structure
mkdir -p ~/Applications/${APP_NAME}.app/Contents/MacOS
mkdir -p ~/Applications/${APP_NAME}.app/Contents/Resources

# Create launcher script
cat > ~/Applications/${APP_NAME}.app/Contents/MacOS/${APP_NAME} << 'INNER_EOF'
#!/bin/bash
export HTTP_PROXY=http://localhost:8080
export HTTPS_PROXY=http://localhost:8080
export NODE_TLS_REJECT_UNAUTHORIZED=0
exec /Applications/Antigravity.app/Contents/MacOS/Antigravity "$@"
INNER_EOF

chmod +x ~/Applications/${APP_NAME}.app/Contents/MacOS/${APP_NAME}

# Create Info.plist
cat > ~/Applications/${APP_NAME}.app/Contents/Info.plist << 'PLIST_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Antigravity-Proxy</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.local.antigravity-proxy</string>
    <key>CFBundleName</key>
    <string>Antigravity Proxy</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
</dict>
</plist>
PLIST_EOF

echo "✓ Created ~/Applications/${APP_NAME}.app"
echo ""
echo "You can now launch Antigravity with proxy by:"
echo "  1. Opening Finder"
echo "  2. Going to ~/Applications"
echo "  3. Double-clicking '${APP_NAME}.app'"
EOF

chmod +x ~/dev/personal/antigravity-proxy/scripts/create-app-launcher.sh