# Getting Started with Google MCP Services

This tutorial is part of a comprehensive guide to building AI agents on Google Cloud. For the full roadmap, including tutorials on security, logging, and database management, visit the Google MCP Servers Tutorial Series.

Welcome to the tutorial on the newly released Google Developer Knowledge MCP Server.
Introducing the Developer Knowledge API and MCP Server.
Announcing the Developer Knowledge API and MCP server in public preview. Connect your AI tools and agents directly to the most up to date and correct developer knowledge for Google services.

## The problem with AI and Developer Knowledge
Language Models are trained on historical snapshots of data. When dealing with APIs, cloud SDKs, or system architecture that changes frequently, the LLMs often hallucinate deprecated parameters or old library syntax.

The Google Developer Knowledge API solves this by giving models a direct search interface into the official Google documentation. By combining this API with the Model Context Protocol (MCP), you can expose this search tool directly to an AI agent like Gemini or Claude.

## Setting it up
The primary configuration is to map the API to the correct endpoint and provide an API Key.
1. Enable the API in GCP.
2. Generate an API Key.
3. Add the MCP server configuration to your tool, passing the API key in the `X-Goog-Api-Key` header.

## Using the Tool
Once configured, the agent has access to `search_documents`. It can formulate queries based on your prompt, retrieve the official documentation snippets, and synthesize a correct, grounded response.

Happy to learn.
