# Claude Code Integration Guide

## Overview

This guide demonstrates how to leverage the **5 specialized Claude Code agents** to optimize your development workflow, create custom automations, and maximize productivity when using Claude Code.

---

## Table of Contents

1. [Introduction to Claude Code](#introduction-to-claude-code)
2. [The 5 Claude Code Agents](#the-5-claude-code-agents)
3. [Session Optimization](#session-optimization)
4. [Hooks & Skills](#hooks--skills)
5. [MCP Server Integration](#mcp-server-integration)
6. [Slash Commands](#slash-commands)
7. [Workflow Architecture](#workflow-architecture)
8. [Complete Examples](#complete-examples)
9. [Best Practices](#best-practices)

---

## Introduction to Claude Code

**Claude Code** is Anthropic's official CLI for Claude, providing powerful development capabilities through:

- **200K token context window** - Work with large codebases
- **Specialized tools** - Read, Edit, Write, Glob, Grep, Bash, and more
- **Extensibility** - Hooks, skills, MCP servers, slash commands
- **Context management** - Automatic compaction for long sessions
- **Production-ready** - Built with best practices

---

## The 5 Claude Code Agents

### 1. **Claude Code Session Optimizer** ⚡

**ID**: `claude_code_session_optimizer`

Analyzes and optimizes your Claude Code sessions for maximum productivity.

**Capabilities**:

- Context window usage analysis (200K tokens)
- Task breakdown recommendations
- Tool usage efficiency optimization
- Workflow pattern suggestions
- Anti-pattern detection

**Use When**:

- Sessions feel slow or inefficient
- Context window fills up quickly
- Need to optimize development workflow
- Want to improve task completion rate

---

### 2. **Hook & Skill Designer** 🪝

**ID**: `hook_and_skill_designer`

Creates custom hooks and skills for Claude Code automation.

**Capabilities**:

- Design SessionStart hooks (`.claude/hooks/session-start.sh`)
- Create PromptSubmit hooks (validation, modification)
- Implement ToolCall hooks (safety, standards)
- Build reusable skills (`.claude/skills/*.md`)
- Ensure safety and performance

**Use When**:

- Need project setup automation
- Want to enforce coding standards
- Require custom validation logic
- Building reusable task patterns

---

### 3. **MCP Server Integration Expert** 🔌

**ID**: `mcp_server_integration`

Integrates Model Context Protocol servers to extend Claude Code capabilities.

**Capabilities**:

- Design custom MCP servers
- Integrate existing MCP servers
- Manage tool availability
- Optimize server performance
- Debug integration issues

**Use When**:

- Need database access from Claude Code
- Want to call external APIs
- Require custom development tools
- Extending Claude Code functionality

---

### 4. **Slash Command Builder** ⚡

**ID**: `slash_command_builder`

Creates custom slash commands for common workflows.

**Capabilities**:

- Design slash commands (`.claude/commands/*.md`)
- Create command composition patterns
- Implement context-aware commands
- Build project-specific automations
- Organize command hierarchies

**Use When**:

- Repeating common task sequences
- Need project-specific workflows
- Want to standardize team processes
- Building command libraries

---

### 5. **Claude Code Workflow Architect** 🏗️

**ID**: `claude_code_workflow_architect`

Designs optimal workflows and task breakdown patterns.

**Capabilities**:

- Design efficient task workflows
- Create task breakdown hierarchies
- Optimize tool usage sequences
- Implement context-efficient processes
- Enable effective collaboration patterns

**Use When**:

- Starting new projects
- Optimizing team workflows
- Need task breakdown guidance
- Building repeatable processes

---

## Session Optimization

### Analyzing Your Current Session

```python
from agents import AgentRegistry

optimizer = AgentRegistry.get_agent("claude_code_session_optimizer")

result = await optimizer.execute(
    task="Analyze my current session and recommend optimizations",
    context={
        "session_type": "feature_development",
        "context_usage": "65%",  # Estimated context used
        "common_operations": [
            "Reading large files",
            "Multiple small edits",
            "Frequent grep searches"
        ],
        "pain_points": [
            "Context fills up quickly",
            "Lots of back-and-forth",
            "Slow progress on tasks"
        ]
    }
)

print(result["prompt"])
```

### Common Optimization Strategies

#### 1. Context Management

**Problem**: Context window fills up quickly

**Solutions**:

- Use `offset`/`limit` when reading large files
- Grep with `head_limit` and type filters
- Glob with specific patterns (not `**/*`)
- Read only relevant file sections
- Summarize completed work

**Example**:

```python
# ❌ BAD: Reads entire 10K line file
Read(file_path="/app/large_file.py")

# ✅ GOOD: Reads only relevant section
Read(file_path="/app/large_file.py", offset=100, limit=50)
```

#### 2. Tool Usage Efficiency

**Problem**: Too many tool calls, slow progress

**Solutions**:

- Parallel tool calls for independent operations
- Batch edits in single messages
- Use TodoWrite for complex task tracking
- Avoid Bash for file operations (use Read/Write)

**Example**:

```python
# ❌ BAD: Sequential independent operations
Read(file_path="/app/file1.py")
Read(file_path="/app/file2.py")
Read(file_path="/app/file3.py")

# ✅ GOOD: Parallel reads in one message
[
    Read(file_path="/app/file1.py"),
    Read(file_path="/app/file2.py"),
    Read(file_path="/app/file3.py")
]
```

#### 3. Task Breakdown

**Problem**: Tasks too large, get lost in context

**Solutions**:

- Break into subtasks (< 10K tokens each)
- Use TodoWrite to track progress
- Complete one subtask before starting next
- Document decisions along the way

**Example**:

```python
TodoWrite(todos=[
    {"content": "Implement user authentication", "status": "in_progress"},
    {"content": "Add password hashing", "status": "pending"},
    {"content": "Create login endpoint", "status": "pending"},
    {"content": "Write tests", "status": "pending"},
    {"content": "Update documentation", "status": "pending"}
])
```

---

## Hooks & Skills

### Creating Session Start Hooks

**File**: `.claude/hooks/session-start.sh`

**Use Cases**:

- Install dependencies
- Start development servers
- Setup environment
- Run migrations

**Example**:

```bash
#!/bin/bash
# .claude/hooks/session-start.sh

echo "🚀 Starting project setup..."

# Install dependencies
if [ -f "package.json" ]; then
    npm install --silent
fi

if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
fi

# Start development server in background
if [ -f "docker-compose.yml" ]; then
    docker-compose up -d
fi

echo "✅ Project ready!"
```

**Creating with Agent**:

```python
hook_designer = AgentRegistry.get_agent("hook_and_skill_designer")

result = await hook_designer.execute(
    task="Create a session-start hook for my Next.js project",
    context={
        "project_type": "Next.js 14 with TypeScript",
        "dependencies": ["npm", "prisma", "docker"],
        "tasks": [
            "Install npm dependencies",
            "Run Prisma migrations",
            "Start PostgreSQL with Docker",
            "Start dev server"
        ]
    }
)
```

### Creating Custom Skills

**File**: `.claude/skills/create-api-endpoint.md`

**Example Skill**:

```markdown
# Create REST API Endpoint

Create a new REST API endpoint following our project conventions:

1. **Define Route** in `src/routes/{resource}.ts`
   - Use Express Router
   - Add input validation with Zod
   - Implement error handling

2. **Create Controller** in `src/controllers/{resource}.ts`
   - Implement CRUD operations
   - Add business logic
   - Handle edge cases

3. **Add Service Layer** in `src/services/{resource}.ts`
   - Database operations
   - External API calls
   - Data transformations

4. **Write Tests** in `tests/{resource}.test.ts`
   - Unit tests for controller
   - Integration tests for endpoint
   - Edge case coverage

5. **Update Documentation** in `docs/api/{resource}.md`
   - Endpoint description
   - Request/response examples
   - Error codes

Follow TypeScript strict mode and our ESLint configuration.
```

**Using the Skill**:

```bash
# In Claude Code
/skill create-api-endpoint
# Claude will follow the defined process
```

---

## MCP Server Integration

### What is MCP?

**Model Context Protocol** extends Claude Code with custom tools by running external servers.

**MCP Server Structure**:

```
mcp-servers/
├── database-server/      # Query databases
├── api-integration/      # Call external APIs
└── custom-tools/         # Project-specific tools
```

### Creating a Database MCP Server

**Example**: PostgreSQL query server

```typescript
// mcp-servers/database/server.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { Client } from "pg";

const server = new Server({
  name: "postgres-mcp",
  version: "1.0.0",
});

const db = new Client({
  connectionString: process.env.DATABASE_URL,
});

await db.connect();

// Define tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "query_database",
      description: "Execute SQL query on PostgreSQL",
      inputSchema: {
        type: "object",
        properties: {
          query: { type: "string" },
          params: { type: "array" },
        },
        required: ["query"],
      },
    },
  ],
}));

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "query_database") {
    const { query, params = [] } = request.params.arguments;
    const result = await db.query(query, params);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result.rows, null, 2),
        },
      ],
    };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

**Configure in Claude Code**:

```json
// .claude/config.json
{
  "mcpServers": {
    "postgres": {
      "command": "node",
      "args": ["mcp-servers/database/server.js"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost/db"
      }
    }
  }
}
```

**Using the MCP Server**:

```python
# Now Claude can query your database directly!
# "Query the users table for active accounts"
# Claude will use the query_database tool
```

### Creating with Agent

```python
mcp_expert = AgentRegistry.get_agent("mcp_server_integration")

result = await mcp_expert.execute(
    task="Create MCP server for GitHub API integration",
    context={
        "apis": ["repos", "issues", "pull_requests"],
        "auth": "OAuth token",
        "rate_limiting": "5000 req/hour"
    }
)
```

---

## Slash Commands

### Creating Project Commands

**File**: `.claude/commands/feature.md`

```markdown
# Create new feature

Create a feature called "{0}" following our stack:

**Stack**:

- Framework: Next.js 14
- Database: PostgreSQL + Prisma
- Styling: Tailwind CSS
- Testing: Jest + Playwright

**Steps**:

1. Create component in `components/{0}/`
2. Add route in `app/{0}/page.tsx`
3. Create API route in `app/api/{0}/route.ts`
4. Add Prisma schema if needed
5. Write tests in `__tests__/{0}/`
6. Update documentation

Ensure TypeScript strict mode and follow our coding standards.
```

**Usage**:

```bash
/feature user-profile
# Creates full feature with all boilerplate
```

### Command Composition

**File**: `.claude/commands/ship.md`

```markdown
# Ship feature to production

Complete workflow to ship "{0}":

1. Run `/test {0}` - Ensure all tests pass
2. Run `/review components/{0}` - Code review
3. Run `/doc {0}` - Update documentation
4. Run `/deploy staging` - Deploy to staging
5. Verify staging works
6. Run `/deploy production` - Deploy to production
7. Monitor for issues

This command chains multiple commands for a complete workflow.
```

### Creating with Agent

```python
command_builder = AgentRegistry.get_agent("slash_command_builder")

result = await command_builder.execute(
    task="Create command for bug fix workflow",
    context={
        "issue_tracker": "GitHub Issues",
        "steps": [
            "Fetch issue details",
            "Reproduce bug",
            "Fix and test",
            "Update changelog"
        ]
    }
)
```

---

## Workflow Architecture

### Designing Efficient Workflows

**Use the Workflow Architect**:

```python
architect = AgentRegistry.get_agent("claude_code_workflow_architect")

result = await architect.execute(
    task="Design workflow for adding new API endpoints",
    context={
        "framework": "Express.js",
        "requirements": [
            "RESTful design",
            "Input validation",
            "Error handling",
            "Test coverage",
            "Documentation"
        ]
    }
)
```

### Common Workflow Patterns

#### 1. Feature Development

```
Planning → Implementation → Testing → Documentation → Review
```

**TodoWrite Plan**:

```python
[
    {"content": "Define API contract", "status": "in_progress"},
    {"content": "Implement route handler", "status": "pending"},
    {"content": "Add input validation", "status": "pending"},
    {"content": "Write unit tests", "status": "pending"},
    {"content": "Add integration tests", "status": "pending"},
    {"content": "Update API documentation", "status": "pending"},
    {"content": "Code review", "status": "pending"}
]
```

#### 2. Bug Fix

```
Reproduce → Root Cause → Fix → Test → Verify
```

#### 3. Refactoring

```
Analyze → Design → Transform → Test → Document
```

---

## Complete Examples

### Example 1: Optimizing a Slow Session

**Problem**: Session is slow, context fills up quickly

**Solution**:

```python
# 1. Analyze session
optimizer = AgentRegistry.get_agent("claude_code_session_optimizer")

analysis = await optimizer.execute(
    task="Analyze my session and provide optimization recommendations",
    context={
        "typical_tasks": ["Reading large files", "Making small edits"],
        "context_usage": "80%",
        "time_spent": "2 hours with little progress"
    }
)

# 2. Apply recommendations
# - Use offset/limit for file reads
# - Batch edits together
# - Use TodoWrite for tracking
```

### Example 2: Creating Project Automation

**Goal**: Automate new feature creation

**Solution**:

```python
# 1. Create session-start hook
hook_designer = AgentRegistry.get_agent("hook_and_skill_designer")

hook = await hook_designer.execute(
    task="Create session-start hook for project setup",
    context={"project": "Next.js", "tasks": ["npm install", "prisma migrate"]}
)

# 2. Create feature command
command_builder = AgentRegistry.get_agent("slash_command_builder")

command = await command_builder.execute(
    task="Create /feature command",
    context={"includes": ["component", "route", "tests", "docs"]}
)

# 3. Now use automation
# /feature user-dashboard
```

### Example 3: Database Integration

**Goal**: Query database from Claude Code

**Solution**:

```python
# Create MCP server
mcp_expert = AgentRegistry.get_agent("mcp_server_integration")

server = await mcp_expert.execute(
    task="Create PostgreSQL MCP server",
    context={
        "operations": ["query", "migrations", "schema_info"],
        "connection": "postgresql://localhost/mydb"
    }
)

# Now use in Claude Code:
# "Show me all users created in the last week"
# Claude will query database via MCP
```

---

## Best Practices

### Session Optimization

✅ **DO**:

- Use offset/limit for large files
- Parallel tool calls when independent
- Batch related edits
- TodoWrite for task tracking
- Clear, concise communication

❌ **DON'T**:

- Read entire large files
- Sequential independent operations
- Multiple small edits separately
- Verbose logging that fills context
- Skip task breakdown for complex work

### Hooks & Skills

✅ **DO**:

- Keep hooks fast (< 30s)
- Make hooks idempotent
- Validate inputs
- Log errors
- Test thoroughly

❌ **DON'T**:

- Hardcode secrets
- Run blocking operations
- Ignore errors
- Make hooks too complex
- Skip safety checks

### MCP Servers

✅ **DO**:

- Single responsibility principle
- Fast tool execution (< 5s)
- Robust error handling
- Type-safe schemas
- Security-first design

❌ **DON'T**:

- Create overly complex servers
- Ignore authentication
- Skip input validation
- Forget timeouts
- Neglect monitoring

### Slash Commands

✅ **DO**:

- Clear, specific instructions
- Define expected outputs
- Include success criteria
- Provide examples
- Keep focused

❌ **DON'T**:

- Make commands too generic
- Skip documentation
- Ignore project context
- Create command sprawl
- Forget to test

### Workflows

✅ **DO**:

- Break into manageable tasks
- Define clear deliverables
- Identify dependencies
- Enable parallelization
- Track progress

❌ **DON'T**:

- Make tasks too large
- Skip planning
- Ignore context limits
- Over-engineer processes
- Forget quality gates

---

## Quick Reference

### Using the Agents

```python
from agents import AgentRegistry

# Session Optimization
optimizer = AgentRegistry.get_agent("claude_code_session_optimizer")
result = await optimizer.execute("Analyze my session")

# Hook & Skill Design
designer = AgentRegistry.get_agent("hook_and_skill_designer")
result = await designer.execute("Create session-start hook")

# MCP Integration
mcp = AgentRegistry.get_agent("mcp_server_integration")
result = await mcp.execute("Create database MCP server")

# Slash Commands
builder = AgentRegistry.get_agent("slash_command_builder")
result = await builder.execute("Create /feature command")

# Workflow Design
architect = AgentRegistry.get_agent("claude_code_workflow_architect")
result = await architect.execute("Design API development workflow")
```

### Project Structure

```
project/
├── .claude/
│   ├── config.json           # MCP server configuration
│   ├── hooks/
│   │   ├── session-start.sh  # Startup automation
│   │   └── tool-call.sh      # Tool validation
│   ├── commands/
│   │   ├── feature.md        # /feature command
│   │   ├── test.md           # /test command
│   │   └── deploy.md         # /deploy command
│   └── skills/
│       ├── api-endpoint.md   # API creation skill
│       └── component.md      # Component creation skill
└── mcp-servers/
    ├── database/             # Database MCP server
    └── api-integration/      # API MCP server
```

---

## Next Steps

1. **Start with Session Optimization**
   - Analyze your current workflow
   - Apply recommended optimizations
   - Measure improvement

2. **Add Project Automation**
   - Create session-start hook
   - Build common slash commands
   - Design reusable skills

3. **Extend Capabilities**
   - Integrate MCP servers
   - Add custom tools
   - Build team workflows

4. **Share with Team**
   - Document conventions
   - Standardize commands
   - Train team members

---

## Support

- **Agent Documentation**: See agent system prompts for detailed capabilities
- **Claude Code Docs**: <https://docs.claude.com/en/docs/claude-code>
- **MCP SDK**: <https://modelcontextprotocol.io>
- **Issues**: <https://github.com/ehanc69/ShadowTag-v2-fastapi-services/issues>

---

**Ready to optimize?** Use the agents to level up your Claude Code workflow!
