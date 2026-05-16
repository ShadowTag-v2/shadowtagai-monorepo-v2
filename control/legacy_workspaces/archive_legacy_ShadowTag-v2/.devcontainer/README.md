# Development Container Setup

This directory contains the devcontainer configuration for the Claude Agent SDK project.

## What's Included

This devcontainer provides a secure, isolated development environment with:

- **Node.js 20**: Latest LTS version for JavaScript/TypeScript development
- **Python 3**: For Python-based Claude Agent SDK usage
- **Security**: Custom firewall restricting network access to trusted services only
- **Developer Tools**: ZSH with Oh My Zsh, fzf, ripgrep, git, and more
- **Persistent Storage**: Command history and package caches preserved between sessions
- **Pre-configured Extensions**: ESLint, Prettier, Python tools, GitLens, and more

## Quick Start

### Prerequisites

1. Install [Visual Studio Code](https://code.visualstudio.com/)
2. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
3. Install [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Opening the Project in a Container

1. Open this repository in VS Code
2. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
3. Select "Dev Containers: Reopen in Container"
4. Wait for the container to build (first time only, ~5-10 minutes)

VS Code will automatically:
- Build the Docker container
- Install all dependencies (`npm install`)
- Configure the firewall rules
- Set up your development environment

## Files Overview

- **`devcontainer.json`**: Container configuration, VS Code settings, and extensions
- **`Dockerfile`**: Container image definition with all required tools
- **`init-firewall.sh`**: Security script that restricts network access

## Security Features

The devcontainer implements strict network security:

### ✅ Allowed Connections

- Anthropic API (api.anthropic.com)
- NPM Registry (registry.npmjs.org)
- GitHub (github.com, api.github.com)
- Python Package Index (pypi.org)
- VS Code Marketplace
- Common CDNs (jsdelivr, unpkg)
- DNS queries (port 53)
- SSH connections (port 22)

### ❌ Blocked Connections

- All other outbound network traffic
- Prevents data exfiltration to untrusted domains
- Default-deny firewall policy

## Running Claude Code Without Prompts

The container's security measures allow you to run Claude Code in unattended mode:

```bash
claude --dangerously-skip-permissions
```

⚠️ **Warning**: Only use this flag in trusted repositories. The devcontainer cannot prevent malicious code from accessing Claude Code credentials or data within the container.

## Customization

### Adding Whitelisted Domains

Edit `.devcontainer/init-firewall.sh` and add domains to the `ALLOWED_DOMAINS` array:

```bash
ALLOWED_DOMAINS=(
    # ... existing domains ...
    "your-domain.com"
)
```

### Adding VS Code Extensions

Edit `.devcontainer/devcontainer.json` in the `customizations.vscode.extensions` array:

```json
"extensions": [
    "publisher.extension-name"
]
```

### Installing Additional Packages

**Node.js packages**: Add to `package.json` and rebuild the container

**Python packages**: Edit the `Dockerfile` and add to the `pip3 install` command

**System packages**: Edit the `Dockerfile` and add to the `apt-get install` command

## Troubleshooting

### Firewall Issues

View current firewall rules:
```bash
iptables -L -n -v
```

Manually initialize firewall:
```bash
bash /usr/local/bin/init-firewall.sh
```

### Container Won't Start

1. Check Docker is running
2. Rebuild the container: `Cmd+Shift+P` → "Dev Containers: Rebuild Container"
3. Check Docker logs for errors

### Network Connection Blocked

If a legitimate service is blocked:
1. Add the domain to `ALLOWED_DOMAINS` in `init-firewall.sh`
2. Rebuild the container

## Resources

- [VS Code Dev Containers Documentation](https://code.visualstudio.com/docs/devcontainers/containers)
- [Claude Agent SDK Documentation](https://docs.claude.com/en/api/agent-sdk/overview)
- [Docker Documentation](https://docs.docker.com/)

## License

This devcontainer configuration is based on the [Claude Code reference implementation](https://github.com/anthropics/claude-code/tree/main/.devcontainer).
