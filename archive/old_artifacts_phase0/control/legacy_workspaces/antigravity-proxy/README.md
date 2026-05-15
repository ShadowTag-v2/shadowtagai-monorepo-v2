# Antigravity Proxy

> Intercept Google Antigravity IDE API calls and use your own Gemini API token

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![mitmproxy](https://img.shields.io/badge/mitmproxy-10.x-green.svg)](https://mitmproxy.org/)

A MITM (Man-in-the-Middle) proxy that intercepts Google Antigravity IDE's API calls to `generativelanguage.googleapis.com` and replaces the authentication credentials with your own Gemini API token.

## 🎯 What This Does

```
Antigravity IDE → MITM Proxy → Google Gemini API
                    ↓
              [Replace API Key]
                    ↓
              Your API Token
```

- **Intercepts** all API calls from Antigravity to Google's Gemini API
- **Replaces** Google's API key with your own token
- **Monitors** all requests and responses for debugging
- **Controls** your own API usage and billing

## ⚡ Quick Start

```bash
# 1. Install dependencies
brew install mitmproxy
pip3 install python-dotenv

# 2. Setup SSL certificate
mitmproxy  # Press 'q' to quit
open ~/.mitmproxy/mitmproxy-ca-cert.pem
# In Keychain Access: Trust → "Always Trust"

# 3. Configure your API key
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 4. Start the proxy
mitmproxy -s mitmproxy-addon.py --listen-port 8080

# 5. Launch Antigravity (new terminal)
HTTP_PROXY=http://localhost:8080 \
HTTPS_PROXY=http://localhost:8080 \
/Applications/Antigravity.app/Contents/MacOS/Antigravity
```

## 📋 Prerequisites

- **macOS** (tested on macOS 14+, should work on Linux/Windows with minor adjustments)
- **Python 3.8+**
- **Homebrew** (for macOS)
- **Google Gemini API Key** ([Get one free](https://aistudio.google.com/apikey))

## 🚀 Installation

### Step 1: Install mitmproxy

```bash
# macOS
brew install mitmproxy

# Linux (Ubuntu/Debian)
sudo apt install mitmproxy

# Or via pip
pip3 install mitmproxy
```

### Step 2: Install Python Dependencies

```bash
pip3 install python-dotenv
```

### Step 3: Install SSL Certificate

This step is **critical** for intercepting HTTPS traffic:

```bash
# Start mitmproxy to generate certificates
mitmproxy
```

Press `q` to quit. Certificate is now at `~/.mitmproxy/mitmproxy-ca-cert.pem`

**macOS:**
```bash
# Open certificate in Keychain
open ~/.mitmproxy/mitmproxy-ca-cert.pem
```

1. Double-click "mitmproxy" certificate in Keychain Access
2. Expand "Trust" section
3. Set "When using this certificate" to **"Always Trust"**
4. Close (enter password when prompted)

**Linux:**
```bash
sudo cp ~/.mitmproxy/mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy.crt
sudo update-ca-certificates
```

**Windows:**
```powershell
# Open Certificate Manager
certmgr.msc
# Import ~/.mitmproxy/mitmproxy-ca-cert.pem to Trusted Root Certification Authorities
```

### Step 4: Configure API Key

```bash
# Clone this repository
git clone https://github.com/yourusername/antigravity-proxy.git
cd antigravity-proxy

# Copy example config
cp .env.example .env

# Edit and add your API key
nano .env  # or use any editor
```

Set your Gemini API key:
```bash
GEMINI_API_KEY=your_actual_api_key_here
```

## 📖 Usage

### Start the Proxy Server

```bash
cd antigravity-proxy

# Interactive mode (with TUI)
mitmproxy -s mitmproxy-addon.py --listen-port 8080

# Headless mode (terminal output only)
mitmdump -s mitmproxy-addon.py --listen-port 8080

# Web interface
mitmweb -s mitmproxy-addon.py --listen-port 8080
# Then open http://localhost:8081
```

### Launch Antigravity with Proxy

**Option 1: Using the launch script**
```bash
./scripts/launch-antigravity.sh
```

**Option 2: Manual launch**
```bash
HTTP_PROXY=http://localhost:8080 \
HTTPS_PROXY=http://localhost:8080 \
/Applications/Antigravity.app/Contents/MacOS/Antigravity
```

### Verify It's Working

When you use Antigravity's AI features, you should see in the proxy terminal:

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
```

## 🏗️ Architecture

This proxy uses [mitmproxy](https://mitmproxy.org/), an industry-standard MITM proxy, with a custom Python addon (`mitmproxy-addon.py`) that:

1. **Intercepts** HTTPS requests to `generativelanguage.googleapis.com`
2. **Extracts** the original API key from headers or query parameters
3. **Replaces** it with your configured API key from `.env`
4. **Forwards** the modified request to Google's servers
5. **Returns** the response to Antigravity

### Why mitmproxy?

- ✅ Industry-standard tool for API interception
- ✅ Handles SSL/TLS certificate generation automatically
- ✅ Can inspect and modify HTTPS traffic
- ✅ Well-documented and actively maintained
- ✅ Python scripting for custom logic

## 🔧 Configuration

Edit `.env` file:

```bash
# Your Google Gemini API Key (required)
GEMINI_API_KEY=your_api_key_here

# Proxy port (optional, default: 8080)
PROXY_PORT=8080
```

## 📚 Documentation

- [MITMPROXY_SETUP.md](./MITMPROXY_SETUP.md) - Complete setup guide
- [IMPORTANT_NOTES.md](./IMPORTANT_NOTES.md) - Technical limitations and alternatives
- [docs/VSCODE_SETUP.md](./docs/VSCODE_SETUP.md) - VS Code configuration

## 🔒 Security Considerations

⚠️ **IMPORTANT:** This proxy is for **local development only**.

**What this means:**
- The mitmproxy certificate allows intercepting ALL HTTPS traffic
- Only use on your personal development machine
- Never use on production systems
- Don't expose the proxy to the internet
- Revoke certificate trust when done

**API Key Security:**
- Never commit `.env` to git (already in `.gitignore`)
- Don't share your `.env` file
- Use separate API keys for development/production
- Rotate keys regularly

See [docs/SECURITY.md](./docs/SECURITY.md) for detailed security information.

## 🐛 Troubleshooting

### Certificate Not Trusted

**Symptom:** SSL/TLS errors in Antigravity

**Solution:**
1. Open Keychain Access (macOS)
2. Search for "mitmproxy"
3. Double-click certificate
4. Set Trust to "Always Trust"
5. Restart Antigravity

### No Requests Appearing

**Symptom:** Proxy shows no traffic

**Solutions:**
1. Verify environment variables:
   ```bash
   echo $HTTP_PROXY
   echo $HTTPS_PROXY
   ```
2. Check proxy is running: `lsof -ti:8080`
3. Test with curl:
   ```bash
   HTTP_PROXY=http://localhost:8080 \
   HTTPS_PROXY=http://localhost:8080 \
   curl https://generativelanguage.googleapis.com/v1beta/models
   ```

### API Key Not Replaced

**Symptom:** Proxy logs show no key replacement

**Solution:**
- Verify `.env` has correct `GEMINI_API_KEY`
- Check logs show "Replaced key in header"
- Ensure you copied `.env.example` to `.env`

See [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) for more help.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
git clone https://github.com/yourusername/antigravity-proxy.git
cd antigravity-proxy
cp .env.example .env
# Edit .env with your API key
```

### Running Tests

```bash
# Test the proxy with curl
HTTP_PROXY=http://localhost:8080 \
HTTPS_PROXY=http://localhost:8080 \
curl -v https://generativelanguage.googleapis.com/v1beta/models
```

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and personal use only. Ensure you comply with:

- [Google's Terms of Service](https://policies.google.com/terms)
- [Gemini API Terms of Service](https://ai.google.dev/gemini-api/terms)
- [Gemini API Usage Policies](https://ai.google.dev/gemini-api/docs/usage-policies)
- Your organization's security policies

The authors are not responsible for any misuse or violations.

## 📦 Alternative Implementations

### Node.js Experimental Branch

An educational Node.js implementation is available in the `nodejs-experimental` branch:

```bash
git checkout nodejs-experimental
```

**Note:** The Node.js version demonstrates proxy concepts but cannot inspect HTTPS content due to encryption limitations. Use the master branch (mitmproxy) for actual functionality.

See [nodejs-experimental branch](../../tree/nodejs-experimental) for details.

## 🙏 Acknowledgments

- [mitmproxy](https://mitmproxy.org/) - The excellent MITM proxy framework
- Google Antigravity team for building an interesting IDE
- Google Gemini team for the API

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/antigravity-proxy/issues)
- **Documentation**: See [docs/](./docs/) directory
- **Security**: See [docs/SECURITY.md](./docs/SECURITY.md)

## 🌟 Star This Project

If you find this project useful, please consider giving it a star ⭐

## 🗂️ Repository Structure

```
master (default)
├── mitmproxy-addon.py          # Working proxy solution
├── docs/                       # Documentation
├── scripts/                    # Helper scripts
└── README.md                   # This file

nodejs-experimental
├── src/                        # Node.js implementation (educational)
├── package.json               # Node.js dependencies
└── README_NODEJS.md           # Branch-specific docs
```

---

**Made with ❤️ for developers who want control over their AI API usage**
