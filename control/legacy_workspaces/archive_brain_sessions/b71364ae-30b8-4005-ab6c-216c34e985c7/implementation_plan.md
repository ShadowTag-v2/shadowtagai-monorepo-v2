# Goal Description

1. **Fix Python Interpreter Path**: The VSCode Native locator `python` command is failing because macOS uses `python3` universally now and the `python` alias or pyenv setup is missing from the environment. We will configure the workspace `.vscode/settings.json` to explicitly point to the working `python3` binary.
2. **Fix ModuleNotFoundError**: The script `god_mode_admin.py` is failing to import `libs.steel.sdk` because the `ShadowTag-v2` root directory is not in the Python path when executed directly from the `scripts` folder without an active environment. We will inject the root directory into `sys.path` dynamically.
3. **Build "Luminina" Website**: Following the transcript and video instructions provided, we will scaffold a stunning, futuristic AI SaaS landing page called "Luminina" using **Stitch MCP**. We will combine the aesthetic inspiration of `unusualmachines.com` with the dark tech-theme of the AI assistant tool. Given the note that you will use **Squarespace**, the UI will be generated in modular, structured blocks that can easily be translated into Squarespace sections or Custom CSS blocks.

## Proposed Changes

### Environment Fixes

#### [MODIFY] `/Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/scripts/god_mode_admin.py`

Add the following at the top of the file to resolve the local package paths properly:

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

#### [NEW] `/Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/.vscode/settings.json`

#### [NEW] `/Users/pikeymickey/.gemini/antigravity/playground/quantum-whirlpool/.vscode/settings.json`

Set the interpreter path directly:

```json
{
    "python.defaultInterpreterPath": "/usr/bin/python3"
}
```

### Stitch MCP UI scaffolding

- **Create Project**: Using `mcp_StitchMCP_create_project`, create a project named "Luminina".
- **Generate Screen**: Using `mcp_StitchMCP_generate_screen_from_text`, generate the landing page UI layout. We will prompt for a dark theme, a hero section housing a futuristic globe animation placeholder, a clear CTA, a feature section (how we help businesses scale with AI), and an email waitlist.

## Verification Plan

1. **Python Path**: We will run `python3 /Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/scripts/god_mode_admin.py` to ensure the module loads without error.
2. **Stitch Project**: The Stitch MCP tools will return a success state with the generated UI tokens or component suggestions. We don't need to manually test the UI because Stitch handles the generation end-to-end.
