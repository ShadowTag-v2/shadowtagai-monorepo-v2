# aiyou-fastapi-services: UX Optimizer Agent Implementation Guide

## 1. PROJECT OVERVIEW

### Current State
- **Repository**: Fresh setup with Claude Agent SDK v0.1.30 (npm) and v0.1.6 (pip)
- **Migration Status**: Recently migrated from Claude Code SDK to Claude Agent SDK
- **Structure**: Configuration-based, ready for agent implementations
- **Dependencies**: Node.js 18+ with @anthropic-ai/claude-agent-sdk

### Key Architecture Components
- **SDK Version**: @anthropic-ai/claude-agent-sdk@0.1.30
- **Execution Model**: Agent-based system using query() and tool() functions
- **Tool System**: MCP (Model Context Protocol) compatible tools
- **Configuration**: TypeScript/JavaScript with optional custom agents

---

## 2. HOW AGENTS ARE CURRENTLY IMPLEMENTED

### Agent System Architecture

Agents in Claude Agent SDK are defined through the `AgentDefinition` interface:

```typescript
type AgentDefinition = {
    description: string;        // What the agent does
    tools?: string[];           // Allowed tool names
    disallowedTools?: string[]; // Explicitly forbidden tools
    prompt: string;             // System prompt/instructions
    model?: 'sonnet' | 'opus' | 'haiku' | 'inherit'; // Model choice
};
```

### Agent Registration Pattern

Agents are registered in the `query()` options:

```typescript
import { query } from '@anthropic-ai/claude-agent-sdk';

const result = query({
    prompt: "Your task description",
    options: {
        agents: {
            'agent-name': {
                description: 'What this agent does',
                prompt: 'Detailed system instructions',
                tools: ['tool1', 'tool2'],
                model: 'sonnet'
            }
        }
    }
});
```

---

## 3. AVAILABLE TOOLS & CAPABILITIES

### Built-in Tools (from SDK)

The Agent SDK provides access to these core tools:

1. **File Operations**
   - `FileRead`: Read file contents with offset/limit support
   - `FileWrite`: Create or overwrite files
   - `FileEdit`: Targeted text replacement in files

2. **Command Execution**
   - `Bash`: Execute shell commands with timeout support
   - `BashOutput`: Retrieve background command output

3. **Code Search & Analysis**
   - `Glob`: File pattern matching (glob syntax)
   - `Grep`: Regex-based content search with multiple output modes
   - `NotebookEdit`: Edit Jupyter notebooks

4. **Data & Information**
   - `WebSearch`: Search the web
   - `WebFetch`: Fetch and analyze web content
   - `MCP`: Model Context Protocol resources
   - `ListMcpResources`: Enumerate available MCP resources
   - `ReadMcpResource`: Read MCP resource content

5. **Control Flow**
   - `Agent`: Invoke specialized subagents
   - `TimeMachine`: Rewind and course-correct execution
   - `TodoWrite`: Update task tracking
   - `ExitPlanMode`: Plan approval workflow

6. **User Interaction**
   - `MultipleChoiceQuestion`: Interactive user prompts

### Available Models
- `claude-sonnet-4.5` (default, most capable)
- `claude-opus` (for very complex tasks)
- `claude-haiku` (for simple, fast tasks)

---

## 4. CONFIGURATION STORAGE PATTERNS

### Where Agents Are Defined

**Primary Method - Runtime Configuration:**
```typescript
// Direct in query() options
query({
    prompt: "...",
    options: {
        agents: {
            'my-agent': AgentDefinition
        }
    }
});
```

**Alternative Methods:**
1. **Environment Variables**: Via `env` option
2. **File Loading**: Through `settingSources: ['project', 'user', 'local']`
3. **Plugins**: Via `plugins: [{ type: 'local', path: './plugin-dir' }]`
4. **MCP Servers**: Configured in `mcpServers` option

