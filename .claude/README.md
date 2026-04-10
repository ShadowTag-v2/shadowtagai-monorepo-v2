# Claude Code Agents for ShadowTag-v2-fastapi-services

Custom agents to enhance development workflow.

## Available Commands

### Development
- `/api-builder` - Build beautiful FastAPI endpoints with auth, validation, docs
- `/database-expert` - Optimize queries, design schemas, add indexes
- `/code-reviewer` - Get senior-level code reviews

### Quality & Testing
- `/test-generator` - Write unit, integration, and E2E tests
- `/security-scanner` - Find vulnerabilities, implement security best practices

## Usage

Simply type the command followed by your request:

```bash
/api-builder Create a user authentication endpoint with JWT
/security-scanner Review my API for vulnerabilities
/test-generator Write tests for the user service
/database-expert Optimize the user query performance
/code-reviewer Review my latest changes
```

## Adding More Agents

1. Create a new `.md` file in `.claude/commands/`
2. Write the agent's role and instructions
3. Use with `/your-agent-name`

## Resources

- [Claude Code Agents Directory](https://www.claudecodeagents.com/)
- [Claude Code Docs](https://docs.anthropic.com/en/docs/claude-code/overview)
