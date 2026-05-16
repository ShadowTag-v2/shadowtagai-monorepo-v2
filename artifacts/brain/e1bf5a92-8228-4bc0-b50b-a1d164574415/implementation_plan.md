# Implementation Plan - Developer Knowledge API & MCP Server

## [Goal Description]
Integrate Google's new **Developer Knowledge API** via **MCP (Model Context Protocol)** to provide the Agent with authoritative, up-to-date documentation for Google Cloud, Android, and Firebase. This fulfills the "Reference Only" clause capability by grounding answers in official docs.

## User Review Required
> [!IMPORTANT]
> **API Key Required**: I cannot generate a restricted API key via CLI. You must generate one in the [Google Cloud Console](https://console.cloud.google.com/apis/credentials) for `developerknowledge.googleapis.com` and provide it, or set it as `GOOGLE_API_KEY` (though the system prefers `GEMINI_API_KEY`, this specific MCP tool might need its own).
> **Confirmation**: I will attempt to enable the service via `gcloud`. If it fails due to permissions, you may need to run it manually.

## Proposed Changes

### 1. Infrastructure (Enable API)
- Run `gcloud beta services mcp enable developerknowledge.googleapis.com` for project `shadowtag-omega-v2`.

### 2. Configuration (MCP Server)
- Locate the active MCP configuration (likely in `.vscode/tasks.json` arguments, `mcp_config.json`, or an internal agent config).
- Add the `developerknowledge` server definition.

#### [NEW/MODIFY] [MCP Config File TBD]
```json
{
  "mcpServers": {
    "google-knowledge": {
      "command": "npx",
      "args": [
        "-y",
        "@google/dev-knowledge-mcp"
      ],
      "env": {
        "GOOGLE_API_KEY": "..."
      }
    }
  }
}
```

## Verification Plan
### Automated Tests
- Restart MCP server/agent.
- Query the agent: "How do I use Firestore with Python?" -> Verify response cites the new tool.

### Manual Verification
- **Playground Sandbox**:
    - Run `python3 apps/playground/sandbox.py`
    - Expected Output: `✅ LINK ESTABLISHED: Sovereign Core is accessible.` and `⛔ INTERCEPTED RISK`.
    - **Status:** Verified (JudgeSix active).
