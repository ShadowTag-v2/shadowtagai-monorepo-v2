#!/usr/bin/env bash
# ==============================================================================
# ANTIGRAVITY OS: JAVA MCP SDK INTEGRATION BUILDER
# ==============================================================================
set -e

echo "🚀 Integrating googleapis/mcp-toolbox-sdk-java for JVM backend context..."
cd /Users/pikeymickey

if [ ! -d "mcp-toolbox-sdk-java" ]; then
    git clone https://github.com/googleapis/mcp-toolbox-sdk-java.git mcp-toolbox-sdk-java
fi

cd mcp-toolbox-sdk-java
echo "☕ Compiling Java MCP SDK..."
./mvnw clean install -DskipTests -q

echo "✅ Java MCP Built. Configured in ~/.gemini/antigravity/mcp_config.json."
