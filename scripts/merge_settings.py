import json

ws_settings_path = "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.vscode/settings.json"
global_settings_path = "/Users/pikeymickey/Library/Application Support/Antigravity/User/settings.json"
default_interpreter_path = "${workspaceFolder}/.venv"

with open(ws_settings_path, encoding="utf-8") as f:
    ws_data = json.load(f)

# global settings had a trailing comma before closing brace, so we might need a messy load or parse
try:
    with open(global_settings_path, encoding="utf-8") as f:
        content = f.read()
        # strip trailing comma before right brace
        content = content.replace(",\n}", "\n}")
        global_data = json.loads(content)
except Exception as e:
    print(f"Failed to read global: {e}")
    global_data = {}

# Merge global into ws (ws takes precedence if conflict)
for k, v in global_data.items():
    if k not in ws_data:
        ws_data[k] = v

# specific cleanup overrides
if "python.defaultInterpreterPath" in ws_data:
    ws_data["python.defaultInterpreterPath"] = default_interpreter_path

with open(ws_settings_path, "w", encoding="utf-8") as f:
    json.dump(ws_data, f, indent=2)

with open(global_settings_path, "w", encoding="utf-8") as f:
    json.dump({}, f, indent=2)

print("Merged successfully.")
