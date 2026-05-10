# Gemini Code Assist & Agent Mode Documentation

## Agent Mode (Preview)

**Overview**
Agent mode enables complex, multi-step development tasks using Gemini CLI backend directly in IDE.

**Supported IDEs**

- VS Code: Available (Preview)

- IntelliJ IDEs: Available (Preview)

- Cloud Workstations: Via VS Code

- Cloud Shell: Via Editor

**Built-in Tools**
Agent mode provides these tools automatically:

- **File Operations:** read, edit, list, search files

- **Terminal:** Run shell commands

- **Web Search:** Gemini search grounding

- **Memory:** Persistent context across sessions

**Activation**

1. Open Gemini Code Assist panel

2. Select Agent mode from chat dropdown

3. Enter multi-step prompt

4. Review and approve tool actions

**YOLO Mode Configuration**
To automatically allow all agent actions (use with caution in trusted workspaces):

```json
"geminicodeassist.agentYoloMode": true

```

## Code Customization (Enterprise)

**Overview**
Code customization provides organization-specific code suggestions based on private repositories.

**Requirements**

- Subscription: Gemini Code Assist Enterprise

- Max Repos: Up to 20,000 repositories

- IAM Roles: `roles/cloudaicompanion.repositoryAdmin`, `roles/cloudaicompanion.customizationAdmin`

**Usage in IDE**

- `@MY_REPO Implement authentication similar to existing patterns`

- `@UTILS_REPO Use our standard logging approach`

## CMEK (Customer-Managed Encryption Keys)

Allows encrypting code customization data with keys you control via Cloud KMS.

## MCP Server Configuration

Model Context Protocol (MCP) servers extend Gemini Code Assist with custom tools.

**VS Code Configuration (`~/.gemini/settings.json`)**

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "@my-org/my-mcp-server"],
      "env": {
        "API_KEY": "${env:MY_API_KEY}"
      }
    }
  }
}
```

## Audit Logging

Service Name: `cloudaicompanion.googleapis.com`

- **Admin Activity:** Always On (Config changes, IAM)

- **Data Access:** Must Enable (Prompts, responses, agent actions)

## Code Generation Methods

1. **Code Transformation:** Ctrl+I / Cmd+I -> `/generate function to...`

2. **Comment-Based:** Write comment -> Ctrl+Enter / Ctrl+Return

3. **Inline Completions:** Start typing -> Tab to accept

4. **Next Edit Predictions:** Suggestions away from cursor (Enable in settings)

## Remote Repository Context

`@REPOSITORY_NAME` to target specific indexed repos for context.

## Smart Actions

Select code -> Click Lightbulb -> Choose action (e.g., "Generate unit tests").
