# Claude Agent SDK - Complete Reference

## SDK Imports

```typescript
// Main query function for running agents
import { query } from '@anthropic-ai/claude-agent-sdk';

// Custom tool creation
import { tool, createSdkMcpServer } from '@anthropic-ai/claude-agent-sdk';

// Type definitions
import type {
    AgentDefinition,
    Options,
    Query,
    SDKMessage,
    SDKAssistantMessage,
    SDKUserMessage,
    SDKResultMessage,
    PermissionMode,
    HookEvent,
    HookCallback,
    CanUseTool
} from '@anthropic-ai/claude-agent-sdk';
```

## Core Types

### AgentDefinition
Definition of a single agent.

```typescript
interface AgentDefinition {
    // Brief description of agent's role (3-5 words)
    description: string;
    
    // Detailed system prompt with instructions
    prompt: string;
    
    // Tools this agent can use
    tools?: string[];
    
    // Tools explicitly forbidden
    disallowedTools?: string[];
    
    // Model selection: 'sonnet' | 'opus' | 'haiku' | 'inherit'
    model?: 'sonnet' | 'opus' | 'haiku' | 'inherit';
}
```

### Options
Configuration for query() function.

```typescript
interface Options {
    // Agents available to this query
    agents?: Record<string, AgentDefinition>;
    
    // Model to use
    model?: string;  // e.g., 'claude-sonnet-4.5'
    
    // Maximum turns/iterations
    maxTurns?: number;
    
    // Maximum budget in USD
    maxBudgetUsd?: number;
    
    // Maximum thinking tokens
    maxThinkingTokens?: number;
    
    // Permission mode: 'default' | 'acceptEdits' | 'bypassPermissions' | 'plan'
    permissionMode?: 'default' | 'acceptEdits' | 'bypassPermissions' | 'plan';
    
    // Whitelist of allowed tools
    allowedTools?: string[];
    
    // Blacklist of disallowed tools
    disallowedTools?: string[];
    
    // Working directory
    cwd?: string;
    
    // Environment variables
    env?: Record<string, string | undefined>;
    
    // System prompt configuration
    systemPrompt?: string | {
        type: 'preset';
        preset: 'claude_code';
        append?: string;
    };
    
    // Load settings from filesystem
    settingSources?: ('user' | 'project' | 'local')[];
    
    // Custom tools callback
    canUseTool?: CanUseTool;
    
    // MCP servers
    mcpServers?: Record<string, McpServerConfig>;
    
    // Event hooks
    hooks?: Partial<Record<HookEvent, HookCallbackMatcher[]>>;
    
    // Plugins to load
    plugins?: SdkPluginConfig[];
}
```

### Query (Return Type)
Async generator that streams results.

```typescript
interface Query extends AsyncGenerator<SDKMessage, void> {
    // Control methods
    interrupt(): Promise<void>;
    setPermissionMode(mode: PermissionMode): Promise<void>;
    setModel(model?: string): Promise<void>;
    setMaxThinkingTokens(tokens: number | null): Promise<void>;
    
    // Query methods
    supportedCommands(): Promise<SlashCommand[]>;
    supportedModels(): Promise<ModelInfo[]>;
    mcpServerStatus(): Promise<McpServerStatus[]>;
    accountInfo(): Promise<AccountInfo>;
}
```

### SDKMessage Union Types

```typescript
// System message (initialization)
interface SDKSystemMessage {
    type: 'system';
    subtype: 'init';
    agents?: string[];
    tools: string[];
    model: string;
    // ... other fields
}

// User input message
interface SDKUserMessage {
    type: 'user';
    message: APIUserMessage;
    session_id: string;
    uuid: UUID;
}

// Agent response
interface SDKAssistantMessage {
    type: 'assistant';
    message: APIAssistantMessage;
    uuid: UUID;
    session_id: string;
}

// Tool execution progress
interface SDKToolProgressMessage {
    type: 'tool_progress';
    tool_name: string;
    elapsed_time_seconds: number;
}

// Stream event (for partial messages)
interface SDKPartialAssistantMessage {
    type: 'stream_event';
    event: RawMessageStreamEvent;
}

// Final result
interface SDKResultMessage {
    type: 'result';
    subtype: 'success' | 'error_during_execution' | 'error_max_turns' | 'error_max_budget_usd';
    result: string;
    usage: NonNullableUsage;
    modelUsage: Record<string, ModelUsage>;
    permission_denials: SDKPermissionDenial[];
    total_cost_usd: number;
}
```