### Configuration Scope Options
- `'local'`: Session-specific settings
- `'user'`: User-level configuration (~/.claude/)
- `'project'`: Repository-level settings (.claude/ or custom)

---

## 5. PATTERNS FOR ADDING NEW AGENTS

### Pattern 1: Simple Specialized Agent

For a focused agent that handles one domain:

```typescript
const uxOptimizerAgent: AgentDefinition = {
    description: 'UX Optimizer - Analyzes and improves user experience',
    prompt: `You are a UX optimization specialist. Your role is to:
1. Analyze user interface code and designs
2. Identify UX/accessibility issues
3. Suggest improvements based on best practices
4. Review analytics and user feedback
5. Provide actionable recommendations

Focus on:
- Accessibility (WCAG compliance)
- User testing insights
- Performance implications
- Mobile responsiveness
- Cognitive load reduction`,
    tools: ['FileRead', 'Glob', 'WebFetch', 'Grep', 'WebSearch'],
    model: 'sonnet'
};
```

### Pattern 2: Hierarchical Agent System

Use subagents for complex workflows:

```typescript
const mainAgent: AgentDefinition = {
    description: 'Main UX Orchestrator',
    prompt: 'Coordinate UX analysis across multiple domains',
    tools: ['Agent', 'FileRead', 'FileWrite'],
    model: 'sonnet'
};

// Can invoke from main agent:
// Agent tool with subagent_type: 'ui-auditor' or 'a11y-checker'
```

### Pattern 3: Tool-Scoped Agents

Restrict agents to specific tools for safety:

```typescript
const restrictedUXAgent: AgentDefinition = {
    description: 'UX Optimizer (read-only)',
    prompt: 'Analyze UX without making changes',
    tools: ['FileRead', 'Glob', 'Grep', 'WebFetch'],
    disallowedTools: ['FileWrite', 'FileEdit', 'Bash'],
    model: 'haiku' // Use smaller model for analysis
};
```

---

## 6. RECOMMENDED PROJECT STRUCTURE

For the "UX Optimizer" agent, I recommend:

```
aiyou-fastapi-services/
├── .claude/                           # Claude Code settings
│   ├── agents.ts                      # Agent definitions
│   ├── tools.ts                       # Custom tool definitions
│   └── config.json                    # Agent registry
├── src/
│   ├── agents/
│   │   ├── ux-optimizer/
│   │   │   ├── index.ts              # Main agent definition
│   │   │   ├── prompts.ts            # System prompts
│   │   │   ├── tools.ts              # Custom tools for this agent
│   │   │   └── README.md             # Agent documentation
│   │   ├── analytics-analyzer/       # Supporting agent
│   │   ├── accessibility-auditor/    # Supporting agent
│   │   └── index.ts                  # Export all agents
│   ├── tools/
│   │   ├── custom-tools.ts          # MCP-compatible tools
│   │   ├── ux-analyzers.ts          # UX-specific analyzers
│   │   └── metrics.ts                # UX metrics collection
│   └── index.ts                      # Main entry point
├── tests/
│   └── agents/                       # Agent test files
├── examples/
│   └── ux-optimizer-example.ts       # Usage example
├── package.json
└── AGENT_REGISTRY.md                 # Documentation
```

---

## 7. IMPLEMENTATION PATTERNS & BEST PRACTICES

### Pattern A: Agent Composition

```typescript
// agents/ux-optimizer/index.ts
import { AgentDefinition } from '@anthropic-ai/claude-agent-sdk';

export const uxOptimizer: AgentDefinition = {
    description: 'Comprehensive UX analysis and optimization',
    prompt: getSystemPrompt(),
    tools: ['FileRead', 'Glob', 'Grep', 'WebFetch', 'Agent'],
    model: 'sonnet'
};

// Can call other agents for specific tasks:
// "Use the Agent tool with subagent_type: 'accessibility-auditor'
//  to check WCAG compliance..."
```

### Pattern B: Model Selection Strategy

