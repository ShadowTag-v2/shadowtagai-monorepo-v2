# Troubleshooting Guide

Common issues and solutions for Antigravity Proxy.

## Installation Issues

### Node.js Not Found

**Error:**
```
command not found: node
```

**Solution:**
```bash
# Install Node.js via Homebrew
brew install node

# Verify installation
node --version
npm --version
```

### npm install fails

**Error:**
```
npm ERR! code EACCES
npm ERR! permission denied
```

**Solution:**
```bash
# Fix npm permissions
sudo chown -R $(whoami) ~/.npm
sudo chown -R $(whoami) /usr/local/lib/node_modules

# Try again
npm install
```

## Configuration Issues

### API Key Not Configured

**Error:**
```
❌ Configuration Error:
   - GEMINI_API_KEY is not configured. Please set it in .env file
```

**Solution:**
1. Copy example file: `cp .env.example .env`
2. Edit `.env`: `nano .env`
3. Set your API key: `GEMINI_API_KEY=your_actual_key_here`
4. Make sure you replaced `your_api_key_here` with real key

### Invalid API Key

**Symptom:** Proxy starts but requests fail with 401 Unauthorized

**Solution:**
1. Verify your API key is correct
2. Get a new key from [Google AI Studio](https://aistudio.google.com/apikey)
3. Check for extra spaces or newlines in `.env`

```bash
# Test your API key directly
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_API_KEY"
```

## Runtime Issues

### Port Already in Use

**Error:**
```
Error: listen EADDRINUSE: address already in use :::8080
```

**Solution:**

**Option 1:** Kill the process using the port
```bash
# Find process using port 8080
lsof -ti:8080

# Kill it
kill -9 $(lsof -ti:8080)
```

**Option 2:** Use a different port
```bash
# Edit .env
PROXY_PORT=8081

# Update launch script
./scripts/launch-antigravity.sh
```

### Proxy Not Intercepting Requests

**Symptom:** Proxy runs but doesn't show any requests

**Possible Causes:**

1. **Antigravity not using proxy**
   ```bash
   # Make sure you launch with the script
   ./scripts/launch-antigravity.sh
   
   # Or set environment variables manually
   HTTP_PROXY=http://localhost:8080 \
   HTTPS_PROXY=http://localhost:8080 \
   NODE_TLS_REJECT_UNAUTHORIZED=0 \
   /Applications/Antigravity.app/Contents/MacOS/Antigravity
   ```

2. **Wrong proxy URL**
   - Check `PROXY_PORT` in `.env` matches the port in launch script
   - Default is 8080

3. **Antigravity using different endpoints**
   - Check proxy logs for any requests
   - Add debug logging: `LOG_LEVEL=debug` in `.env`

### SSL/Certificate Errors

**Error:**
```
Error: unable to verify the first certificate
```

**Solution:**
This is normal! The launch script sets `NODE_TLS_REJECT_UNAUTHORIZED=0` to bypass this.

If still having issues:
```bash
# Verify environment variable is set
echo $NODE_TLS_REJECT_UNAUTHORIZED  # Should be 0

# Try launching manually with explicit setting
NODE_TLS_REJECT_UNAUTHORIZED=0 \
HTTP_PROXY=http://localhost:8080 \
HTTPS_PROXY=http://localhost:8080 \
/Applications/Antigravity.app/Contents/MacOS/Antigravity
```

### Antigravity Not Found

**Error:**
```
❌ Antigravity not found at: /Applications/Antigravity.app/Contents/MacOS/Antigravity
```

**Solution:**

1. **Find Antigravity location:**
   ```bash
   # Search for Antigravity
   mdfind -name "Antigravity"
   
   # Or check Applications
   ls -la /Applications/ | grep -i antigravity
   ```

2. **Set correct path in .env:**
   ```bash
   ANTIGRAVITY_PATH=/path/to/Antigravity.app/Contents/MacOS/Antigravity
   ```

3. **Or install Antigravity** from Google

## API Issues

### 401 Unauthorized

**Symptom:** Requests show 401 in proxy logs

**Solution:**
- Verify API key in `.env` is correct
- Check if API key has expired
- Get new API key from [Google AI Studio](https://aistudio.google.com/apikey)

### 429 Too Many Requests

**Symptom:** Requests fail with "Resource exhausted"

**Solution:**
You've hit rate limits. Free tier limits:
- 15 requests per minute
- 1,500 requests per day

Wait a few minutes or upgrade to paid tier.

### 500 Internal Server Error

**Symptom:** Google's API returns 500

**Solution:**
- This is a Google API issue, not the proxy
- Wait and retry
- Check [Google Cloud Status](https://status.cloud.google.com/)

## Logging Issues

### No Logs Appearing

**Solution:**
```bash
# Set debug level
LOG_LEVEL=debug

# Check logs directory
ls -la logs/

# Tail logs in real-time
tail -f logs/combined.log
```

### Too Verbose Logging

**Solution:**
```bash
# Reduce log level
LOG_LEVEL=warn  # or 'error'
```

## Performance Issues

### Slow Responses

**Possible Causes:**

1. **Network latency** - Proxy adds minimal overhead
2. **Google API is slow** - Check direct API performance
3. **Large requests** - Token counting and generation takes time

**Debug:**
```bash
# Compare direct vs proxy
time curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_KEY"

time curl -x http://localhost:8080 \
  "https://generativelanguage.googleapis.com/v1beta/models?key=fake_key"
```

### Memory Issues

**Symptom:** Node.js process using too much memory

**Solution:**
```bash
# Restart proxy periodically
npm start

# Monitor memory
top -pid $(pgrep -f "node src/server.js")
```

## Testing Issues

### Test Script Fails

**Error:**
```
❌ Test failed: connect ECONNREFUSED 127.0.0.1:8080
```

**Solution:**
Make sure proxy is running:
```bash
# Terminal 1: Start proxy
npm start

# Terminal 2: Run test
npm test
```

### Test Shows Wrong API Key

**Symptom:** Test logs show your real API key, not test key

**Expected:** This is correct! The proxy should replace test key with your real key.

## Debug Mode

Enable detailed logging:

```bash
# Edit .env
LOG_LEVEL=debug

# Restart proxy
npm start
```

Debug output includes:
- Full request URLs
- All headers
- Request/response bodies (preview)
- Timing information
- Error stack traces

## Still Having Issues?

1. **Check logs:**
   ```bash
   cat logs/error.log
   tail -50 logs/combined.log
   ```

2. **Test components individually:**
   ```bash
   # Test API key directly
   curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_KEY"
   
   # Test proxy
   npm test
   
   # Test Antigravity launch
   ./scripts/launch-antigravity.sh
   ```

3. **Clean reinstall:**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Check versions:**
   ```bash
   node --version  # Should be 18+
   npm --version
   cat package.json | grep version
   ```

## Getting Help

If you're still stuck:

1. Review all documentation in `/docs`
2. Check logs in `/logs` directory
3. Search for similar issues in proxy logs
4. Verify each component works independently

## Common Error Messages

### "Cannot find module"
```bash
npm install  # Reinstall dependencies
```

### "EPERM: operation not permitted"
```bash
sudo npm start  # Run with elevated permissions (not recommended)
# Or fix permissions on logs directory
chmod -R 755 logs/
```

### "Unexpected token"
```bash
# Check Node.js version
node --version  # Must be 18+

# Update if needed
brew upgrade node
```
