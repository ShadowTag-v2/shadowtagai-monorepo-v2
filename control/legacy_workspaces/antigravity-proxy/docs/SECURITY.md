# Security Considerations

Important security information for Antigravity Proxy.

## ⚠️ CRITICAL WARNINGS

### 1. Local Development Only

**This proxy is designed for LOCAL DEVELOPMENT ONLY.**

DO NOT:
- ❌ Use in production environments
- ❌ Expose the proxy to the internet
- ❌ Run on shared/public networks
- ❌ Use on company networks without permission

### 2. SSL Verification Disabled

The proxy requires `NODE_TLS_REJECT_UNAUTHORIZED=0` which **disables SSL certificate verification**.

**Why this matters:**
- Your connection is vulnerable to man-in-the-middle attacks
- Only safe on trusted local networks (your computer)
- Never use this setting in production code

### 3. API Key Security

Your Gemini API key is stored in `.env` and used by the proxy.

**Protect your API key:**
- Never commit `.env` to git (already in `.gitignore`)
- Don't share your `.env` file
- Don't post logs containing your API key online
- Rotate keys regularly
- Use separate keys for testing/production

## What the Proxy Does

### Request Interception

The proxy:
1. Intercepts HTTP/HTTPS traffic
2. Reads request headers and URLs
3. Modifies authentication credentials
4. Forwards to Google's servers
5. Returns responses unchanged

### Data Access

The proxy can see:
- ✅ Request URLs
- ✅ Request/response headers
- ✅ API keys (original and replacement)
- ✅ Request/response bodies
- ✅ All data sent to Gemini API

### What It Does NOT Do

The proxy does NOT:
- ❌ Store request/response data (except logs)
- ❌ Send data anywhere except Google's API
- ❌ Modify response content
- ❌ Share your API key externally
- ❌ Track usage beyond local logs

## Log Security

### What's Logged

Logs contain:
- Request URLs (may contain query parameters)
- Partial API keys (first 15 characters)
- Response status codes
- Timestamps
- Error messages

### Log Files

```
logs/
├── combined.log    # All logs
└── error.log       # Errors only
```

**Log Security:**
- Logs are stored locally only
- Not sent anywhere
- `.gitignore` prevents committing logs
- Review logs before sharing

**Sensitive Data in Logs:**
```
# Logs show partial keys (safe):
Old Key: AIzaSyABC123***
New Key: AIzaSyDEF456***

# NOT full keys (never logged):
AIzaSyABC123456789abcdefghijk  ❌
```

## Network Security

### Local Network Only

The proxy binds to `localhost` by default:
```javascript
server.listen(config.proxyPort, () => {
  // Listening on 127.0.0.1 (localhost only)
});
```

### Firewall

macOS firewall may prompt to allow Node.js connections. This is safe for local development.

### Port Security

Default port 8080 is:
- Not exposed externally
- Only accessible from your computer
- Not forwarded through router

## Environment Variables

### Sensitive Configuration

`.env` contains:
```bash
GEMINI_API_KEY=your_secret_key_here  # SENSITIVE!
PROXY_PORT=8080                      # Not sensitive
LOG_LEVEL=info                       # Not sensitive
```

### Protection

- `.env` is in `.gitignore` (never committed)
- Only readable by you (file permissions)
- Not exposed to child processes (except proxy itself)

Check permissions:
```bash
ls -la .env
# Should show: -rw-r--r--  (readable by you)
```

Make private if needed:
```bash
chmod 600 .env
```

## Code Security

### Dependencies

All dependencies are from npm:
- `http-proxy` - Trusted, widely-used proxy library
- `dotenv` - Standard environment variable loader
- `winston` - Standard logging library
- `chalk` - Terminal colors (no network access)

### Audit

Check for vulnerabilities:
```bash
npm audit
```

Fix vulnerabilities:
```bash
npm audit fix
```

## API Key Best Practices

### Separate Keys for Development

Use different API keys for:
- ✅ Development (this proxy)
- ✅ Testing
- ✅ Production

This limits damage if a key is compromised.

### Key Rotation

Rotate keys regularly:
1. Generate new key in [Google AI Studio](https://aistudio.google.com/apikey)
2. Update `.env`
3. Delete old key in Google AI Studio
4. Restart proxy

### Monitoring Usage

Monitor API usage in [Google AI Studio](https://aistudio.google.com/):
- Check for unexpected usage
- Review rate limit consumption
- Monitor costs (if on paid tier)

### Revoke Compromised Keys

If you accidentally expose your key:
1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Delete the compromised key immediately
3. Generate a new key
4. Update `.env`

## Compliance

### Terms of Service

Ensure you comply with:
- [Google Gemini API Terms of Service](https://ai.google.dev/gemini-api/terms)
- [Google API Services User Data Policy](https://developers.google.com/terms/api-services-user-data-policy)
- Your organization's security policies

### Data Privacy

Consider what data you're sending to Gemini API:
- Code may contain sensitive information
- Prompts may contain private data
- Don't send passwords, secrets, or PII unnecessarily

### Company Policies

If using for work:
- ✅ Check if allowed to use external AI services
- ✅ Verify API usage complies with data policies
- ✅ Get approval for proxy usage
- ✅ Use company-provided API keys if required

## Threat Model

### What This Protects Against

✅ **Accidental key exposure** - Your key stays in `.env`, not hardcoded in Antigravity

### What This Does NOT Protect Against

❌ **Malicious actors on your machine** - If your computer is compromised, they can read `.env`
❌ **Network attacks** - SSL verification is disabled
❌ **Google's data usage** - Google still sees all your requests

## Safe Usage Checklist

Before using the proxy:

- [ ] Only using on your local machine
- [ ] Not on a public/shared network
- [ ] Have separate API key for development
- [ ] `.env` is not committed to git
- [ ] Understand SSL verification is disabled
- [ ] Reviewed logs for sensitive data before sharing
- [ ] Comply with Google's Terms of Service
- [ ] Have permission if using for work

## Security Updates

Keep dependencies updated:
```bash
# Check for outdated packages
npm outdated

# Update all packages
npm update

# Update package.json
npm install package@latest
```

## Reporting Security Issues

If you discover a security issue:

1. **Do not** open a public issue
2. **Do not** post details online
3. Email the maintainer privately
4. Include details and potential impact

## Additional Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [Node.js Security Best Practices](https://nodejs.org/en/docs/guides/security/)
- [npm Security](https://docs.npmjs.com/about-security-audits)
- [Google Cloud Security](https://cloud.google.com/security)

## Disclaimer

**Use at your own risk.** This tool is provided as-is for educational purposes. The authors are not responsible for:
- API key compromises
- Data breaches
- Terms of Service violations
- Security incidents
- Costs incurred from API usage

Always follow security best practices and comply with all applicable terms and policies.