## Built-in Tools

### File Operations

#### FileRead
Read file contents.
```typescript
interface FileReadInput {
    file_path: string;           // Absolute path
    offset?: number;             // Line offset
    limit?: number;              // Lines to read
}
```

#### FileWrite
Create or overwrite file.
```typescript
interface FileWriteInput {
    file_path: string;           // Absolute path
    content: string;             // File content
}
```

#### FileEdit
Replace text in file.
```typescript
interface FileEditInput {
    file_path: string;           // Absolute path
    old_string: string;          // Text to find
    new_string: string;          // Replacement text
    replace_all?: boolean;       // Replace all occurrences
}
```

### Command Execution

#### Bash
Run shell commands.
```typescript
interface BashInput {
    command: string;             // Shell command
    timeout?: number;            // Timeout in ms (max 600000)
    description?: string;        // What this does
    run_in_background?: boolean; // Run async
    dangerouslyDisableSandbox?: boolean; // Disable sandbox
}
```

#### BashOutput
Get background command output.
```typescript
interface BashOutputInput {
    bash_id: string;             // Background shell ID
    filter?: string;             // Regex filter for output
}
```

#### KillShell
Terminate background command.
```typescript
interface KillShellInput {
    shell_id: string;            // Background shell ID
}
```

### File Search & Analysis

#### Glob
Find files by pattern.
```typescript
interface GlobInput {
    pattern: string;             // Glob pattern (e.g., "**/*.ts")
    path?: string;               // Search directory
}
```

#### Grep
Search file contents with regex.
```typescript
interface GrepInput {
    pattern: string;             // Regex pattern
    path?: string;               // Search directory
    glob?: string;               // File filter pattern
    output_mode?: 'content' | 'files_with_matches' | 'count';
    '-B'?: number;               // Lines before match
    '-A'?: number;               // Lines after match
    '-C'?: number;               // Lines before/after
    '-n'?: boolean;              // Show line numbers
    '-i'?: boolean;              // Case insensitive
    type?: string;               // File type (js, ts, py, etc)
    head_limit?: number;         // Limit results
    multiline?: boolean;         // Match across lines
}
```

#### NotebookEdit
Edit Jupyter notebooks.
```typescript
interface NotebookEditInput {
    notebook_path: string;       // Path to .ipynb
    cell_id?: string;            // Cell to edit
    new_source: string;          // New cell content
    cell_type?: 'code' | 'markdown'; // Cell type
    edit_mode?: 'replace' | 'insert' | 'delete'; // Operation
}
```

### Information & Web

#### WebFetch
Fetch and analyze URL content.
```typescript
interface WebFetchInput {
    url: string;                 // URL to fetch
    prompt: string;              // How to analyze it
}
```

#### WebSearch
Search the web.
```typescript
interface WebSearchInput {
    query: string;               // Search query
    allowed_domains?: string[];  // Only these domains
    blocked_domains?: string[];  // Exclude these domains
}
```

### Control Flow

#### Agent
Invoke a subagent.
```typescript
interface AgentInput {
    description: string;         // Short task description (3-5 words)
    prompt: string;              // Task instructions
    subagent_type: string;       // Agent to use
    model?: 'sonnet' | 'opus' | 'haiku'; // Model override
    resume?: string;             // Resume from previous
}
```

