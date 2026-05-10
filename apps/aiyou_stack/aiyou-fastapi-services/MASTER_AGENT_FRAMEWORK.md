# Master Agent Framework

## Universal Agent Distribution Architecture

A production-ready framework for distributing specialized AI agent configurations inspired by Claude Code's plugin marketplace architecture. This framework enables instant agent specialization, team-wide standardization, and version-controlled evolution of agent capabilities.

## Table of Contents

- [Overview](#overview)

- [Architecture](#architecture)

- [Core Concepts](#core-concepts)

- [Agent Archetypes](#agent-archetypes)

- [Installation & Usage](#installation--usage)

- [Configuration](#configuration)

- [Extension Development](#extension-development)

- [Best Practices](#best-practices)

---

## Overview

### Vision

**"Think Different. Make a Dent in the Universe."**

The Master Agent Framework transforms how teams deploy and manage AI agents by providing:

- **Instant Specialization**: Select agent archetypes from a marketplace for immediate deployment

- **Team Standardization**: Share agent configurations across teams via version-controlled manifests

- **Modular Composition**: Combine tools, personas, hooks, and integrations flexibly

- **Production Ready**: Battle-tested patterns that "just work" at scale

### Key Benefits

1. **Marketplace-Driven Distribution**: Centralized discovery and installation of agent templates

2. **Component Architecture**: Modular design with commands, agents, hooks, and MCP servers

3. **Flexible Deployment**: Strict mode for production, non-strict for rapid prototyping

4. **Dynamic Configuration**: Environment variable patterns for portable agent setups

---

## Architecture

### Component Model

```

master-agent-marketplace/
├── marketplace/
│   └── marketplace.json           # Central marketplace configuration
├── agents/
│   ├── research/                  # Research agent archetype
│   │   ├── manifest.json          # Agent configuration
│   │   ├── tools/                 # Agent-specific tools
│   │   │   ├── search.js
│   │   │   ├── synthesis.js
│   │   │   └── citation.js
│   │   ├── personas/              # Persona configurations
│   │   │   ├── academic.md
│   │   │   ├── business.md
│   │   │   └── technical.md
│   │   └── hooks/                 # Event-driven behaviors
│   │       └── validate-sources.sh
│   ├── coding/                    # Coding agent archetype
│   │   ├── manifest.json
│   │   ├── tools/
│   │   │   ├── test-runner.js
│   │   │   ├── linter.js
│   │   │   └── formatter.js
│   │   ├── personas/
│   │   │   ├── backend-dev.md
│   │   │   ├── frontend-dev.md
│   │   │   └── devops.md
│   │   └── hooks/
│   │       ├── run-tests.sh
│   │       └── lint-and-format.sh
│   ├── analysis/                  # Analysis agent archetype
│   └── deployment/                # Deployment agent archetype
└── settings.json                  # Team-wide settings

```

### Architecture Principles

1. **Marketplace-Centric**: All agents are distributed through a marketplace model

2. **Component-Based**: Agents compose tools, personas, hooks, and integrations

3. **Version-Controlled**: All configurations tracked in git for auditability

4. **Environment-Aware**: Dynamic paths via `${CLAUDE_PLUGIN_ROOT}` pattern

5. **Mode-Flexible**: Strict mode for production, non-strict for development

---

## Core Concepts

### 1. Agent Archetypes

Pre-configured agent templates optimized for specific domains:

- **Research Agent**: Information gathering, synthesis, citation management

- **Coding Agent**: Software development, testing, code review

- **Analysis Agent**: Data analysis, visualization, reporting

- **Deployment Agent**: CI/CD, infrastructure, monitoring

### 2. Component Types

#### Commands (Tools)

JavaScript/TypeScript implementations using Claude Agent SDK's `tool()` function:

```typescript
import { tool } from "@anthropic-ai/claude-agent-sdk";

export const myTool = tool({
  name: "tool_name",
  description: "What the tool does",
  parameters: { /* JSON Schema */ },
  execute: async (params) => { /* implementation */ }
});

```

#### Personas

Markdown files defining agent personality, expertise, and behavior:

```markdown

# Senior Backend Developer

## Identity

You are a senior backend developer...

## Core Competencies



- API design


- Database optimization
...

## Temperature: 0.3

```

#### Hooks

Event-driven shell scripts triggered by agent actions:

```json
{
  "hooks": {
    "PostToolUse": [{"type": "command", "command": "validate.sh"}],
    "PreCommit": [{"type": "command", "command": "lint.sh"}]
  }
}

```

#### MCP Servers

Model Context Protocol integrations for external services:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  }
}

```

### 3. Operating Modes

#### Strict Mode

- Agent manifest must be complete and valid

- All dependencies explicitly declared

- Suitable for production environments

- Enabled: `"strictMode": true`

#### Non-Strict Mode

- Marketplace can provide missing configuration

- Faster prototyping and iteration

- Suitable for development

- Enabled: `"strictMode": false` (default)

---

## Agent Archetypes

### Research Agent

**Purpose**: Comprehensive information gathering and synthesis

**Capabilities**:

- Multi-source search (web, academic, technical)

- Information synthesis with citations

- Source credibility evaluation

- Multiple citation styles (APA, MLA, Chicago)

**Personas**:

- **Academic**: Rigorous research with peer-reviewed focus

- **Business**: Market research and actionable insights

- **Technical**: Deep technical evaluation and benchmarking

**Use Cases**:

- Literature reviews

- Competitive intelligence

- Technology evaluation

- Market research

**Installation**:

```bash
npx @anthropic-ai/claude-agent-sdk install research-agent

```

### Coding Agent

**Purpose**: Software development, testing, and quality assurance

**Capabilities**:

- Code generation (Python, TypeScript, Rust, Go)

- Test automation (pytest, jest, mocha)

- Code review and refactoring

- CI/CD integration

**Personas**:

- **Backend Developer**: API design, database optimization

- **Frontend Developer**: React/Vue/Angular, UX focus

- **DevOps Engineer**: Infrastructure, deployment, monitoring

**Use Cases**:

- Feature development

- Test suite creation

- Code refactoring

- Deployment automation

**Installation**:

```bash
npx @anthropic-ai/claude-agent-sdk install coding-agent

```

### Analysis Agent

**Purpose**: Data analysis, metrics tracking, and reporting

**Capabilities**:

- Data analysis and visualization

- Metrics tracking and reporting

- Business intelligence

- Performance analysis

**Personas**:

- **Data Scientist**: Statistical analysis, ML

- **Business Analyst**: KPIs, ROI analysis

**Use Cases**:

- Performance reporting

- Data pipeline analysis

- Business metrics tracking

### Deployment Agent

**Purpose**: Infrastructure management and deployment automation

**Capabilities**:

- Deployment automation

- Infrastructure as Code

- CI/CD pipeline management

- Health monitoring

**Personas**:

- **DevOps Engineer**: Deployment automation

- **SRE**: Reliability and monitoring

**Use Cases**:

- Production deployments

- Infrastructure provisioning

- Monitoring setup

---

## Installation & Usage

### Prerequisites

```bash

# Install Claude Agent SDK

npm install @anthropic-ai/claude-agent-sdk

# or

pip install claude-agent-sdk

```

### Quick Start

#### 1. Clone or Install from Marketplace

```bash

# Clone repository

git clone https://github.com/yourusername/master-agent-framework.git
cd master-agent-framework

# Install dependencies

npm install

```

#### 2. Select Agent Archetype

```bash

# Install research agent

npx @anthropic-ai/claude-agent-sdk install research-agent

# Or use the marketplace CLI (conceptual)

./marketplace install research-agent@latest

```

#### 3. Configure Agent

```json
{
  "agent": "research-agent",
  "persona": "academic",
  "tools": ["search", "synthesis", "citation"],
  "settingSources": ["user", "project", "local"]
}

```

#### 4. Use in Your Code

**TypeScript Example**:

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";
import { searchTool, synthesisTool } from "./agents/research/tools";

// Initialize agent with research tools
const result = await query({
  prompt: "Research the latest developments in quantum computing",
  options: {
    systemPrompt: {
      type: "file",
      path: "./agents/research/personas/academic.md"
    },
    tools: [searchTool, synthesisTool],
    settingSources: ["project", "local"]
  }
});

```

**Python Example**:

```python
from claude_agent_sdk import query, ClaudeAgentOptions

# Use research agent

async for message in query(
    prompt="Research machine learning trends 2024",
    options=ClaudeAgentOptions(
        system_prompt={
            "type": "file",
            "path": "./agents/research/personas/business.md"
        },
        setting_sources=["project", "local"]
    )
):
    print(message)

```

---

## Configuration

### Marketplace Configuration

**File**: `marketplace/marketplace.json`

```json
{
  "name": "master-agent-marketplace",
  "version": "1.0.0",
  "strictMode": false,
  "plugins": [
    {
      "id": "research-agent",
      "source": "./agents/research",
      "commands": ["./agents/research/tools/*.js"],
      "agents": ["./agents/research/personas/*.md"],
      "hooks": { /* ... */ },
      "mcpServers": { /* ... */ }
    }
  ]
}

```

### Agent Manifest

**File**: `agents/{archetype}/manifest.json`

```json
{
  "name": "research-agent",
  "version": "1.0.0",
  "archetype": "research",
  "capabilities": {
    "search": { "enabled": true },
    "synthesis": { "enabled": true }
  },
  "tools": [ /* ... */ ],
  "personas": { /* ... */ },
  "hooks": { /* ... */ },
  "environment": {
    "AGENT_ROOT": "${CLAUDE_PLUGIN_ROOT}/agents/research"
  }
}

```

### Team Settings

**File**: `settings.json`

```json
{
  "agents": {
    "default": "coding-agent",
    "personas": {
      "coding": "backend-dev",
      "research": "technical"
    }
  },
  "marketplace": {
    "registry": "https://internal.company.com/agents",
    "autoUpdate": false
  }
}

```

---

## Extension Development

### Creating a New Agent Archetype

#### 1. Directory Structure

```bash
mkdir -p agents/my-agent/{tools,personas,hooks}

```

#### 2. Create Manifest

```json
{
  "name": "my-agent",
  "version": "1.0.0",
  "description": "My custom agent",
  "capabilities": {},
  "tools": [],
  "personas": {},
  "hooks": {}
}

```

#### 3. Implement Tools

```typescript
import { tool } from "@anthropic-ai/claude-agent-sdk";

export const myTool = tool({
  name: "my_tool",
  description: "Custom tool",
  parameters: {
    type: "object",
    properties: {
      input: { type: "string" }
    }
  },
  execute: async ({ input }) => {
    return { success: true, data: input };
  }
});

```

#### 4. Define Personas

Create `agents/my-agent/personas/specialist.md`:

```markdown

# My Specialist

## Identity

You are a specialist in...

## Core Competencies



- Skill 1


- Skill 2

## Temperature: 0.5

```

#### 5. Register in Marketplace

Add to `marketplace/marketplace.json`:

```json
{
  "plugins": [
    {
      "id": "my-agent",
      "name": "My Agent",
      "source": "./agents/my-agent",
      "commands": ["./agents/my-agent/tools/*.js"],
      "agents": ["./agents/my-agent/personas/*.md"]
    }
  ]
}

```

---

## Best Practices

### 1. Version Control Everything

- Commit all agent configurations

- Tag releases semantically (v1.0.0, v1.1.0)

- Document breaking changes

### 2. Use Personas Effectively

- Define clear expertise boundaries

- Set appropriate temperature values

- Document use cases

### 3. Tool Design

- Single responsibility principle

- Comprehensive error handling

- Rich metadata in responses

### 4. Team Standardization

- Share `settings.json` via git

- Document team-specific configurations

- Use private marketplace for proprietary agents

### 5. Testing

- Test tools independently

- Validate persona effectiveness

- Monitor hook performance

### 6. Security

- Never hardcode secrets

- Use environment variables

- Implement least-privilege access

### 7. Documentation

- Keep personas updated

- Document tool parameters

- Provide usage examples

---

## Architecture Insights

This framework incorporates key patterns from Claude Code's plugin marketplace:

### 1. Marketplace-Driven Distribution

- Centralized agent discovery

- Version-controlled distribution

- Public and private registries

- Team standardization via `settings.json`

### 2. Component Architecture

- **Commands**: Agent actions/tools

- **Agents**: Persona configurations

- **Hooks**: Event-driven behaviors

- **MCP Servers**: External integrations

### 3. Deployment Flexibility

- **Strict Mode**: Complete manifest required (production)

- **Non-Strict Mode**: Marketplace fills gaps (development)

### 4. Dynamic Configuration

- `${CLAUDE_PLUGIN_ROOT}` for portable paths

- Environment-specific settings

- Runtime configuration injection

---

## Roadmap

### Phase 1: Foundation (Current)

- [x] Core marketplace architecture

- [x] Four agent archetypes (research, coding, analysis, deployment)

- [x] Basic tool implementations

- [x] Persona system

### Phase 2: Enhancement

- [ ] Web-based marketplace UI

- [ ] Agent versioning and updates

- [ ] Tool composition framework

- [ ] Advanced hooks system

### Phase 3: Scale

- [ ] Enterprise registry support

- [ ] Team collaboration features

- [ ] Analytics and telemetry

- [ ] Multi-language support

### Phase 4: Ecosystem

- [ ] Community marketplace

- [ ] Plugin certification

- [ ] Agent marketplace API

- [ ] Third-party integrations

---

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.

---

## License

MIT License - see LICENSE file for details.

---

## Resources

- [Claude Agent SDK Documentation](https://docs.claude.com/en/api/agent-sdk/overview)

- [Claude Code Plugin Marketplace](https://docs.claude.com/en/docs/claude-code)

- [Model Context Protocol](https://modelcontextprotocol.io/)

---

**"The people who are crazy enough to think they can change the world are the ones who do."**

This framework is your scaffolding for making that dent in the universe—a universal agent framework that scales from individual use to enterprise deployment through marketplace mechanics.
