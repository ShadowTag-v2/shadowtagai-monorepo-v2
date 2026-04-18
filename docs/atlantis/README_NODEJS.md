# Antigravity Proxy - Node.js Experimental Branch

> ⚠️ **This is an experimental/educational branch** - For the working solution, see the `master` branch

## About This Branch

This branch contains a Node.js implementation of the proxy server. It demonstrates proxy concepts and HTTP mechanics but **cannot inspect HTTPS content** due to technical limitations.

### What This Implementation Does

✅ **Works:**


- HTTP proxy server with http-proxy library


- HTTPS CONNECT tunneling


- Multi-domain proxying


- Request logging and monitoring


- Configuration management


- Colored console output

❌ **Doesn't Work:**


- **Inspecting HTTPS request content** (headers, body, API keys)


- **Replacing API keys in encrypted traffic**


- **Actually intercepting Gemini API calls**

## Why It Doesn't Work

When Antigravity makes HTTPS requests:



1. Client sends `CONNECT generativelanguage.googleapis.com:443`


2. Proxy establishes TCP tunnel


3. Client and server perform TLS handshake **directly**


4. All traffic flows through tunnel **encrypted**

The proxy can only see the tunnel setup, not the encrypted data inside.

## Educational Value

This implementation is valuable for:


- Understanding HTTP proxy architecture


- Learning about CONNECT tunneling


- Studying request/response handling


- Exploring logging patterns


- Configuration management examples

## Installation (Educational)

```bash

# Switch to this branch

git checkout nodejs-experimental

# Install dependencies

npm install

# Configure

cp .env.example .env

# Add your GEMINI_API_KEY

# Run

npm start

```

## Architecture

### Files



- `src/server.js` - Main HTTP server with CONNECT tunneling


- `src/interceptor.js` - Request inspection (unused due to encryption)


- `src/logger.js` - Structured logging with Winston


- `src/config.js` - Environment configuration


- `src/test.js` - Test script

### Dependencies



- `http-proxy` - HTTP proxy library


- `winston` - Logging framework


- `chalk` - Terminal colors


- `dotenv` - Environment variables

## What You'll Learn

Running this implementation will teach you:



1. **HTTP Proxy Basics**: How proxies forward requests


2. **CONNECT Method**: HTTPS tunneling mechanism


3. **Node.js Networking**: Using `http`, `https`, and `net` modules


4. **Request/Response Flow**: Understanding the proxy lifecycle


5. **Encryption Limitations**: Why simple proxies can't inspect HTTPS

## Limitations

### Cannot Intercept HTTPS Content

```javascript
// What we CAN see:
CONNECT generativelanguage.googleapis.com:443

// What we CANNOT see (encrypted):
POST /v1beta/models/gemini-1.5-flash:generateContent
Headers: x-goog-api-key: ABC123...
Body: { "contents": [...] }

```

### Why Not Use This?

For actual HTTPS interception, you need:


1. Certificate generation (per domain or wildcard)


2. TLS termination at the proxy


3. Re-encryption of outbound traffic


4. Certificate trust installation

This is exactly what **mitmproxy does automatically**.

## Comparison: Node.js vs mitmproxy

| Feature | Node.js (this branch) | mitmproxy (master) |
|---------|----------------------|-------------------|
| Setup | `npm install` | Certificate install |
| HTTP Requests | ✅ Works | ✅ Works |
| HTTPS Tunneling | ✅ Works | ✅ Works |
| HTTPS Content | ❌ **Encrypted** | ✅ **Decrypted** |
| API Key Replacement | ❌ **No access** | ✅ **Full access** |
| Actually Works | ❌ **No** | ✅ **Yes** |

## For Working Solution

**Switch to master branch:**

```bash
git checkout master

```

See `MITMPROXY_SETUP.md` for the working implementation.

## Contributing

If you want to improve this Node.js implementation to actually work:

### Option 1: Full MITM Implementation

Implement certificate generation and TLS termination:


- Generate certificates on-the-fly


- Terminate TLS at proxy


- Re-encrypt outbound


- Handle certificate trust

Libraries: `node-mitmproxy`, `node-forge`, `pem`

### Option 2: Use Existing Library

Use a library that does this:

```bash
npm install http-mitm-proxy

```

Then rewrite to use it instead of basic `http-proxy`.

## Documentation (This Branch)



- `README_NODEJS.md` (this file) - Node.js branch overview


- `src/` - Source code with comments


- `docs/` - Architecture and API documentation


- `package.json` - Dependencies

## License

MIT License - Same as master branch

## Acknowledgments

This Node.js implementation was created to:


1. Understand proxy mechanics


2. Attempt a pure JavaScript solution


3. Discover the limitations of simple proxies


4. Learn why mitmproxy exists

It serves as educational reference and documents the journey to the working solution.

---

**For the working solution, use the `master` branch with mitmproxy.**
