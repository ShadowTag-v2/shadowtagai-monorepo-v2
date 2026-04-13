#!/usr/bin/env bash
set -euo pipefail

echo "[BUILD] Integrating googleapis/mcp-toolbox-sdk-java for JVM backend context..."
MCP_DIR="${HOME}/mcp-toolbox-sdk-java"

if [ ! -d "$MCP_DIR" ]; then
    git clone https://github.com/googleapis/mcp-toolbox-sdk-java.git "$MCP_DIR"
fi

cd "$MCP_DIR" || exit 1

# Resolve Maven — ./mvnw doesn't ship with this repo (Risk #2)
if [ -x "./mvnw" ]; then
    MVN="./mvnw"
elif command -v mvn >/dev/null 2>&1; then
    MVN="mvn"
elif [ -x "/tmp/apache-maven-3.9.9/bin/mvn" ]; then
    MVN="/tmp/apache-maven-3.9.9/bin/mvn"
else
    echo "[FAIL] Maven not found. Install via: brew install maven"
    exit 1
fi

echo "[BUILD] Compiling Java MCP SDK via: $MVN"
$MVN clean install -DskipTests -q

JAR_PATH=$(find . -name "mcp-toolbox-sdk-java-*.jar" -path "*/target/*" | head -n 1)
if [ -z "$JAR_PATH" ]; then
    JAR_PATH=$(find . -name "*.jar" -path "*/build/libs/*" | head -n 1)
fi

if [ -z "$JAR_PATH" ]; then
    echo "[FAIL] No JAR artifact found after build."
    exit 1
fi

JAR_PATH="$(cd "$(dirname "$JAR_PATH")" && pwd)/$(basename "$JAR_PATH")"
echo "[SUCCESS] Java MCP Built at: $JAR_PATH"
echo "Export: export MCP_JAVA_SDK_JAR_PATH=\"$JAR_PATH\""