#### TimeMachine
Rewind and course-correct.
```typescript
interface TimeMachineInput {
    message_prefix: string;      // Message to rewind to
    course_correction: string;   // New instructions
    restore_code?: boolean;      // Restore file history
}
```

#### ExitPlanMode
Submit plan for approval.
```typescript
interface ExitPlanModeInput {
    plan: string;                // Plan to approve
}
```

### User Interaction

#### MultipleChoiceQuestion
Ask user questions.
```typescript
interface MultipleChoiceQuestionInput {
    questions: Array<{
        question: string;        // The question
        header: string;          // Short label (max 12 chars)
        options: Array<{
            text: string;        // Option text
        }>;
        multiSelect?: boolean;   // Allow multiple choices
    }>;
}
```

#### TodoWrite
Update task tracking.
```typescript
interface TodoWriteInput {
    todos: Array<{
        content: string;
        status: 'pending' | 'in_progress' | 'completed';
        activeForm: string;
    }>;
}
```

### MCP Tools

#### ListMcpResources
List MCP resources.
```typescript
interface ListMcpResourcesInput {
    server?: string;             // Filter by server name
}
```

#### ReadMcpResource
Read MCP resource.
```typescript
interface ReadMcpResourceInput {
    server: string;              // MCP server name
    uri: string;                 // Resource URI
}
```

#### MCP
Call MCP tool directly.
```typescript
interface McpInput {
    [key: string]: unknown;      // Tool-specific inputs
}
```

## Custom Tool Creation

### tool() Function
```typescript
import { tool } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';

const myTool = tool(
    'tool_name',                 // Tool name
    'Tool description',          // What it does
    {
        // Zod schema for inputs
        param1: z.string().describe('Parameter description'),
        param2: z.number().optional()
    },
    async ({ param1, param2 }) => {
        // Implementation
        return { output: 'Result' };
    }
);
```

### createSdkMcpServer() Function
```typescript
import { createSdkMcpServer } from '@anthropic-ai/claude-agent-sdk';

const server = createSdkMcpServer({
    name: 'my-server',
    version: '1.0.0',
    tools: [myTool, anotherTool]
});

// Use in options:
query({
    prompt: '...',
    options: {
        mcpServers: {
            'my-server': server
        }
    }
});
```

## Hook System

### Hook Events
```typescript
type HookEvent = 
    | 'PreToolUse'       // Before tool execution
    | 'PostToolUse'      // After tool execution
    | 'Notification'     // Notification message
    | 'UserPromptSubmit' // User submitted input
    | 'SessionStart'     // Session started
    | 'SessionEnd'       // Session ended
    | 'Stop'             // Stop requested
    | 'SubagentStop'     // Subagent stopped
    | 'PreCompact';      // Before context compaction
```

### Hook Input Types
```typescript
// All hooks have base info
interface BaseHookInput {
    session_id: string;
    transcript_path: string;
    cwd: string;
    permission_mode?: string;
}

// Tool-specific hooks
interface PreToolUseHookInput extends BaseHookInput {
    hook_event_name: 'PreToolUse';
    tool_name: string;
    tool_input: unknown;
}

interface PostToolUseHookInput extends BaseHookInput {
    hook_event_name: 'PostToolUse';
    tool_name: string;
    tool_input: unknown;
    tool_response: unknown;
}
```

### Hook Output
```typescript
interface HookJSONOutput {
    continue?: boolean;          // Continue execution
    suppressOutput?: boolean;    // Suppress output
    stopReason?: string;         // Stop reason
    decision?: 'approve' | 'block'; // Tool decision
    systemMessage?: string;      // Message to agent
    hookSpecificOutput?: {
        // Hook-specific responses
    };
}
```

## Models

### Model Options
```typescript
type Model = 
    | 'claude-sonnet-4.5'       // Best general-purpose
    | 'claude-opus'             // Best for complex reasoning
    | 'claude-haiku'            // Fastest, cheapest
    | 'sonnet'                  // Shorthand for sonnet
    | 'opus'                    // Shorthand for opus
    | 'haiku'                   // Shorthand for haiku
    | 'inherit';                // Use parent model
```

