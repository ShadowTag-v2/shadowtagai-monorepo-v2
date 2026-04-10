# Claude Code GitHub Actions Workflows

This directory contains GitHub Actions workflows that integrate Claude Code AI into our development process.

## Prerequisites

Before using these workflows, ensure you have:


1. **Installed the Claude GitHub App** to this repository

   - Visit: https://github.com/apps/claude

   - Grant permissions for Contents, Issues, and Pull Requests


2. **Added the ANTHROPIC_API_KEY secret**

   - Go to: Repository Settings → Secrets and variables → Actions

   - Create a new secret named `ANTHROPIC_API_KEY`

   - Add your Claude API key from https://console.anthropic.com

## Available Workflows

### 1. Claude Code (`claude.yml`)

**Trigger**: `@claude` mention in issue comments or PR comments

**Purpose**: Interactive AI assistant that responds to mentions

**Usage**:

```

@claude implement user authentication
@claude fix the bug in the login endpoint
@claude how should I structure this feature?

```

**Features**:

- Responds to natural language requests

- Creates PRs with implementations

- Answers questions about code

- Provides suggestions and recommendations

---

### 2. Claude PR Review (`claude-pr-review.yml`)

**Trigger**: When a PR is opened or updated

**Purpose**: Automatic code review for all pull requests

**What it checks**:

- Code quality and style

- Potential bugs

- Best practices adherence

- Documentation completeness

**Configuration**:

- Max turns: 5

- Auto-runs on every PR

**To disable**: Remove or comment out the workflow file

---

### 3. Claude Bug Fix (`claude-bug-fix.yml`)

**Trigger**: When an issue is labeled with "bug"

**Purpose**: Automatically analyzes and attempts to fix bugs

**Usage**:

1. Create an issue describing the bug

2. Add the "bug" label

3. Claude will analyze and create a fix PR

**What Claude does**:

- Investigates the root cause

- Implements a fix

- Adds regression tests

- Creates a PR with the changes

---

### 4. Claude Security Review (`claude-security-review.yml`)

**Trigger**: When a PR is labeled with "security-review"

**Purpose**: Comprehensive security analysis of code changes

**Usage**:

1. Create or update a PR

2. Add the "security-review" label

3. Claude performs deep security analysis

**Security checks**:

- OWASP Top 10 vulnerabilities

- Input validation issues

- Authentication/authorization flaws

- SQL injection and XSS

- Sensitive data exposure

- API security

- Dependency vulnerabilities

**Model**: Uses Claude Opus for thorough analysis

---

### 5. Claude Code Quality Check (`claude-code-quality.yml`)

**Trigger**: When Python files change in a PR

**Purpose**: Automated code quality review

**What it reviews**:

- PEP 8 compliance

- Type hints usage

- Code duplication

- Function complexity

- Error handling

- Documentation

- Test coverage

- Performance

**Output**: Quality score (1-10) with specific improvement suggestions

---

## Customizing Workflows

### Change the Model

Edit the `claude_args` parameter:

```yaml
claude_args: "--model claude-opus-4-1-20250805"

```

Available models:

- `claude-sonnet-4-5-20250929` (default, fast and capable)

- `claude-opus-4-1-20250805` (most capable, for complex tasks)

- `claude-haiku-4-1-20250805` (fastest, for simple tasks)

### Adjust Conversation Length

Control how many back-and-forth interactions Claude can have:

```yaml
claude_args: "--max-turns 10"

```

### Custom Prompts

Modify the `prompt` parameter to customize behavior:

```yaml
prompt: |
  Review this code for:

  1. Security issues

  2. Performance problems

  3. Code style

```

### Add Custom Tools

Restrict or specify which tools Claude can use:

```yaml
claude_args: "--allowed-tools Read,Write,Bash"

```

## Best Practices

### 1. API Usage Optimization


- Use specific prompts to reduce API calls

- Set appropriate `--max-turns` limits

- Enable only needed workflows

- Use workflow conditions to limit runs

### 2. Security


- Never commit API keys to the repository

- Always use GitHub Secrets

- Review Claude's suggestions before merging

- Use security-review workflow for sensitive changes

### 3. Cost Management


- Monitor GitHub Actions minutes usage

- Track Claude API token consumption

- Use concurrency controls for workflows

- Set appropriate timeouts

### 4. Workflow Triggers


- Use specific labels to control when workflows run

- Combine conditions to prevent unnecessary runs

- Test workflows on feature branches first

## Configuration Files

### CLAUDE.md

The `CLAUDE.md` file in the repository root defines:

- Code style guidelines

- Review criteria

- Project-specific rules

- FastAPI best practices

Claude follows these guidelines when generating code.

### Workflow Conditions

Each workflow includes conditions to control when it runs:

```yaml
if: |
  (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude'))

```

Modify these to customize trigger behavior.

## Troubleshooting

### Claude not responding


1. ✅ Verify GitHub App is installed

2. ✅ Check ANTHROPIC_API_KEY secret exists

3. ✅ Ensure workflow triggers are correct

4. ✅ Check Actions tab for workflow runs

5. ✅ Verify `@claude` mention syntax

### Workflow not running


1. Check workflow file syntax (YAML validation)

2. Verify trigger conditions are met

3. Check repository permissions

4. Look for errors in Actions tab

### API rate limits


1. Reduce `--max-turns` value

2. Use more specific prompts

3. Disable auto-running workflows

4. Implement concurrency controls

## Examples

### Request a feature implementation

```

@claude implement a new endpoint for user profile updates with these requirements:

- PUT /api/v1/users/{user_id}/profile

- Accept JSON body with name, email, bio

- Validate all inputs

- Return updated user profile

- Add tests

```

### Ask for architecture advice

```

@claude how should I structure the authentication system for this API?
Consider JWT tokens, refresh tokens, and role-based access control.

```

### Request code refactoring

```

@claude refactor the database connection code to use dependency injection
and follow the FastAPI best practices outlined in CLAUDE.md

```

## Resources


- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)

- [Claude Code GitHub Actions](https://github.com/anthropics/claude-code-action)

- [GitHub Actions Documentation](https://docs.github.com/en/actions)

- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Support

For issues with:

- **Claude Code**: https://github.com/anthropics/claude-code/issues

- **Workflows**: Create an issue in this repository

- **API access**: https://console.anthropic.com

---

**Note**: These workflows consume both GitHub Actions minutes and Claude API tokens. Monitor usage and adjust configurations as needed.
