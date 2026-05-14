# Architecture Documentation

Technical architecture and design of the Antigravity Proxy.

## Overview

The Antigravity Proxy is a transparent HTTP/HTTPS proxy that intercepts API calls from Google Antigravity IDE and replaces authentication credentials on-the-fly.

```
┌─────────────────┐
│  Antigravity    │
│      IDE        │
└────────┬────────┘
         │ HTTP/HTTPS requests
         │ (with proxy config)
         ↓
┌─────────────────┐
│   Node.js       │
│  Proxy Server   │
│                 │
│  ┌───────────┐  │
│  │Interceptor│  │ ← Replaces API key
│  └───────────┘  │
└────────┬────────┘
         │ Modified requests
         │ (with your API key)
         ↓
┌─────────────────┐
│   Google        │
│  Gemini API     │
└─────────────────┘
```

## Components

### 1. Proxy Server (`src/server.js`)

**Responsibility:** HTTP/HTTPS proxy server

**Technology:** Node.js `http` module + `http-proxy` library

**Key Features:**
- Listens on configurable port (default: 8080)
- Handles HTTP/HTTPS traffic transparently
- Tracks request timing
- Error handling and graceful shutdown
- Signal handling (SIGINT, SIGTERM)

**Flow:**
1. Receives request from Antigravity
2. Emits `proxyReq` event before forwarding
3. Forwards modified request to Google
4. Emits `proxyRes` event when response received
5. Returns response to Antigravity

### 2. Request Interceptor (`src/interceptor.js`)

**Responsibility:** Request inspection and modification

**Key Features:**
- Detects Gemini API requests
- Extracts original API key
- Replaces with configured key
- Supports both header and query parameter authentication

**Detection Logic:**
```javascript
shouldIntercept(proxyReq) {
  const host = proxyReq.getHeader('host');
  return host.includes('generativelanguage.googleapis.com');
}
```

**Replacement Logic:**
```javascript
// Header replacement
proxyReq.setHeader('x-goog-api-key', this.apiKey);

// Query parameter replacement
req.url = req.url.replace(/key=([^&]+)/, `key=${this.apiKey}`);
```

### 3. Logger (`src/logger.js`)

**Responsibility:** Structured logging and monitoring

**Technology:** Winston logging library + Chalk for colors

**Features:**
- Console output with colors
- File logging (combined + errors)
- Structured JSON logs
- Log levels (debug, info, warn, error)
- Timestamp formatting

**Log Destinations:**
```
Console (colored)  →  Terminal output
File (JSON)        →  logs/combined.log
File (JSON, errors) → logs/error.log
```

### 4. Configuration (`src/config.js`)

**Responsibility:** Environment configuration and validation

**Features:**
- Loads `.env` file
- Validates required configuration
- Provides centralized config object
- Error handling for missing values

**Validation:**
```javascript
if (!process.env.GEMINI_API_KEY) {
  console.error('API key not configured');
  process.exit(1);
}
```

## Data Flow

### Request Flow (Detailed)

```
1. Antigravity sends request
   ↓
2. Node.js server receives on port 8080
   ↓
3. http-proxy emits 'proxyReq' event
   ↓
4. Interceptor.intercept() is called
   ├→ Check if host is generativelanguage.googleapis.com
   ├→ Extract original API key
   ├→ Replace with configured key
   └→ Log replacement
   ↓
5. Modified request forwarded to Google
   ↓
6. Google processes request
   ↓
7. http-proxy emits 'proxyRes' event
   ├→ Calculate duration
   └→ Log response
   ↓
8. Response returned to Antigravity
```

### Authentication Flow

```
Original Request:
  POST /v1beta/models/gemini-1.5-flash:generateContent
  Headers:
    x-goog-api-key: AIzaSyABC123...  ← Antigravity's key
    
         ↓ Interceptor

Modified Request:
  POST /v1beta/models/gemini-1.5-flash:generateContent
  Headers:
    x-goog-api-key: AIzaSyDEF456...  ← Your key
```

## Network Architecture

### Proxy Configuration

Antigravity is launched with environment variables:

```bash
HTTP_PROXY=http://localhost:8080
HTTPS_PROXY=http://localhost:8080
NODE_TLS_REJECT_UNAUTHORIZED=0
```

### TLS/SSL Handling

**Challenge:** HTTPS traffic is encrypted

**Solution:** `NODE_TLS_REJECT_UNAUTHORIZED=0`

This tells Node.js/Electron to:
- Not verify SSL certificates
- Allow proxy to inspect HTTPS traffic
- Trust the proxy as a legitimate endpoint

**Security Trade-off:**
- ✅ Enables interception without certificate management
- ❌ Disables security features
- ⚠️ Only safe for local development

### Request Routing

```
Antigravity
    ↓
localhost:8080 (Proxy)
    ↓
generativelanguage.googleapis.com:443
```

All requests to `generativelanguage.googleapis.com` are:
1. Intercepted by proxy
2. Modified (API key replaced)
3. Forwarded to real destination

## Error Handling

### Proxy Errors

```javascript
proxy.on('error', (err, req, res) => {
  logError(err);
  
  if (!res.headersSent) {
    res.writeHead(500, {
      'Content-Type': 'application/json'
    });
    res.end(JSON.stringify({
      error: 'Proxy error',
      message: err.message
    }));
  }
});
```

### Server Errors

```javascript
server.on('error', (err) => {
  logError(err);
  process.exit(1);
});
```

### Configuration Errors

