# MITM Proxy Setup (Working Solution)

This is the **actually working** solution for proxying Antigravity's API calls.

## Why This Instead of Node.js?

The Node.js proxy **cannot inspect HTTPS content** without implementing full MITM with certificate generation. 

`mitmproxy` is the industry-standard tool that handles all of this automatically.

## Installation (5 minutes)

### 1. Install mitmproxy

```bash
brew install mitmproxy
```

### 2. Install Python dependencies (for the addon)

```bash
# Install python-dotenv for reading .env file
pip3 install python-dotenv
```

### 3. Verify Installation

```bash
mitmproxy --version
```

Should output something like: `Mitmproxy: 10.x.x`

## Setup (10 minutes)

### 1. Install SSL Certificate

This is the **critical step** that allows mitmproxy to intercept HTTPS traffic.

```bash
# Start mitmproxy once to generate certificate
mitmproxy
```

Press `q` to quit.

The certificate is now at: `~/.mitmproxy/mitmproxy-ca-cert.pem`

### 2. Add Certificate to macOS Keychain

```bash
# Open certificate in Keychain Access
open ~/.mitmproxy/mitmproxy-ca-cert.pem
```

In Keychain Access:
1. Find "mitmproxy" certificate
2. Double-click it
3. Expand "Trust" section
4. Set "When using this certificate" to **"Always Trust"**
5. Close (you'll be prompted for password)

**Visual Guide:**
- Certificate should show "This certificate is marked as trusted for all users"
- Green checkmark next to "mitmproxy"

## Usage

### Start the Proxy

```bash
cd ~/dev/personal/antigravity-proxy

# Use the Python addon
mitmproxy -s mitmproxy-addon.py --listen-port 8080
```

You should see:
```
🚀 Antigravity Proxy - MITM Interceptor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔑 Using API Key: AIzaSyABC123***
🎯 Target: generativelanguage.googleapis.com
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Proxy server listening at http://*:8080
```

### Launch Antigravity

**In a new terminal:**

```bash
cd ~/dev/personal/antigravity-proxy

# Use the shell script
./scripts/launch-antigravity.sh
```

Or manually:
```bash
HTTP_PROXY=http://localhost:8080 \
HTTPS_PROXY=http://localhost:8080 \
/Applications/Antigravity.app/Contents/MacOS/Antigravity
```

### Verify It's Working

When you use Antigravity's AI features, you should see in the mitmproxy terminal:

```
📥 INCOMING REQUEST #1
   Method: POST
   URL: https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent
   🔄 Replaced key in header
      Old: AIzaSyABC123***
      New: AIzaSyDEF456***

✅ RESPONSE
   Status: 200

📊 Stats: 1 requests, 1 keys replaced
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Configuration

The addon reads from your `.env` file:

```bash
# Make sure you have this set
GEMINI_API_KEY=your_actual_api_key_here
```

## Troubleshooting

### Certificate Not Trusted

**Symptom:** Antigravity shows SSL errors

**Solution:**
1. Open Keychain Access
2. Search for "mitmproxy"
3. Double-click certificate
4. Set Trust to "Always Trust"
5. Restart Antigravity

### No Requests Appearing

**Symptom:** mitmproxy shows no traffic

**Solutions:**

1. **Verify proxy settings:**
   ```bash
   # In the terminal where you launched Antigravity
   echo $HTTP_PROXY
   echo $HTTPS_PROXY
   ```
   Should both output: `http://localhost:8080`

2. **Check if mitmproxy is running:**
   ```bash
   lsof -ti:8080
   ```
   Should return a process ID

3. **Test with curl:**
   ```bash
   HTTP_PROXY=http://localhost:8080 \
   HTTPS_PROXY=http://localhost:8080 \
   curl https://generativelanguage.googleapis.com/v1beta/models
   ```
   Should appear in mitmproxy logs

### mitmproxy Command Not Found

**Solution:**
```bash
brew install mitmproxy
```

### python-dotenv Not Found

**Solution:**
```bash
pip3 install python-dotenv
```

## Advanced Usage

### Interactive Mode

mitmproxy has an interactive TUI:

```bash
mitmproxy -s mitmproxy-addon.py
```

Press:
- `q` - Quit
- `?` - Help
- Arrow keys - Navigate requests
- Enter - View request/response details

### Web Interface

mitm has a web interface:

```bash
mitmweb -s mitmproxy-addon.py --listen-port 8080
```

Then open: http://localhost:8081

### Headless Mode

For background operation:

```bash
mitmdump -s mitmproxy-addon.py --listen-port 8080
```

### Save Traffic

Record all traffic to a file:

```bash
mitmdump -s mitmproxy-addon.py --listen-port 8080 -w traffic.mitm
```

Replay later:
```bash
mitmproxy -r traffic.mitm
```

## Comparison: Node.js vs mitmproxy

| Feature | Node.js Proxy | mitmproxy |
|---------|--------------|-----------|
| HTTPS Inspection | ❌ Doesn't work | ✅ Works perfectly |
| Certificate Setup | ❌ Complex | ✅ Automatic |
| API Key Replacement | ❌ Can't access content | ✅ Full access |
| Logging | ✅ Good | ✅ Excellent |
| Setup Time | 5 minutes | 10 minutes |
| **Actually Works** | ❌ No | ✅ Yes |

## Automation

### Create App Launcher

Add to `~/.zshrc` or `~/.bashrc`:

```bash
# Antigravity with proxy
antigravity-proxy() {
    # Start mitmproxy in background
    mitmdump -s ~/dev/personal/antigravity-proxy/mitmproxy-addon.py --listen-port 8080 > /dev/null 2>&1 &
    MITM_PID=$!
    
    # Wait for proxy to start
    sleep 2
    
    # Launch Antigravity
    HTTP_PROXY=http://localhost:8080 \
    HTTPS_PROXY=http://localhost:8080 \
    /Applications/Antigravity.app/Contents/MacOS/Antigravity
    
    # Kill mitmproxy when Antigravity exits
    kill $MITM_PID 2>/dev/null
}
```

Then just run:
```bash
antigravity-proxy
```

### Background Service (pm2)

Run mitmproxy as a service:

```bash
# Install pm2
npm install -g pm2

# Create start script
cat > ~/dev/personal/antigravity-proxy/start-mitm.sh << 'EOF'
#!/bin/bash
cd ~/dev/personal/antigravity-proxy
mitmdump -s mitmproxy-addon.py --listen-port 8080
EOF

chmod +x ~/dev/personal/antigravity-proxy/start-mitm.sh

# Start with pm2
pm2 start ~/dev/personal/antigravity-proxy/start-mitm.sh --name antigravity-proxy

# Make it start on boot
pm2 save
pm2 startup
```

Then always launch Antigravity with proxy settings:
```bash
alias antigravity='HTTP_PROXY=http://localhost:8080 HTTPS_PROXY=http://localhost:8080 /Applications/Antigravity.app/Contents/MacOS/Antigravity'
```

## Security Notes

- ⚠️ The mitmproxy certificate allows intercepting ALL HTTPS traffic
- Only use on your development machine
- Don't export the private key (`~/.mitmproxy/mitmproxy-ca.pem`)
- Revoke trust when done with development

## Summary

**This is the working solution.** The Node.js proxy was a good learning exercise but doesn't actually work for HTTPS content inspection.

mitmproxy:
- ✅ Industry standard for API interception
- ✅ Handles certificate generation automatically
- ✅ Can inspect and modify HTTPS traffic
- ✅ Well-documented and maintained
- ✅ **Actually works with Antigravity**

Total setup time: **~15 minutes**
