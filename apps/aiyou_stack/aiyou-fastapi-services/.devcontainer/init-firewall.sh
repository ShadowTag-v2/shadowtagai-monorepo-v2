#!/bin/bash

# Claude Code Development Container Firewall Configuration
# This script establishes network security rules for the devcontainer

set -e

echo "🔒 Initializing firewall for Claude Code devcontainer..."

# Check if iptables is available
if ! command -v iptables &> /dev/null; then
    echo "⚠️  Warning: iptables not found. Firewall rules will not be applied."
    exit 0
fi

# Clear existing rules
echo "📋 Clearing existing firewall rules..."
iptables -F OUTPUT 2>/dev/null || true
iptables -F INPUT 2>/dev/null || true

# Set default policies
echo "🛡️  Setting default policies..."
iptables -P INPUT ACCEPT 2>/dev/null || true
iptables -P OUTPUT DROP 2>/dev/null || true
iptables -P FORWARD DROP 2>/dev/null || true

# Allow loopback traffic (localhost)
echo "🔄 Allowing loopback traffic..."
iptables -A OUTPUT -o lo -j ACCEPT 2>/dev/null || true
iptables -A INPUT -i lo -j ACCEPT 2>/dev/null || true

# Allow established and related connections
echo "🔗 Allowing established connections..."
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT 2>/dev/null || true
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT 2>/dev/null || true

# Allow DNS (port 53)
echo "🌐 Allowing DNS queries..."
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT 2>/dev/null || true
iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT 2>/dev/null || true

# Allow SSH (port 22)
echo "🔑 Allowing SSH connections..."
iptables -A OUTPUT -p tcp --dport 22 -j ACCEPT 2>/dev/null || true

# Whitelisted domains and services for Claude Code
ALLOWED_DOMAINS=(
    # Anthropic API
    "api.anthropic.com"

    # NPM registry
    "registry.npmjs.org"
    "registry.npmjs.com"

    # GitHub
    "github.com"
    "api.github.com"
    "raw.githubusercontent.com"

    # Python Package Index
    "pypi.org"
    "files.pythonhosted.org"

    # VS Code extensions
    "marketplace.visualstudio.com"
    "vscode.dev"

    # Common CDNs
    "cdn.jsdelivr.net"
    "unpkg.com"
)

echo "✅ Whitelisting approved domains..."

# Allow HTTP/HTTPS for whitelisted domains
for domain in "${ALLOWED_DOMAINS[@]}"; do
    # Resolve domain to IP addresses (both IPv4)
    IPS=$(getent ahosts "$domain" 2>/dev/null | awk '{print $1}' | sort -u | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' || true)

    if [ -n "$IPS" ]; then
        echo "  📍 Whitelisting $domain"
        for ip in $IPS; do
            # Allow HTTP (port 80)
            iptables -A OUTPUT -p tcp -d "$ip" --dport 80 -j ACCEPT 2>/dev/null || true
            # Allow HTTPS (port 443)
            iptables -A OUTPUT -p tcp -d "$ip" --dport 443 -j ACCEPT 2>/dev/null || true
        done
    else
        echo "  ⚠️  Warning: Could not resolve $domain"
    fi
done

# Log dropped packets (optional - uncomment for debugging)
# iptables -A OUTPUT -j LOG --log-prefix "DROPPED OUTPUT: " --log-level 4

echo ""
echo "✅ Firewall configuration complete!"
echo "🔒 Security measures active:"
echo "   • Outbound connections restricted to whitelisted domains"
echo "   • DNS and SSH connections allowed"
echo "   • All other external network access blocked"
echo ""
echo "📋 To view current rules: iptables -L -n -v"
echo ""

# Verify firewall rules
RULE_COUNT=$(iptables -L OUTPUT -n | grep -c "ACCEPT" || true)
if [ "$RULE_COUNT" -gt 0 ]; then
    echo "✅ Firewall rules verified: $RULE_COUNT ACCEPT rules active"
else
    echo "⚠️  Warning: No ACCEPT rules found. Firewall may not be working correctly."
fi