### Model Comparison
```typescript
{
    'haiku': {
        speed: 'fastest',
        cost: 'lowest',
        capability: 'good for simple tasks',
        tokens_per_second: 100
    },
    'sonnet': {
        speed: 'balanced',
        cost: 'moderate',
        capability: 'good for most tasks',
        tokens_per_second: 50
    },
    'opus': {
        speed: 'slower',
        cost: 'highest',
        capability: 'best for complex reasoning',
        tokens_per_second: 30
    }
}
```

## Permission Modes

```typescript
type PermissionMode = 
    | 'default'            // Ask user for each tool
    | 'acceptEdits'        // Auto-approve safe edits
    | 'bypassPermissions'  // Auto-approve all
    | 'plan';              // Require plan approval
```

## Usage Examples

### Basic Usage
```typescript
import { query } from '@anthropic-ai/claude-agent-sdk';

const result = query({
    prompt: 'Analyze this code',
    options: {
        model: 'claude-sonnet-4.5',
        maxTurns: 10
    }
});

for await (const message of result) {
    console.log(message);
}
```

### With Agent Definition
```typescript
const result = query({
    prompt: 'Use the analyzer agent',
    options: {
        agents: {
            'analyzer': {
                description: 'Code analyzer',
                prompt: 'You are a code analyzer...',
                tools: ['FileRead', 'Glob', 'Grep'],
                model: 'sonnet'
            }
        }
    }
});
```

### With Permission Control
```typescript
const result = query({
    prompt: 'Analyze and fix bugs',
    options: {
        permissionMode: 'plan',
        canUseTool: async (toolName, input) => {
            if (toolName === 'Bash') {
                return { behavior: 'ask' };
            }
            return { behavior: 'allow', updatedInput: input };
        },
        allowedTools: ['FileRead', 'Glob'],
        disallowedTools: ['Bash', 'FileWrite']
    }
});
```

### With Hooks
```typescript
const result = query({
    prompt: 'Do something',
    options: {
        hooks: {
            'PreToolUse': [{
                hooks: [async (input) => ({
                    continue: true,
                    systemMessage: `Using ${input.tool_name}`
                })]
            }]
        }
    }
});
```

### With MCP Servers
```typescript
const result = query({
    prompt: 'Use custom tools',
    options: {
        mcpServers: {
            'custom-server': {
                type: 'stdio',
                command: 'node',
                args: ['./server.js']
            }
        }
    }
});
```

## Error Handling

```typescript
try {
    const result = query({ prompt: 'Task' });
    
    for await (const message of result) {
        if (message.type === 'result') {
            if (message.subtype === 'success') {
                console.log('Success:', message.result);
            } else {
                console.log('Error:', message.errors);
            }
        }
    }
} catch (error) {
    console.error('Query failed:', error);
}
```

## Common Patterns

### Read-Only Analysis
```typescript
{
    allowedTools: ['FileRead', 'Glob', 'Grep', 'WebFetch'],
    disallowedTools: ['FileWrite', 'FileEdit', 'Bash']
}
```

### Code Modification
```typescript
{
    permissionMode: 'acceptEdits',
    allowedTools: ['FileRead', 'FileEdit', 'FileWrite', 'Glob', 'Grep'],
    disallowedTools: ['Bash']
}
```

### Full Access
```typescript
{
    permissionMode: 'bypassPermissions',
    // All tools allowed by default
}
```

### Cost-Conscious
```typescript
{
    model: 'haiku',
    maxTurns: 5,
    maxBudgetUsd: 1
}
```

## Best Practices

1. Always validate tool inputs
2. Use specific models for different tasks
3. Set reasonable cost/turn limits
4. Provide clear system prompts
5. Use appropriate permission modes
6. Monitor tool usage with hooks
7. Test with sample data first
8. Document agent responsibilities
9. Handle all SDKMessage types
10. Gracefully handle errors and timeouts
