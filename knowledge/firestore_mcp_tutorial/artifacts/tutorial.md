# How to Manage Your Firestore Database with Natural Language via Firestore MCP Server: Step-by-Step Examples

Imagine being able to manage your Firestore database, update records, and even perform data migrations, all through natural language commands. This is where Google Cloud’s Firestore MCP Server comes in.

This guide will walk you through how to get started with the Firestore MCP Server, and then demonstrate its capabilities with several practical, step-by-step scenarios.

## Configuring the Firestore MCP Server

Assuming that you have a Google Cloud Project , have the Firestore API
( `firestore.googleapis.com` ) enabled for the project, and are using Google Cloud Shell or your own setup with `gcloud` CLI installed and setup, we can do a few things at the start:

```bash
gcloud config set project "YOUR_PROJECT_ID"
gcloud auth application-default login
gcloud beta services mcp enable firestore.googleapis.com --project=[YOUR_PROJECT_ID]
```

## Configure Gemini CLI

Just add the following snippet in the `HOME/.gemini/settings.json` file for Gemini CLI:
```json
"firestore-mcp": {
  "httpUrl": "https://firestore.googleapis.com/mcp",
  "authProviderType": "google_credentials",
  "oauth": {
    "scopes": [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  },
  "timeout": 30000,
  "headers": {
    "x-goog-user-project": "YOUR_PROJECT_ID"
  }
}
```

## Scenarios
1. **Moving a Document**: Mark task as complete and delete from pending.
2. **Conditional Batch Updates**: Flag products running low on stock.
3. **Data Aggregation and Reporting**: Calculate a value from one collection and store it in another.
4. **Managing Hierarchical Data (Chat App)**: Create a chat room and post a welcome message.
5. **Performing a Data Schema Migration**: Evolve data model, change field data types.
6. **Data Validation and Cleanup**: Find and flag documents missing critical information.
7. **Cross-Collection Data Synchronization**: Update related documents when data changes.
8. **Managing Access with Array Fields**: Add a user to an array field for role-based access.