```typescript
// Haiku: Quick analysis (cost-efficient)
analysisAgent: { model: 'haiku', ... }

// Sonnet: Detailed recommendations (balanced)
optimizationAgent: { model: 'sonnet', ... }

// Opus: Complex design decisions (high quality)
strategicAgent: { model: 'opus', ... }

// inherit: Use parent model
supportingAgent: { model: 'inherit', ... }
```

### Pattern C: Permission & Safety

```typescript
// In query() options:
{
    permissionMode: 'plan',  // Require approval for tool use
    canUseTool: async (toolName, input) => {
        if (toolName === 'Bash') {
            return { behavior: 'ask' }; // Ask user
        }
        return { behavior: 'allow', updatedInput: input };
    },
    allowedTools: ['FileRead', 'Glob'], // Whitelist
    disallowedTools: ['Bash'] // Blacklist
}
```

---

## 8. QUICK START: IMPLEMENTING UX OPTIMIZER

### Step 1: Create Agent Definition

```typescript
// src/agents/ux-optimizer/index.ts
import { AgentDefinition } from '@anthropic-ai/claude-agent-sdk';

export const uxOptimizer: AgentDefinition = {
    description: 'UX Optimizer - Analyzes and improves user experience',
    prompt: `You are an expert UX optimization specialist with deep knowledge of:

Core Responsibilities:
1. UI/UX Code Analysis: Review frontend code for UX issues
2. Accessibility Audits: Check WCAG 2.1 compliance
3. Performance Impact: Analyze UX performance metrics
4. User Research: Incorporate analytics and feedback
5. Recommendations: Provide actionable improvements

Analysis Framework:
- Interaction Patterns: Usability and intuitiveness
- Visual Hierarchy: Information organization
- Accessibility: WCAG, screen readers, keyboard navigation
- Performance: Load times, responsiveness, Core Web Vitals
- Mobile: Responsive design, touch interactions
- Analytics: User behavior data interpretation

When analyzing:
1. First understand the context and purpose
2. Identify specific UX/accessibility issues
3. Explain impact on users
4. Provide concrete, implementable solutions
5. Include code examples where relevant`,
    
    tools: [
        'FileRead',      // Read UI code
        'Glob',          // Find UI components
        'Grep',          // Search for patterns
        'WebFetch',      // Research best practices
        'WebSearch',     // Current UX standards
        'Agent'          // Delegate to specialists
    ],
    
    model: 'sonnet'
};
```

### Step 2: Create Entry Point

```typescript
// src/index.ts
import { query } from '@anthropic-ai/claude-agent-sdk';
import { uxOptimizer } from './agents/ux-optimizer';

export async function analyzeUX(prompt: string) {
    const result = query({
        prompt,
        options: {
            agents: {
                'ux-optimizer': uxOptimizer
            },
            systemPrompt: {
                type: 'preset',
                preset: 'claude_code'
            }
        }
    });

    return result;
}
```

### Step 3: Create Example Usage

```typescript
// examples/ux-optimizer-example.ts
import { analyzeUX } from '../src';

async function exampleUsage() {
    const result = await analyzeUX(`
        Using the ux-optimizer agent, analyze the file 
        /path/to/component.tsx for UX issues and provide 
        recommendations for improvement.
    `);

    for await (const message of result) {
        console.log(message);
    }
}

exampleUsage().catch(console.error);
```

---

## 9. CONFIGURATION FILES TO CREATE

### .claude/agents.json

```json
{
  "agents": {
    "ux-optimizer": {
      "type": "specialist",
      "models": ["sonnet"],
      "tools": ["FileRead", "Glob", "Grep", "WebFetch", "Agent"],
      "capabilities": [
        "ui-analysis",
        "accessibility-audit",
        "performance-analysis",
        "user-research"
      ]
    },
    "accessibility-auditor": {
      "type": "supporting",
      "models": ["haiku"],
      "tools": ["FileRead", "Glob"]
    }
  }
}
```

### package.json Scripts

