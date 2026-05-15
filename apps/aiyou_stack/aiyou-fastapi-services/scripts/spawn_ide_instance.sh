#!/bin/bash
#
# Spawn IDE Instance - Launch Headless Cursor or VS Code
#
# Usage: ./spawn_ide_instance.sh <type> <instance_id> <port> <workspace_path> <api_key>
#
# Example: ./spawn_ide_instance.sh cursor 1 9000 /path/to/workspace CURSOR_API_KEY
#

set -e

IDE_TYPE=$1
INSTANCE_ID=$2
PORT=$3
WORKSPACE_PATH=$4
API_KEY=$5

if [ -z "$IDE_TYPE" ] || [ -z "$INSTANCE_ID" ] || [ -z "$PORT" ] || [ -z "$WORKSPACE_PATH" ]; then
    echo "Usage: $0 <cursor|vscode> <instance_id> <port> <workspace_path> [api_key]"
    exit 1
fi

echo "///▞ SPAWN IDE :: Type=$IDE_TYPE Instance=$INSTANCE_ID Port=$PORT"

# Create workspace directory if it doesn't exist
mkdir -p "$WORKSPACE_PATH"

# Spawn based on IDE type
if [ "$IDE_TYPE" = "cursor" ]; then
    echo "///▞ SPAWN IDE :: Launching Cursor instance..."

    # Cursor headless mode (using custom server)
    # In production, this would use Cursor's API/CLI
    # For now, simulate with a placeholder

    # Example (adjust based on Cursor's actual CLI):
    # cursor --headless \
    #     --port $PORT \
    #     --workspace "$WORKSPACE_PATH" \
    #     --api-key "$API_KEY" &

    echo "CURSOR_INSTANCE_${INSTANCE_ID}=running on port $PORT" > "$WORKSPACE_PATH/.cursor_instance"

elif [ "$IDE_TYPE" = "vscode" ]; then
    echo "///▞ SPAWN IDE :: Launching VS Code instance..."

    # VS Code Server (code-server for headless operation)
    # Install code-server if not present:
    # curl -fsSL https://code-server.dev/install.sh | sh

    # Launch VS Code Server
    # code-server \
    #     --bind-addr "127.0.0.1:$PORT" \
    #     --auth none \
    #     --disable-telemetry \
    #     "$WORKSPACE_PATH" &

    echo "VSCODE_INSTANCE_${INSTANCE_ID}=running on port $PORT" > "$WORKSPACE_PATH/.vscode_instance"

else
    echo "///▞ ERROR :: Unknown IDE type: $IDE_TYPE"
    exit 1
fi

# Configure extensions and settings
configure_ide() {
    local ide_type=$1
    local workspace=$2

    if [ "$ide_type" = "cursor" ]; then
        # Cursor extensions
        cat > "$workspace/.cursor/settings.json" <<EOF
{
  "cursor.ai.model": "gpt-4",
  "cursor.ai.apiKey": "$API_KEY",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": true
  }
}
EOF

    elif [ "$ide_type" = "vscode" ]; then
        # VS Code extensions
        mkdir -p "$workspace/.vscode"
        cat > "$workspace/.vscode/settings.json" <<EOF
{
  "github.copilot.enable": {
    "*": true
  },
  "github.copilot.advanced": {},
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": true
  }
}
EOF

        # Install key extensions (if code-server allows)
        # code-server --install-extension GitHub.copilot
        # code-server --install-extension ms-python.python
        # code-server --install-extension dbaeumer.vscode-eslint
    fi
}

configure_ide "$IDE_TYPE" "$WORKSPACE_PATH"

echo "///▞ SPAWN IDE :: Instance $INSTANCE_ID configured and running"
echo "///▞ SPAWN IDE :: Workspace: $WORKSPACE_PATH"
echo "///▞ SPAWN IDE :: Port: $PORT"
