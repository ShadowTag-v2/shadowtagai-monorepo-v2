# Troubleshooting Google Cloud with Google Cloud Logging and Developer Knowledge MCP Servers

In the world of modern cloud infrastructure, debugging often feels like a weary cycle of:
Copy Error -> Search Documentation -> Try Command -> Repeat.

What if we could automate that entire loop?
Google Cloud has announced fully-managed MCP Servers for Cloud Logging and Developer Knowledge API in preview. By leveraging these servers, we can connect our AI agents directly to our live infrastructure logs and official developer knowledge bases.

In this post, we’ll build a scenario that detects, analyzes, and recommends fixes for Google Cloud platform (GCP) errors.

## The Tech Stack: MCP Servers
We will be using two primary Google managed MCP Servers for our AI agent:

### Google Cloud Logging MCP Server
This server exposes the `list_log_entries` tool, allowing the agent to programmatically scan your project for ERROR and CRITICAL entries. It’s the agent's "eyes" into the system health.

### Google Developer Knowledge MCP Server
This server provides `search_documents`, giving the agent access to the most up-to-date Google Cloud documentation. Unlike general LLM knowledge, this ensures the agent’s recommendations are based on the latest documentation (current official APIs. best practices, CLI syntax and more).

## Setup: Enabling the MCP Servers and our AI Agent (Gemini CLI)

### Step 1: Authentication
Ensure you have an active GCP project and the gcloud CLI installed. Ensure that you have setup the Application Default Credentials (ADC) for the application.
```bash
gcloud auth application-default login
```

### Step 2: Developer Knowledge API Key
For the Developer Knowledge MCP, you’ll need an API key. Here are the steps taken from the documentation:
Enable the Developer Knowledge API from Google APIs library and Create and secure the API key. Add API restrictions specifically for "Developer Knowledge API".

### Step 3 : Enable MCP Servers in your project
```bash
gcloud beta services mcp enable logging.googleapis.com --project=PROJECT_ID
gcloud beta services mcp enable developerknowledge.googleapis.com --project=PROJECT_ID
```

### Step 4 : Setting up the MCP Servers in Gemini CLI
Add the following two blocks for the MCP Servers in the `mcpServers` section in the `HOME/.gemini/settings.json` file.

```json
"logging-mcp": {
      "httpUrl": "https://logging.googleapis.com/mcp",
      "authProviderType": "google_credentials",
      "oauth": {
        "scopes": [
          "https://www.googleapis.com/auth/logging.read"
        ]
      },
      "timeout": 30000,
      "headers": {
        "x-goog-user-project": "YOUR_GCP_PROJECT_ID"
      }
    },
"developer-knowledge-mcp": {
      "httpUrl": "https://developerknowledge.googleapis.com/mcp",
      "headers": {
        "X-Goog-Api-Key": "YOUR_DEVELOPER_KNOWLEDGE_API_KEY"
      }
    }
```

Once you have saved the files and restarted Gemini CLI, check if the MCP Servers have got initialized via the `/mcp list` command.

## The Scenario: Scaling Troubleshooting from One to Many
Instead of running a prompt for every error, we use a prompt that does the following:
1. Retrieve the last 10 logs.
2. Iterate through every unique service failure.
3. Research each one independently using the Developer Knowledge MCP.
4. Consolidate everything into a unified report.

Prompt:
```
I need to troubleshoot recent issues in my Google Cloud project "projects/[YOUR_PROJECT_ID]".

Please perform the following autonomous loop:
1. Retrieval: Use the Logging MCP (list_log_entries) to fetch the 10 most recent entries with severity='ERROR' or 'CRITICAL'.
2. Iteration: For EVERY unique infrastructure-related error found (e.g. GCS, Pub/Sub, Cloud Run, Cloud SQL, Secret Manager):
   a. Extract the key entities (bucket, topic, service account, etc.).
   b. Use the Developer Knowledge MCP (search_documents) to find the official resolution.
3. Resolution: Consolidate ALL findings into a single markdown table: | Service | Error Summary | Root Cause | Recommended Fix (gcloud/config) |. Ensure every error from the logs is addressed.
```

The output will be a structured Resolution Table that you can copy-paste directly into your terminal or configuration management scripts.

## Conclusion
By bridging the gap between live infrastructure logs and the official source of truth in documentation, the workflow presented here provides a glimpse into how we could manage cloud complexity. AI handles the repetitive ‘discovery’ and ‘research’ phases, saving toil.
