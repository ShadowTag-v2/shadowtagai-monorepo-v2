# Walkthrough - Gemini 3.0 Flash Upgrade

## Goal
Upgrade system to `gemini-3.0-flash-preview` and enable "High Thinking" reasoning capabilities.

## Changes

### 1. Upgrade Deployment
- Modified `scripts/gucci_deploy.sh`:
    - Updated `TARGET_MODEL` to `gemini-3.0-flash-preview`.
    - Enhanced update logic to catch all legacy model variants (1.5, 2.5, Pro/Flash).

### 2. Global Codebase Update
- Executed `grep` and `sed` replacements to swap all instances of:
    - `gemini-1.5-flash` / `pro`
    - `gemini-2.5-flash` / `pro`
    - `gemini-pro`
- Replaced with: `gemini-3.0-flash-preview`.

### 3. Smart Client Configuration
- Updated `atomic_pipeline/clients/gemini_client.py`:
    - Added `GEMINI_3_0_FLASH` to `GeminiModel` enum.
    - Set it as the default model.
    - Implemented logic to inject `thinkingConfig` when model is "flash" and thinking is enabled.
    - Configured: `payload["thinkingConfig"] = {"thinking_level": "HIGH", "includeThoughts": True}`.

## Verification Results

### Static Analysis
- **Linting**: Fixed type checking error in matching `GeminiModel` enum. Code is cleaner.

### Runtime Check
- **Client Instantiation**: Confirmed `GeminiClient` initializes with `gemini-3.0-flash-preview` by default.
- **Config**: `enable_thinking` is True.

## Next Steps
- Deploy via `scripts/gucci_deploy.sh` (Cmd+Shift+B).
- Monitor "Thinking" traces in logs to see the "High Reason" output.
