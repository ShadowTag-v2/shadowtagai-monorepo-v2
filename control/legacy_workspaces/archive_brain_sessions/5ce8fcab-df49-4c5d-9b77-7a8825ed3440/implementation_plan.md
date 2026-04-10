# Implementation Plan - Gemini 3 Flash Upgrade

## Goal
Upgrade the entire `ShadowTag-Omega-v2` codebase to use `gemini-3.0-flash-preview` exclusively, replacing all legacy model references. Configure the "Thinking Level" to `HIGH` to align with the "Antigravity/Ultrathink" persona, maximizing reasoning capabilities for the new flash model.

## User Review Required
> [!IMPORTANT]
> **Model Change**: This is a global replacement. All `gemini-1.5-*` and `gemini-2.5-*` references will be replaced with `gemini-3.0-flash-preview`.
> **Thinking Level**: We are introducing `thinking_code="HIGH"` (or equivalent config) to the `GeminiClient`.

## Proposed Changes

### 1. Upgrade Deployment Script
#### [MODIFY] `scripts/gucci_deploy.sh`
- Update `TARGET_MODEL` variable to `gemini-3.0-flash-preview`.
- Ensure the `sed` command correctly targets all legacy model patterns.

### 2. Codebase-Wide Model Replacement
#### [MODIFY] Multiple Files
- Use `sed` or `fasd` (if available, else `find` + `sed`) to replace occurrences of:
    - `gemini-1.5-flash`
    - `gemini-1.5-pro`
    - `gemini-2.5-flash`
    - `gemini-2.5-pro`
    - `gemini-pro`
- Target: `gemini-3.0-flash-preview`

### 3. Configure Thinking Level
#### [MODIFY] `atomic_pipeline/clients/gemini_client.py`
- Locate `genai.Client` initialization or `generate_content` calls.
- Inject `thinking_config={'thinking_level': 'HIGH'}` into the generation config.
- *Note:* We need to verify if the library version supports this specific parameter syntax. If not, we will default to the latest supported pattern.

## Verification Plan

### Automated Verification
- **Run Agent Test**: Execute `scripts/gucci_agent.sh` (after updating it to use the new model logic if it hardcodes it).
- **Check Response**: Verify the agent output confirms `gemini-3.0-flash-preview` is active.

### Manual Verification
- **Review Diff**: Check the `sed` replacement results to ensure no unintended strings were modified.
- **Deploy**: Run the `gucci_deploy.sh` script (simulated or dry run if possible) to confirm it builds.
