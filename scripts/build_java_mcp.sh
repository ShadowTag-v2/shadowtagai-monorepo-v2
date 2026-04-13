#!/usr/bin/env bash
set -euo pipefail

echo "[BUILD] Integrating googleapis/mcp-toolbox-sdk-java for JVM backend context..."
MCP_DIR="${HOME}/mcp-toolbox-sdk-java"

if [ ! -d "$MCP_DIR" ]; then
    git clone https://github.com/googleapis/mcp-toolbox-sdk-java.git "$MCP_DIR"
fi

cd "$MCP_DIR" || exit 1
echo "[BUILD] Compiling Java MCP SDK via Maven..."

# Use system mvn (./mvnw not present in this repo — tracked as RISK_REGISTER #2)
if command -v mvn &>/dev/null; then
    mvn clean install -DskipTests -q
elif [ -x "/tmp/apache-maven-3.9.9/bin/mvn" ]; then
    /tmp/apache-maven-3.9.9/bin/mvn clean install -DskipTests -q
else
    echo "[ERROR] Maven not found. Install via: brew install maven"
    exit 1
fi

JAR_PATH=$(find target -name "mcp-toolbox-sdk-java-*.jar" | head -n 1)
echo "[SUCCESS] Java MCP Built at: $JAR_PATH"
