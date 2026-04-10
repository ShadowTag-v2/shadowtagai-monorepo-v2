# Important Notes & Limitations

## Current Implementation Status

### ✅ What Works

1. **HTTP Proxy** - Correctly forwards HTTP requests
2. **HTTPS CONNECT Tunneling** - Establishes HTTPS tunnels for secure connections
3. **Multi-Domain Support** - Can proxy requests to any domain (not just Gemini API)
4. **API Key Replacement** - Replaces keys in headers and query parameters for Gemini API

### ⚠️ Current Limitation: HTTPS Content Inspection

**The proxy currently CANNOT inspect/modify HTTPS request content** after the CONNECT tunnel is established.

#### Why This Happens

When Antigravity makes an HTTPS request:

1. **CONNECT Request**: Browser sends `CONNECT generativelanguage.googleapis.com:443`
2. **Tunnel Created**: Proxy establishes a TCP tunnel between client and server
3. **TLS Handshake**: Client and server negotiate encryption **directly**
4. **Encrypted Traffic**: All subsequent data flows through the tunnel **encrypted**

The proxy only sees:
- ✅ Initial CONNECT request (domain + port)
- ❌ NOT the actual HTTPS request content (headers, body, URL path)

```
Client → [CONNECT tunnel] → Proxy → [CONNECT tunnel] → Server
         └─ Encrypted TLS traffic flows through ─┘
                    (proxy can't see inside)
```

#### What This Means

The proxy **cannot replace API keys in HTTPS requests** using this simple approach because:
- API keys are inside the encrypted TLS tunnel
- Proxy would need to perform TLS man-in-the-middle (MITM)
- MITM requires certificate generation and installation

### 🔧 Solutions

#### Option 1: Full MITM Proxy (Complex but Complete)

Implement proper MITM with certificate generation:

**Pros:**
- Can inspect and modify HTTPS traffic
- Can replace API keys in real-time
- Works transparently

**Cons:**
- Complex implementation (need to generate certificates on-the-fly)
- Requires installing root CA certificate in macOS Keychain
- Security implications (disables certificate verification)

**Implementation:**
Use existing MITM libraries:
- `mitmproxy` (Python - what we initially considered)
- `http-mitm-proxy` (Node.js)
- `node-mitmproxy` (Node.js)

#### Option 2: VS Code Extension (Simpler, More Direct)

Create a VS Code extension that hooks into Antigravity:

**Pros:**
- Direct access to API calls before encryption
- No certificate management needed
- Clean integration

**Cons:**
- Need to understand Antigravity's extension API
- May need to reverse-engineer their API calling mechanism
- Extension might break with Antigravity updates

#### Option 3: Binary Patching (Not Recommended)

Modify Antigravity's compiled code to change hardcoded API endpoints or keys.

**Pros:**
- Direct solution

**Cons:**
- Very fragile
- Breaks with updates
- Legally questionable
- Difficult to maintain

#### Option 4: Use Python mitmproxy (What We Should Have Done)

Go back to the original plan with `mitmproxy`:

**Setup:**
```bash
# Install mitmproxy
brew install mitmproxy

# Start with addon script
mitmproxy -s ~/dev/personal/antigravity-proxy/mitm-addon.py

# Install certificate
open ~/.mitmproxy/mitmproxy-ca-cert.pem
# Add to Keychain and trust

# Launch Antigravity
HTTP_PROXY=http://localhost:8080 \
HTTPS_PROXY=http://localhost:8080 \
/Applications/Antigravity.app/Contents/MacOS/Antigravity
```

**Python addon script:**
```python
from mitmproxy import http

YOUR_API_KEY = "your_key_here"

def request(flow: http.HTTPFlow) -> None:
    if "generativelanguage.googleapis.com" in flow.request.pretty_host:
        # Replace API key
        if "x-goog-api-key" in flow.request.headers:
            flow.request.headers["x-goog-api-key"] = YOUR_API_KEY
        
        # Replace in URL
        if "key=" in flow.request.url:
            import re
            flow.request.url = re.sub(r'key=[^&]+', f'key={YOUR_API_KEY}', flow.request.url)
```

### 📊 Comparison

| Approach | Complexity | Effectiveness | Maintenance |
|----------|-----------|---------------|-------------|
| Current Node.js | Low | ❌ Doesn't work for HTTPS | Easy |
| Node.js MITM | Medium | ✅ Works | Medium |
| mitmproxy | Low | ✅ Works | Easy |
| VS Code Extension | High | ✅ Works | Hard |
| Binary Patching | Very High | ⚠️ Fragile | Very Hard |

### 🎯 Recommendation

**Use `mitmproxy`** - It's the industry-standard solution for exactly this use case:

1. **Proven**: Used by thousands of developers for API interception
2. **Simple**: Just install certificate and run
3. **Powerful**: Full Python scripting for request/response modification
4. **Well-Documented**: Extensive docs and examples
5. **Maintained**: Active open-source project

### 🚀 Next Steps

If you want this to actually work, I recommend:

1. **Switch to mitmproxy** (30 minutes setup)
2. Or **implement full MITM in Node.js** using `node-mitmproxy` library (2-4 hours)
3. Or **create a VS Code extension** (1-2 days, requires reverse engineering)

Let me know which direction you want to go!

## Current Status

The current Node.js proxy:
- ✅ Demonstrates the concept
- ✅ Shows request flow and logging
- ✅ Works for HTTP requests
- ❌ **Does NOT work for HTTPS content inspection**
- ❌ **Cannot replace API keys in encrypted traffic**

This is essentially a learning/demonstration project that would need significant enhancement to actually work with Antigravity's HTTPS API calls.
