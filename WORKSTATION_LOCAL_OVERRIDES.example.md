# WORKSTATION_LOCAL_OVERRIDES — v8.2c (Example)

> This file contains machine-local paths and secrets. Use env vars in production.
> Do NOT commit real secrets. This is a template.

## PEM Keys
```
SHADOWTAG_PEM=/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem
EHANC69_PEM=/Users/pikeymickey/Downloads/antigravity-manager.2026-03-13.private-key.pem
```

## OAuth Client Secret
```
GOOGLE_CLIENT_SECRET_PATH=/Users/pikeymickey/Downloads/client_secret_767252945109-g8e1bdmvl4u2ff4mkbvhcsbbduh6kv7v.apps.googleusercontent.com.json
```

## Java
```
JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-26.jdk/Contents/Home
MAVEN_BIN=/tmp/apache-maven-3.9.9/bin/mvn  # or 'mvn' if brew-installed
MCP_JAR=/Users/pikeymickey/mcp-toolbox-sdk-java/target/mcp-toolbox-sdk-java-0.2.1-SNAPSHOT.jar
```

## .NET
```
DOTNET_BIN=/usr/local/share/dotnet/dotnet
DOTNET_VERSION=11.0.100-preview.2.26159.112
```

## Python
```
UV_BIN=$HOME/.cargo/bin/uv
PYTHON_VERSION=3.14.3
```

## Obsidian
```
OBSIDIAN_VAULT=~/Documents/Obsidian/ShadowTag-Vault
```

## Antigravity Brain
```
BRAIN_DIR=/Users/pikeymickey/.gemini/antigravity/brain
```

## OrbStack Docker
```
ORBSTACK_DOCKER=$HOME/.orbstack/bin/docker
# MUST prepend PATH explicitly: PATH=$HOME/.orbstack/bin:$PATH
```

## NotebookLM
```
NOTEBOOKLM_MASTER_BRAIN=c493b409-3955-418f-a993-755c38dc8e7f
NOTEBOOKLM_AUTH=storage_state.json
```
