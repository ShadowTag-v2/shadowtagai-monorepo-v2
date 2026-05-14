# MCP Server Configuration Guide

This document provides information about the MCP (Model Context Protocol) servers configured for this project.

## Overview

All MCP servers have been configured in `.mcp.json` at the project root. This configuration is shared with the team via version control.

## Installed MCP Servers

### Development & Testing Tools

#### Sentry
- **Description**: Monitor errors, debug production issues
- **URL**: https://mcp.sentry.dev/mcp
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

#### Socket
- **Description**: Security analysis for dependencies
- **URL**: https://mcp.socket.dev/
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

#### Hugging Face
- **Description**: Provides access to Hugging Face Hub information and Gradio AI Applications
- **URL**: https://huggingface.co/mcp
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

#### Jam
- **Description**: Debug faster with AI agents that can access Jam recordings like video, console logs, network requests, and errors
- **URL**: https://mcp.jam.dev/mcp
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

### Project Management & Documentation

#### Asana
- **Description**: Interact with your Asana workspace to keep projects on track
- **URL**: https://mcp.asana.com/sse
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

#### Atlassian
- **Description**: Manage your Jira tickets and Confluence docs
- **URL**: https://mcp.atlassian.com/v1/sse
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

#### ClickUp
- **Description**: Task management, project tracking
- **Authentication**: API Key (required)
- **Environment Variables**:
  - `CLICKUP_API_KEY`: Your ClickUp API key
  - `CLICKUP_TEAM_ID`: Your ClickUp team ID
- **Setup**: Update the `.mcp.json` file with your API credentials

#### Intercom
- **Description**: Access real-time customer conversations, tickets, and user data
- **URL**: https://mcp.intercom.com/mcp
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

#### Linear
- **Description**: Integrate with Linear's issue tracking and project management
- **URL**: https://mcp.linear.app/mcp
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

#### Notion
- **Description**: Read docs, update pages, manage tasks
- **URL**: https://mcp.notion.com/mcp
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

#### Box
- **Description**: Ask questions about your enterprise content, get insights from unstructured data, automate content workflows
- **URL**: https://mcp.box.com/
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

#### Fireflies
- **Description**: Extract valuable insights from meeting transcripts and summaries
- **URL**: https://api.fireflies.ai/mcp
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

#### Monday
- **Description**: Manage monday.com boards by creating items, updating columns, assigning owners, setting timelines
- **URL**: https://mcp.monday.com/mcp
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

### Databases & Data Management

#### Airtable
- **Description**: Read/write records, manage bases and tables
- **Authentication**: API Key (required)
- **Environment Variables**:
  - `AIRTABLE_API_KEY`: Your Airtable API key
- **Setup**: Update the `.mcp.json` file with your API key

#### HubSpot
- **Description**: Access and manage HubSpot CRM data by fetching contacts, companies, and deals
- **URL**: https://mcp.hubspot.com/anthropic
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

#### Daloopa
- **Description**: Supplies high quality fundamental financial data sourced from SEC Filings, investor presentations
- **URL**: https://mcp.daloopa.com/server/mcp
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

### Payments & Commerce

#### PayPal
- **Description**: Integrate PayPal commerce capabilities, payment processing, transaction management
- **URL**: https://mcp.paypal.com/mcp
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

#### Plaid
- **Description**: Analyze, troubleshoot, and optimize Plaid integrations. Banking data, financial account linking
- **URL**: https://api.dashboard.plaid.com/mcp/sse
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

#### Square
- **Description**: Use an agent to build on Square APIs. Payments, inventory, orders, and more
- **URL**: https://mcp.squareup.com/sse
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

#### Stripe
- **Description**: Payment processing, subscription management, and financial transactions
- **URL**: https://mcp.stripe.com
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

### Design & Media

#### Figma
- **Description**: Generate better code by bringing in full Figma context
- **URL**: https://mcp.figma.com/mcp
- **Authentication**: Required
- **Setup**: Use `/mcp` in Claude Code to authenticate
- **Notes**: Visit developers.figma.com for local server setup

#### invideo
- **Description**: Build video creation capabilities into your applications
- **URL**: https://mcp.invideo.io/sse
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

#### Canva
- **Description**: Browse, summarize, autofill, and even generate new Canva designs directly from Claude
- **URL**: https://mcp.canva.com/mcp
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

### Infrastructure & DevOps

#### Netlify
- **Description**: Create, deploy, and manage websites on Netlify
- **URL**: https://netlify-mcp.netlify.app/mcp
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

#### Stytch
- **Description**: Configure and manage Stytch authentication services, redirect URLs, email templates
- **URL**: http://mcp.stytch.dev/mcp
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

#### Vercel
- **Description**: Vercel's official MCP server for managing projects, deployments, and analyzing logs
- **URL**: https://mcp.vercel.com/
- **Authentication**: OAuth (required)
- **Setup**: Use `/mcp` in Claude Code to authenticate

## Authentication Setup

### For OAuth-based servers (most HTTP/SSE servers)

1. Within Claude Code, use the `/mcp` command
2. Select the server you want to authenticate with
3. Follow the browser-based OAuth flow
4. Authentication tokens are stored securely and refreshed automatically

### For API Key-based servers (stdio servers)

1. Obtain your API key from the service provider
2. Update the `.mcp.json` file:
   - For Airtable: Replace `YOUR_API_KEY` with your actual Airtable API key
   - For ClickUp: Replace `YOUR_API_KEY` and `YOUR_TEAM_ID` with your actual credentials
3. Restart Claude Code to apply changes

## Important Notes

### Servers Not Included

The following servers from the documentation were not included because they require user-specific URLs:

- **Zapier**: Generate a user-specific URL at mcp.zapier.com
- **Workato**: MCP servers are programmatically generated
- **Cloudflare**: Multiple services available, see documentation for specific server URLs
- **Cloudinary**: Multiple services available, see documentation for specific server URLs

To add these, generate your specific URL from the provider and add them manually to `.mcp.json`.

### Security Considerations

- **Never commit real API keys** to version control
- Use environment variables or secure credential management for production
- The current configuration includes placeholder values for API keys
- Review each service's permissions before authenticating

### Updating Configuration

To add environment variables without hardcoding them in `.mcp.json`:

```json
{
  "mcpServers": {
    "example": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "example-server"],
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

Then set the environment variable before running Claude Code:
```bash
export API_KEY=your_actual_key
claude
```

## Usage

Once authenticated, you can use MCP servers in Claude Code:

1. **View available servers**: Use `/mcp` in Claude Code
2. **Reference resources**: Use `@servername:resource://path` syntax
3. **Execute prompts**: Use `/mcp__servername__promptname` for MCP-provided slash commands
4. **Ask Claude**: Simply ask Claude to interact with the services (e.g., "Check Sentry for recent errors")

## Troubleshooting

- **Connection issues**: Try re-authenticating using `/mcp`
- **Server not responding**: Check if the service is online
- **Authentication expired**: Use `/mcp` to clear and re-authenticate
- **Stdio server errors**: Verify API keys are correctly set in `.mcp.json`

## Resources

- [MCP Official Documentation](https://modelcontextprotocol.io/)
- [Claude Code MCP Guide](https://docs.claude.com/en/docs/claude-code/mcp)
- [MCP Server Directory](https://github.com/modelcontextprotocol/servers)