```json
{
  "scripts": {
    "agent:ux": "node -r esbuild-register src/agents/ux-optimizer/index.ts",
    "example:ux": "node -r esbuild-register examples/ux-optimizer-example.ts",
    "test:agents": "jest tests/agents"
  }
}
```

---

## 10. INTEGRATION POINTS & EXTENSIBILITY

### Custom MCP Tools

```typescript
// src/tools/custom-tools.ts
import { tool, createSdkMcpServer } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';

export const analyzeUXMetrics = tool(
    'analyze_ux_metrics',
    'Analyze user experience metrics and performance data',
    {
        filePath: z.string().describe('Path to metrics file'),
        threshold: z.number().optional().describe('Alert threshold')
    },
    async ({ filePath, threshold }) => {
        // Implementation
        return { output: 'metrics analysis' };
    }
);

export const uxToolServer = createSdkMcpServer({
    name: 'ux-tools',
    version: '1.0.0',
    tools: [analyzeUXMetrics]
});
```

### Hooks for Monitoring

```typescript
// In query() options:
{
    hooks: {
        'PreToolUse': [{
            hooks: [
                async (input, toolUseID) => ({
                    continue: true,
                    systemMessage: `Tool ${input.tool_name} being used...`
                })
            ]
        }],
        'PostToolUse': [{
            hooks: [
                async (input, toolUseID) => ({
                    continue: true,
                    additionalContext: `Tool completed with results...`
                })
            ]
        }]
    }
}
```

---

## 11. TESTING STRATEGY

### Test Structure

```typescript
// tests/agents/ux-optimizer.test.ts
import { query } from '@anthropic-ai/claude-agent-sdk';
import { uxOptimizer } from '../../src/agents/ux-optimizer';

describe('UX Optimizer Agent', () => {
    it('should analyze UI component for accessibility', async () => {
        const result = query({
            prompt: 'Analyze accessibility in /test/component.tsx',
            options: {
                agents: { 'ux-optimizer': uxOptimizer },
                cwd: '/test'
            }
        });

        let finalResult;
        for await (const message of result) {
            if (message.type === 'result') {
                finalResult = message;
            }
        }

        expect(finalResult).toBeDefined();
    });
});
```

---

## 12. DEPLOYMENT & USAGE

### Production Configuration

```typescript
// src/index.ts - Production setup
import { query } from '@anthropic-ai/claude-agent-sdk';
import { uxOptimizer } from './agents/ux-optimizer';

export async function analyzeUXProduction(
    userPrompt: string,
    options: {
        maxTurns?: number;
        maxBudgetUsd?: number;
        model?: string;
    } = {}
) {
    return query({
        prompt: userPrompt,
        options: {
            agents: { 'ux-optimizer': uxOptimizer },
            model: options.model || 'claude-sonnet-4.5',
            maxTurns: options.maxTurns || 10,
            maxBudgetUsd: options.maxBudgetUsd || 5,
            permissionMode: 'acceptEdits', // Auto-approve for safety
            cwd: process.cwd()
        }
    });
}
```

---

## 13. KEY TAKEAWAYS

### For UX Optimizer Implementation:

1. **Define Clear Scope**: Focus on UX analysis and recommendations
2. **Tool Selection**: Use FileRead, Glob, Grep for code analysis
3. **Model Strategy**: Sonnet for analysis, Haiku for quick checks
4. **Safety**: Restrict to read-only operations (no FileEdit/Bash)
5. **Composition**: Use Agent tool to delegate to specialized agents
6. **Documentation**: Document UX analysis framework in prompts
7. **Testing**: Test with real component examples
8. **Monitoring**: Use hooks to track agent behavior

### Next Steps:

1. Create `/src/agents/ux-optimizer/` directory structure
2. Define agent with comprehensive system prompt
3. Create example usage script
4. Add test cases for common UX analysis scenarios
5. Document UX analysis framework
6. Build supporting agents (accessibility-auditor, performance-analyzer)

