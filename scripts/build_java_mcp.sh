#!/usr/bin/env bash
set -uo pipefail

echo "☕ Integrating googleapis/mcp-toolbox-sdk-java for JVM backend context..."
cd /Users/pikeymickey || exit 1

if [ ! -d "mcp-toolbox-sdk-java" ]; then
    git clone https://github.com/googleapis/mcp-toolbox-sdk-java.git mcp-toolbox-sdk-java
fi

cd mcp-toolbox-sdk-java

# Resolve the Maven binary — system Maven or downloaded Maven
MAVEN_BIN=""
if command -v mvn >/dev/null 2>&1; then
    MAVEN_BIN="mvn"
elif [ -x "/tmp/apache-maven-3.9.9/bin/mvn" ]; then
    MAVEN_BIN="/tmp/apache-maven-3.9.9/bin/mvn"
else
    echo "❌ Maven not found. Install via 'brew install maven' or download to /tmp/apache-maven-3.9.9/"
    exit 1
fi

echo "⚙️ Compiling Java MCP SDK via Maven ($MAVEN_BIN)..."
# -Dfmt.skip=true required because google-java-format is incompatible with JDK 26
"$MAVEN_BIN" clean install -DskipTests -Dfmt.skip=true -q

echo "✅ Java MCP Built. Ensure ~/.gemini/antigravity/mcp_config.json points to the target JAR."
echo "   JAR location: $(ls /Users/pikeymickey/mcp-toolbox-sdk-java/target/mcp-toolbox-sdk-java-*-SNAPSHOT.jar 2>/dev/null | head -1)"
