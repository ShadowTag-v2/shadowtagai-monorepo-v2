# TungstenTool Internals Mapping

**Tool:** \`TungstenTool\`
**Status:** Ant-only Hidden Tool
**Access:** Gated behind \`process.env.USER_TYPE === 'ant'\`

## Core Architecture
Based on the audit of references across the codebase (specifically in \`src/tools.ts\`, \`ToolSelector.tsx\`, and \`tmuxSocket.ts\`), TungstenTool operates as a persistent virtual terminal abstraction layer.

### 1. Tmux Socket Isolation
Unlike the standard \`BashTool\` which executes commands in isolated subprocesses, \`TungstenTool\` utilizes \`tmux\` sessions to maintain state across commands.
- It instantiates sessions using \`new-session -e\` and binds to specific sockets.
- This allows long-running processes, background tasks, and interactive prompts to survive between tool calls.

### 2. Singleton Constraints
The architecture uses a singleton virtual terminal abstraction. 
- *Limitation:* It explicitly "conflicts between agents" (\`src/constants/tools.ts\`), meaning multiple concurrent Task Agents cannot safely multiplex \`TungstenTool\` without stepping on each other's \`tmux\` state.

### 3. Live Monitoring
The tool is paired with \`TungstenLiveMonitor\` (\`src/screens/REPL.tsx\`), suggesting an active streaming view of the terminal output that allows Anthropic engineers to view the real-time execution of long-running terminal commands without waiting for process exit codes.

### 4. Telemetry and Analytics
The tool logs distinct events compared to \`BashTool\`. References in \`transcriptSearch.ts\` differentiate between standard \`BashTool\` executions and \`TungstenTool\` tool-use blocks, capturing internal-only workflow patterns separate from external users.
