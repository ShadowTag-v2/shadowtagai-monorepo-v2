# Contributing to Antigravity Proxy

First off, thank you for considering contributing to Antigravity Proxy! It's people like you that make this tool better for everyone.

## Code of Conduct

This project and everyone participating in it is governed by common sense and mutual respect. Please be professional and courteous.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps which reproduce the problem**
- **Provide specific examples** (command output, logs, screenshots)
- **Describe the behavior you observed** and what behavior you expected
- **Include your environment details** (OS, Python version, mitmproxy version)

**Bug Report Template:**
```markdown
## Description
[Clear description of the bug]

## Steps to Reproduce
1. Start proxy with `mitmproxy -s mitmproxy-addon.py`
2. Launch Antigravity
3. [Additional steps...]

## Expected Behavior
[What you expected to happen]

## Actual Behavior
[What actually happened]

## Environment
- OS: macOS 14.2
- Python: 3.11.0
- mitmproxy: 10.1.0
- Antigravity: 1.0.0

## Logs
[Paste relevant logs]
```

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- **Clear and descriptive title**
- **Detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **Provide examples** of how it would work

### Pull Requests

1. **Fork the repo** and create your branch from `master`
2. **Make your changes** with clear commit messages
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Submit a pull request**

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/antigravity-proxy.git
cd antigravity-proxy

# Install dependencies
brew install mitmproxy  # or your OS equivalent
pip3 install python-dotenv

# Setup certificate
mitmproxy  # Press 'q' to quit
open ~/.mitmproxy/mitmproxy-ca-cert.pem
# Trust the certificate in Keychain

# Configure
cp .env.example .env
# Add your test API key
```

## Development Guidelines

### Python Code Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small

**Example:**
```python
def replace_api_key(request: http.HTTPFlow, new_key: str) -> bool:
    """
    Replace API key in request headers.
    
    Args:
        request: The HTTP flow to modify
        new_key: The new API key to use
        
    Returns:
        True if key was replaced, False otherwise
    """
    if "x-goog-api-key" in request.headers:
        request.headers["x-goog-api-key"] = new_key
        return True
    return False
```

### Documentation

- Update README.md for user-facing changes
- Update relevant docs/ files for technical changes
- Add comments for complex logic
- Keep examples up-to-date

### Commit Messages

Use clear commit messages:

**Good:**
```
Add support for multiple API keys
Fix certificate trust issue on Linux
Update README with Windows instructions
```

**Bad:**
```
Update stuff
Fix bug
Changes
```

Follow conventional commits format when possible:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Code style changes (formatting, etc)
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

### Testing

Before submitting a PR:

1. **Test basic functionality:**
   ```bash
   # Start proxy
   mitmproxy -s mitmproxy-addon.py
   
   # Test with curl
   HTTP_PROXY=http://localhost:8080 \
   HTTPS_PROXY=http://localhost:8080 \
   curl https://generativelanguage.googleapis.com/v1beta/models
   ```

2. **Test with Antigravity:**
   - Launch Antigravity with proxy
   - Make AI requests
   - Verify key replacement in logs

3. **Test edge cases:**
   - Invalid API keys
   - Network errors
   - Large requests/responses

## Project Structure

```
antigravity-proxy/
├── mitmproxy-addon.py      # Main proxy logic
├── .env.example            # Config template
├── scripts/
│   └── launch-antigravity.sh  # Launch helper
├── docs/
│   ├── MITMPROXY_SETUP.md     # Setup guide
│   ├── ARCHITECTURE.md        # Technical docs
│   ├── SECURITY.md            # Security info
│   └── TROUBLESHOOTING.md     # Common issues
└── README.md               # Main documentation
```

## Areas for Contribution

### High Priority

- [ ] Windows support and testing
- [ ] Linux distribution testing
- [ ] Automated tests
- [ ] Docker container
- [ ] CI/CD pipeline

### Medium Priority

- [ ] Web dashboard for monitoring
- [ ] Request/response recording
- [ ] Multiple API key support
- [ ] Rate limiting
- [ ] Metrics/statistics

### Documentation

- [ ] More troubleshooting scenarios
- [ ] Video tutorials
- [ ] Architecture diagrams
- [ ] API endpoint documentation
- [ ] Translation to other languages

### Nice to Have

- [ ] GUI application
- [ ] Browser extension
- [ ] Configuration wizard
- [ ] Log analysis tools

## Questions?

Feel free to:
- Open an issue for discussion
- Ask in pull request comments
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
