# Hidden Tools Port Spec

## 1. SuggestBackgroundPRTool
### Forensics
- **Location**: `src/tools/SuggestBackgroundPRTool/`
- **Activation**: `USER_TYPE === 'ant'`
- **Function**: Automatically scaffolds a PR in the background for low-priority suggestions without blocking the main workflow.

### AGNT Port
- **Implementation**: `packages/agnt_tools/suggest_pr.py`
- **Logic**: Use the authenticated GitHub App (`scripts/auth_github_app.py`) to spawn an async branch and push a non-blocking PR via the background `LoopSteward`.

## 2. ConfigTool
### Forensics
- **Location**: `src/tools/ConfigTool/`
- **Activation**: `USER_TYPE === 'ant'`
- **Function**: Allows runtime toggling of growthbook flags and modifying internal states without editing code.

### AGNT Port
- **Implementation**: `packages/agnt_tools/config_tool.py`
- **Logic**: Exposes a tool that reads and writes overrides to a local `.beads/agnt_config.json`, which acts as the `AGNT_FC_OVERRIDES` source of truth.

## 3. VerifyPlanExecutionTool
### Forensics
- **Location**: `src/tools/VerifyPlanExecutionTool/`
- **Activation**: `CLAUDE_CODE_VERIFY_PLAN === 'true'`
- **Function**: Forces the agent to review the original spec against the actual output diff.

### AGNT Port
- **Implementation**: `packages/agnt_tools/verify_plan.py`
- **Logic**: Reads the `.md` plan file and executes a cross-check prompt using the `agnt_qa_agent` prior to allowing task completion.
