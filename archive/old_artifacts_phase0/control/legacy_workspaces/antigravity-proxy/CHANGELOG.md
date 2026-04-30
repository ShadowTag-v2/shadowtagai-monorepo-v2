# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-20

### Added
- Initial release of Antigravity Proxy
- mitmproxy-based HTTPS interception
- Automatic API key replacement for Gemini API calls
- SSL certificate management
- Request/response logging with statistics
- Environment-based configuration via .env file
- Launch script for macOS
- Comprehensive documentation:
  - README with quick start guide
  - MITMPROXY_SETUP with detailed instructions
  - IMPORTANT_NOTES explaining technical limitations
  - Security considerations
  - Troubleshooting guide
  - VS Code setup guide
  - Architecture documentation
  - API endpoints reference
- Python addon with colored console output
- Support for both header and query parameter API keys
- Real-time request interception and modification

### Documentation
- Complete setup guide for macOS
- Linux and Windows setup instructions
- Security best practices
- Troubleshooting common issues
- Contributing guidelines
- MIT License
- Code of conduct

### Technical
- Uses mitmproxy for HTTPS MITM
- Python 3.8+ compatible
- python-dotenv for configuration
- Colored console output for better UX
- Request statistics tracking
- Error handling and logging

## [Unreleased]

### Planned Features
- Docker container support
- Automated tests
- CI/CD pipeline
- Web dashboard for monitoring
- Multiple API key support
- Request/response recording
- Rate limiting
- Windows native support
- Linux distribution packages

---

## Version History

### What Changed Between Versions

**Node.js Attempt (experimental branch)**
- Initial implementation using Node.js http-proxy
- Could handle HTTP requests
- Could not inspect HTTPS content (limitation discovered)
- Educational implementation for understanding proxy mechanics
- Moved to `nodejs-experimental` branch for reference

**mitmproxy Solution (master branch)**
- Complete rewrite using mitmproxy
- Full HTTPS content inspection capability
- Automatic SSL certificate generation
- Actually works with Antigravity
- Production-ready solution

---

## Migration Guide

### From Node.js to mitmproxy

If you were using the Node.js implementation:

1. Install mitmproxy: `brew install mitmproxy`
2. Install python-dotenv: `pip3 install python-dotenv`
3. Setup certificate: See MITMPROXY_SETUP.md
4. Use `mitmproxy-addon.py` instead of `src/server.js`
5. Same `.env` configuration works

**Key Differences:**
- Start command: `mitmproxy -s mitmproxy-addon.py` (instead of `npm start`)
- Certificate setup required (one-time)
- Actually intercepts HTTPS traffic (Node.js couldn't)

---

## Links

- [Repository](https://github.com/yourusername/antigravity-proxy)
- [Issues](https://github.com/yourusername/antigravity-proxy/issues)
- [Pull Requests](https://github.com/yourusername/antigravity-proxy/pulls)
