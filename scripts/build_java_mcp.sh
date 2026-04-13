#!/usr/bin/env bash
set -uo pipefail

echo "☕ Integrating googleapis/mcp-toolbox-sdk-java for JVM backend context..."
cd /Users/pikeymickey || exit 1

if [ ! -d "mcp-toolbox-sdk-java" ]; then
    git clone https://github.com/googleapis/mcp-toolbox-sdk-java.git mcp-toolbox-sdk-java
fi

cd mcp-toolbox-sdk-java
echo "⚙️ Compiling Java MCP SDK via Maven..."
./mvnw clean install -DskipTests -q

echo "✅ Java MCP Built. Ensure ~/.gemini/antigravity/mcp_config.json points to the target JAR."
