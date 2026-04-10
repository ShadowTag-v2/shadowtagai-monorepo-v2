# Claude Agent SDK Migration Summary

## Date: 2025-11-07

## Overview

This repository has been successfully migrated from Claude Code SDK to Claude Agent SDK.

## Changes Made

### 1. TypeScript/JavaScript (Node.js)

- **Removed**: `@anthropic-ai/claude-code`
- **Installed**: `@anthropic-ai/claude-agent-sdk@0.1.30`
- **Updated**: `package.json` and `package-lock.json`

### 2. Python

- **Removed**: `claude-code-sdk` (was not previously installed)
- **Installed**: `claude-agent-sdk@0.1.6`

### 3. Repository Configuration

- **Created**: `.gitignore` to exclude `node_modules/` from version control

## Package Versions Installed

| Package                              | Version |
| ------------------------------------ | ------- |
| @anthropic-ai/claude-agent-sdk (npm) | 0.1.30  |
| claude-agent-sdk (pip)               | 0.1.6   |

## Usage Examples

### TypeScript/JavaScript

```typescript
// Import from the new package
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";

// Use with custom system prompt
const result = query({
  prompt: "Hello",
  options: {
    systemPrompt: "You are a helpful coding assistant",
  },
});

// Or use Claude Code preset
const result = query({
  prompt: "Hello",
  options: {
    systemPrompt: { type: "preset", preset: "claude_code" },
  },
});
```

### Python

```python
# Import from the new package
from claude_agent_sdk import query, ClaudeAgentOptions

# Use with custom system prompt
async for message in query(
    prompt="Hello",
    options=ClaudeAgentOptions(
        system_prompt="You are a helpful coding assistant"
    )
):
    print(message)

# Or use Claude Code preset
async for message in query(
    prompt="Hello",
    options=ClaudeAgentOptions(
        system_prompt={"type": "preset", "preset": "claude_code"}
    )
):
    print(message)
```

## Breaking Changes to Note

### 1. System Prompt No Longer Default

The SDK no longer uses Claude Code's system prompt by default. You must explicitly configure it if needed.

### 2. Settings Sources No Longer Loaded by Default

The SDK no longer reads from filesystem settings (CLAUDE.md, settings.json, slash commands, etc.) by default.

To load settings, explicitly configure:

```typescript
// TypeScript
query({
  prompt: "Hello",
  options: {
    settingSources: ["user", "project", "local"],
  },
});
```

```python
# Python
query(
    prompt="Hello",
    options=ClaudeAgentOptions(
        setting_sources=["user", "project", "local"]
    )
)
```

### 3. Python: ClaudeCodeOptions → ClaudeAgentOptions

If you have existing Python code, rename `ClaudeCodeOptions` to `ClaudeAgentOptions`.

## Migration Checklist

- [x] Uninstall `@anthropic-ai/claude-code` (npm)
- [x] Install `@anthropic-ai/claude-agent-sdk` (npm)
- [x] Update `package.json` dependencies
- [x] Uninstall `claude-code-sdk` (pip)
- [x] Install `claude-agent-sdk` (pip)
- [x] Create `.gitignore` for node_modules
- [x] Verify package installations
- [ ] Update any existing source code imports (none found in this repository)
- [ ] Update any Python dependency files (none found in this repository)

## Next Steps

When you create new code files:

1. **TypeScript/JavaScript**: Import from `@anthropic-ai/claude-agent-sdk`
2. **Python**: Import from `claude_agent_sdk` and use `ClaudeAgentOptions`
3. **System Prompts**: Explicitly configure if you need Claude Code behavior
4. **Settings**: Explicitly configure `settingSources` if you need filesystem settings

## Resources

- [Agent SDK Overview](https://docs.claude.com/en/api/agent-sdk/overview)
- [TypeScript SDK Reference](https://docs.claude.com/en/api/agent-sdk/typescript)
- [Python SDK Reference](https://docs.claude.com/en/api/agent-sdk/python)
- [Custom Tools](https://docs.claude.com/en/api/agent-sdk/custom-tools)
- [MCP Integration](https://docs.claude.com/en/api/agent-sdk/mcp)

## Status

✅ Migration completed successfully on 2025-11-07