```javascript
function validateConfig() {
  if (!process.env.GEMINI_API_KEY) {
    console.error('Configuration Error');
    process.exit(1);
  }
}
```

## Performance Considerations

### Request Timing

Tracked per-request:
```javascript
const requestTimings = new Map();

// On request start
requestTimings.set(req, Date.now());

// On response
const duration = Date.now() - requestTimings.get(req);
```

### Memory Management

- Request timings cleaned up after response
- No persistent state between requests
- Logs rotated by Winston

### Throughput

The proxy adds minimal overhead:
- ~1-5ms latency for key replacement
- No buffering of request/response bodies
- Streaming responses supported

## Security Architecture

### Attack Surface

**Exposed:**
- Local port 8080 (localhost only)
- Process accepts connections from local machine

**Not Exposed:**
- Not accessible from network
- No public endpoints
- No remote access

### API Key Storage

```
.env file (600 permissions)
    ↓
Loaded by dotenv at startup
    ↓
Stored in memory (config.geminiApiKey)
    ↓
Used by Interceptor for replacement
```

**Protection:**
- File permissions limit access
- Not in git (.gitignore)
- Only partial key in logs (first 15 chars)

### SSL/TLS

**Standard Flow (Without Proxy):**
```
Antigravity → [TLS] → Google API
            ↑
        Encrypted
        Verified cert
```

**Proxy Flow:**
```
Antigravity → [TLS disabled] → Proxy → [TLS] → Google API
            ↑                        ↑
        Unverified              Encrypted
                                Verified
```

The proxy trusts Google's certificate, but Antigravity doesn't verify the proxy.

## Logging Architecture

### Log Levels

```
DEBUG: Verbose details (headers, bodies)
INFO:  Normal operations (requests, responses)
WARN:  Potential issues (4xx responses)
ERROR: Actual errors (5xx, exceptions)
```

### Log Format

**Console (Human-readable):**
```
2025-01-20 10:30:15 INFO  📥 INCOMING REQUEST
  method: 'POST'
  url: '...'
```

**File (Machine-readable):**
```json
{
  "timestamp": "2025-01-20T10:30:15.123Z",
  "level": "info",
  "message": "📥 INCOMING REQUEST",
  "method": "POST",
  "url": "..."
}
```

### Log Rotation

Handled by Winston:
- Combined logs: All messages
- Error logs: Errors only
- No automatic rotation (manual cleanup)

## Deployment Architecture

### Local Development

```
~/dev/personal/antigravity-proxy/
├── node_modules/      # Dependencies
├── src/               # Source code
├── logs/              # Runtime logs
├── .env               # Configuration
└── package.json       # Project metadata
```

### Process Management

**Manual:**
```bash
npm start              # Foreground
npm run dev            # Auto-reload
```

**Background (optional):**
```bash
nohup npm start &      # Background process
pm2 start src/server.js  # Process manager
```

## Testing Architecture

### Test Script (`src/test.js`)

Sends test request through proxy:

```javascript
http.request({
  hostname: 'localhost',
  port: config.proxyPort,
  path: 'https://generativelanguage.googleapis.com/...',
  headers: {
    'x-goog-api-key': 'fake_test_key'
  }
})
```

**Verifies:**
- Proxy is running
- Request interception works
- API key replacement occurs

## Extension Points

### Adding New Interceptors

```javascript
// src/interceptor.js
export class CustomInterceptor {
  intercept(proxyReq, req) {
    // Custom logic
  }
}
```

### Adding New Loggers

```javascript
// src/logger.js
export const logCustomEvent = (data) => {
  logger.info('Custom event', data);
};
```

### Configuration Extensions

```javascript
// src/config.js
export default {
  ...existingConfig,
  newFeature: process.env.NEW_FEATURE
};
```

## Dependencies

### Runtime Dependencies

```json
{
  "http-proxy": "^1.18.1",    // Proxy server
  "dotenv": "^16.4.5",        // Environment variables
  "winston": "^3.11.0",       // Logging
  "chalk": "^5.3.0"           // Terminal colors
}
```

### Development Dependencies

```json
{
  "nodemon": "^3.0.2"         // Auto-reload
}
```

### Why These Libraries?

- **http-proxy**: Industry standard, battle-tested
- **dotenv**: Simple, secure environment management
- **winston**: Flexible, structured logging
- **chalk**: Better UX with colored output
- **nodemon**: Developer productivity

## Future Enhancements

Potential improvements:

1. **Certificate Management**: Generate self-signed certificates for proper HTTPS
2. **Request Recording**: Save/replay requests for debugging
3. **Rate Limiting**: Protect against accidental API abuse
4. **Multi-Key Support**: Switch between multiple API keys
5. **Web Dashboard**: Monitor requests in browser
6. **Docker Support**: Containerized deployment
7. **Metrics**: Prometheus/Grafana integration

## Limitations

Current limitations:

1. **macOS only**: Launch script is macOS-specific
2. **Single API key**: Can't switch keys without restart
3. **No request filtering**: All Gemini requests intercepted
4. **No caching**: Every request hits Google's API
5. **No rate limiting**: Depends on Google's limits
6. **Local only**: Not designed for remote access

## References

- [Node.js HTTP Module](https://nodejs.org/api/http.html)
- [http-proxy Documentation](https://github.com/http-party/node-http-proxy)
- [Winston Logging](https://github.com/winstonjs/winston)
- [Gemini API Docs](https://ai.google.dev/api)
