# Claude Code GitHub Actions Integration

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Setup](#setup)
  - [Prerequisites](#prerequisites)
  - [Quick Setup](#quick-setup)
  - [Manual Setup](#manual-setup)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Mentioning Claude](#mentioning-claude)
  - [Assigning Issues](#assigning-issues)
  - [Pull Request Reviews](#pull-request-reviews)
- [Advanced Configuration](#advanced-configuration)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

## Overview

Claude Code GitHub Actions integration enables AI-powered automation in your repository. By integrating Claude directly into your GitHub workflow, you can:

- Get intelligent code reviews on pull requests
- Implement features and bug fixes automatically
- Answer questions about your codebase
- Generate documentation
- Perform automated code analysis

The integration uses the official [Claude Code Action](https://github.com/anthropics/claude-code-action) and runs entirely within your GitHub Actions infrastructure.

## Features

### Intelligent Mode Detection

Claude automatically determines how to help based on context:

- **Interactive Mode**: Answer questions when @claude is mentioned
- **Implementation Mode**: Create code changes and PRs when assigned to issues
- **Review Mode**: Analyze pull requests and suggest improvements

### Flexible Authentication

Supports multiple authentication backends:

- Direct Anthropic API
- Amazon Bedrock
- Google Vertex AI

### GitHub Integration

- Works seamlessly with PR comments and reviews
- Updates issue statuses and creates check runs
- Visual progress tracking with dynamic checkboxes
- Full access to GitHub API and repository files

## Setup

### Prerequisites

1. **Repository admin access** - Required to configure secrets and workflows
2. **Anthropic API key** - Get one from [console.anthropic.com](https://console.anthropic.com)
3. **GitHub Actions enabled** - Must be enabled in repository settings

### Quick Setup

The fastest way to set up is using Claude Code terminal:

```bash
/install-github-app
```

This command will:

1. Guide you through GitHub app setup
2. Configure required secrets automatically
3. Create the workflow file in your repository

### Manual Setup

If you prefer manual setup or need custom configuration:

#### Step 1: Add API Key to Secrets

1. Go to your repository settings
2. Navigate to **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `ANTHROPIC_API_KEY`
5. Value: Your Anthropic API key
6. Click **Add secret**

#### Step 2: Create Workflow File

The workflow file is already created at `.github/workflows/claude.yml` in this repository.

#### Step 3: Verify Permissions

Ensure the workflow has the necessary permissions:

```yaml
permissions:
  contents: write
  pull-requests: write
  issues: write
  checks: write
```

## Configuration

### Basic Configuration

The minimal configuration requires only your API key:

```yaml
- uses: anthropics/claude-code-action@v2
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Model Selection

Specify a particular Claude model:

```yaml
- uses: anthropics/claude-code-action@v2
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    model: "claude-sonnet-4-5-20250929"
```

Available models:

- `claude-sonnet-4-5-20250929` (latest, recommended)
- `claude-opus-4-5-20250514`
- `claude-haiku-4-5-20250514`

### Custom Instructions

Provide project-specific guidance for Claude:

```yaml
- uses: anthropics/claude-code-action@v2
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    instructions: |
      This is a FastAPI project using Python 3.11+.

      Code review guidelines:
      - Enforce PEP 8 style compliance
      - Check for security vulnerabilities (SQL injection, XSS, etc.)
      - Verify proper error handling and logging
      - Ensure all endpoints have appropriate authentication
      - Check for proper async/await usage

      Implementation guidelines:
      - Follow existing project structure in /app
      - Use Pydantic models for request/response validation
      - Include comprehensive docstrings
      - Add unit tests in /tests directory
      - Update API documentation
```

## Usage

### Mentioning Claude

Simply mention @claude in any PR or issue comment to get assistance:

**Example: Asking a question**

```
@claude What's the purpose of the UserService class in app/services/user.py?
```

**Example: Requesting a review**

```
@claude Can you review this PR and check for security issues?
```

**Example: Requesting changes**

```
@claude Please add error handling to the database connection logic in app/db.py
```

### Assigning Issues

Assign an issue to @claude to have it implement the requested feature or fix:

1. Create an issue describing the feature or bug
2. Assign the issue to @claude
3. Claude will analyze the codebase and create a PR with the implementation

### Pull Request Reviews

Claude can automatically review PRs:

**Automatic Review**: Configure your workflow to trigger on PR events (already configured in this repo)

**Manual Review**: Comment on a PR:

```
@claude Please review this PR
```

Claude will:

- Analyze all changed files
- Check for bugs and security issues
- Suggest improvements
- Verify code follows project standards

## Advanced Configuration

### Trigger Specific Files Only

Review only certain files or directories:

```yaml
on:
  pull_request:
    paths:
      - "app/**"
      - "tests/**"
      - "requirements.txt"
```

### Scheduled Maintenance

Run Claude on a schedule for maintenance tasks:

```yaml
on:
  schedule:
    - cron: "0 0 * * 0" # Weekly on Sunday
  workflow_dispatch:

jobs:
  maintenance:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v2
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          instructions: |
            Review the codebase for:
            - Outdated dependencies
            - Deprecated API usage
            - TODO comments that should be addressed
            - Missing documentation
```

### Multiple Workflows

Create separate workflows for different purposes:

- `.github/workflows/claude-review.yml` - PR reviews
- `.github/workflows/claude-docs.yml` - Documentation updates
- `.github/workflows/claude-security.yml` - Security scans

## Best Practices

### Security

1. **Always use secrets** - Never hardcode API keys
2. **Limit permissions** - Only grant necessary permissions
3. **Review changes** - Always review Claude's PRs before merging
4. **Use branch protection** - Require reviews for all PRs including Claude's

### Custom Instructions

1. **Be specific** - Provide clear guidelines about your project
2. **Include coding standards** - Reference style guides and conventions
3. **Define test requirements** - Specify testing expectations
4. **Document architecture** - Explain key design patterns

### Workflow Triggers

1. **Use appropriate triggers** - Don't trigger on every event
2. **Filter by paths** - Only run when relevant files change
3. **Combine triggers** - Use multiple trigger types when needed

### Performance

1. **Use latest model** - Generally provides best results
2. **Optimize instructions** - Keep custom instructions concise
3. **Limit scope** - Focus Claude on specific tasks

## Troubleshooting

### Common Issues

#### Claude doesn't respond to mentions

**Possible causes:**

- Workflow file has syntax errors
- API key is not configured correctly
- GitHub Actions is disabled

**Solutions:**

1. Check workflow run logs in Actions tab
2. Verify `ANTHROPIC_API_KEY` secret exists
3. Ensure Actions is enabled in repository settings

#### Permission denied errors

**Cause:** Insufficient workflow permissions

**Solution:** Add required permissions to workflow:

```yaml
permissions:
  contents: write
  pull-requests: write
  issues: write
  checks: write
```

#### API rate limits

**Cause:** Too many requests to Anthropic API

**Solutions:**

- Reduce trigger frequency
- Use path filters to limit when workflow runs
- Consider using scheduled workflows instead of on every event

#### Claude makes incorrect changes

**Solutions:**

- Provide more detailed custom instructions
- Be more specific in your requests
- Review and refine prompts in issue descriptions
- Add examples of expected output

### Getting Help

1. **Check workflow logs**: Go to Actions tab and review failed runs
2. **Review documentation**: Visit [docs.claude.com/en/docs/claude-code/github-actions](https://docs.claude.com/en/docs/claude-code/github-actions)
3. **GitHub issues**: Check [github.com/anthropics/claude-code-action/issues](https://github.com/anthropics/claude-code-action/issues)
4. **Update action**: Ensure you're using the latest version (`@v2`)

## Examples

### Example 1: Automated PR Review

```yaml
name: PR Review

on:
  pull_request:
    types: [opened, synchronize]

permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v2
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          instructions: |
            Review this PR focusing on:
            - Code quality and maintainability
            - Security vulnerabilities
            - Performance implications
            - Test coverage
```

### Example 2: Documentation Updates

```yaml
name: Update Docs

on:
  issue_comment:
    types: [created]

permissions:
  contents: write
  issues: write

jobs:
  docs:
    if: contains(github.event.comment.body, '@claude update docs')
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v2
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          instructions: |
            Update documentation to reflect recent code changes.
            Ensure all docstrings are complete and accurate.
```

### Example 3: Security Scan

```yaml
name: Security Review

on:
  schedule:
    - cron: "0 0 * * 1" # Monday at midnight
  workflow_dispatch:

permissions:
  contents: read
  issues: write

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v2
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          instructions: |
            Perform security review focusing on:
            - SQL injection vulnerabilities
            - XSS attack vectors
            - Authentication and authorization issues
            - Sensitive data exposure
            - Known CVEs in dependencies

            Create an issue with findings.
```

### Example 4: Feature Implementation

Simply create an issue like:

```
Title: Add rate limiting to API endpoints

Description:
Implement rate limiting for all API endpoints to prevent abuse.

Requirements:
- Use Redis for rate limit storage
- Limit to 100 requests per minute per IP
- Return 429 status code when limit exceeded
- Add X-RateLimit-* headers to responses

Assign to: @claude
```

Claude will analyze the codebase and create a PR with the implementation.

## Additional Resources

- **Official Documentation**: [docs.claude.com/en/docs/claude-code/github-actions](https://docs.claude.com/en/docs/claude-code/github-actions)
- **GitHub Repository**: [github.com/anthropics/claude-code-action](https://github.com/anthropics/claude-code-action)
- **GitHub Marketplace**: [github.com/marketplace/actions/claude-code-action-official](https://github.com/marketplace/actions/claude-code-action-official)
- **Claude Code SDK**: [github.com/anthropics/claude-agent-sdk](https://github.com/anthropics/claude-agent-sdk)
- **Migration Guide**: For upgrading from v0.x to v2

## License

This documentation is for the pnkln-stack-fastapi-services project. The Claude Code Action is licensed under MIT by Anthropic.
