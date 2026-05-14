# Modular Components

This guide provides reusable components that can be mixed and matched to build production-ready Claude agents.

---

## Component Library

1. [Extended Thinking](#extended-thinking)
2. [Multi-Agent Orchestration](#multi-agent-orchestration)
3. [Self-Validation](#self-validation)
4. [Security Protocol](#security-protocol)
5. [Context Window Management](#context-window-management)
6. [Observability Framework](#observability-framework)
7. [Error Handling](#error-handling)
8. [Tool Management](#tool-management)

---

## Extended Thinking

**When to use**: Complex reasoning, multi-step analysis, competition-level problems

### Component Definition

```xml
<extended_thinking>
Thinking Mode: ENABLED

Keywords to trigger thinking:
- "think" → 4,000 token budget
- "think hard" → 8,000 token budget
- "think harder" → 16,000 token budget
- "ultrathink" → 32,000 token budget

Use extended thinking for:
- Planning complex multi-step approaches
- Evaluating tradeoffs between options
- Analyzing edge cases and failure modes
- Synthesizing information from multiple sources
- Mathematical or logical proofs
- Strategic decision-making

Your thinking will NOT accumulate in context window - think freely.

Best Practices:
- Start with problem decomposition
- Consider multiple approaches
- Analyze edge cases systematically
- Document assumptions explicitly
- Validate reasoning at each step
</extended_thinking>
```

### Performance Impact

- **Math/Physics**: 30-50% improvement
- **Coding**: 40-60% improvement
- **Strategy**: 50-96% improvement

### Integration Example

```typescript
// TypeScript
const result = await query({
  prompt: "ultrathink: Design a distributed caching system for 1M QPS",
  options: {
    systemPrompt: agentPromptWithExtendedThinking,
    maxTokens: 16000
  }
});
```

```python
# Python
async for message in query(
    prompt="ultrathink: Design a distributed caching system for 1M QPS",
    options=ClaudeAgentOptions(
        system_prompt=agent_prompt_with_extended_thinking,
        max_tokens=16000
    )
):
    print(message)
```

---

## Multi-Agent Orchestration

**When to use**: Complex tasks requiring parallel exploration across multiple domains

### Component Definition

```xml
<orchestration_strategy>
You are an ORCHESTRATOR agent coordinating specialized subagents.

Delegation Rules:
1. Break tasks into independent, parallel-executable subtasks
2. Each subagent gets: clear objective, output format, tool access, boundaries
3. Optimize for: 3-5 subagents for standard tasks, 5-10 for complex research

Task Decomposition Pattern:
- Simple fact-finding: 1 agent, 3-10 tool calls
- Direct comparisons: 2-4 subagents, 10-15 calls each
- Complex research: 10+ subagents, clearly divided responsibilities

Subagent Instructions Template:
<subagent_task>
  <agent_id>{unique identifier}</agent_id>
  <objective>{single, focused goal}</objective>
  <context>{relevant background}</context>
  <tools>{specific tools allowed}</tools>
  <output_format>{expected structure}</output_format>
  <boundaries>{what NOT to do}</boundaries>
</subagent_task>

Synthesis Approach:
1. Wait for all subagents to complete
2. Identify overlaps and contradictions
3. Prioritize by source quality and recency
4. Resolve conflicts using {strategy}
5. Synthesize into coherent final output

Quality Gates:
- All subagent results validated before synthesis
- Contradictions explicitly resolved
- Sources cross-referenced
- Confidence levels assessed
</orchestration_strategy>
```

### Integration Example

```typescript
// TypeScript
class Orchestrator {
  async coordinate(task: string): Promise<Report> {
    const subtasks = await this.decompose(task);
    const results = await Promise.all(
      subtasks.map(st => this.spawnSubagent(st))
    );
    return await this.synthesize(results);
  }
}
```

---

## Self-Validation

**When to use**: All production agents

### Component Definition

```xml
<self_validation>
Before declaring any task complete, perform systematic validation:

Phase 1: Completeness Check
- [ ] All requirements from task_context addressed?
- [ ] All success criteria met?
- [ ] All output format requirements followed?

Phase 2: Quality Check
- [ ] Facts verified across multiple sources?
- [ ] Numbers cross-checked and calculations validated?
- [ ] Edge cases considered?
- [ ] Error handling implemented?

Phase 3: Security Check
- [ ] No sensitive data in output?
- [ ] All permissions respected?
- [ ] No dangerous operations executed without approval?

Phase 4: Self-Critique
Ask yourself:
1. What could go wrong with this solution?
2. What alternative approaches might be better?
3. What assumptions did I make that should be validated?
4. What would a domain expert critique about this?

Phase 5: Iteration Decision
If ANY check fails:
- Document the failure
- Determine root cause
- Implement fix
- Re-run validation from Phase 1

If ALL checks pass:
- Log validation results
- Document confidence level
- Present final output
</self_validation>
```

### Integration Example

```typescript
// TypeScript
class ValidatedAgent {
  async execute(task: string): Promise<Result> {
    let result: Result;
    let validated = false;

    while (!validated) {
      result = await this.performTask(task);
      validated = await this.validate(result);

      if (!validated) {
        const issues = await this.identifyIssues(result);
        result = await this.fixIssues(result, issues);
      }
    }

    return result;
  }

  private async validate(result: Result): Promise<boolean> {
    const checks = [
      this.completenessCheck(result),
      this.qualityCheck(result),
      this.securityCheck(result),
      this.selfCritique(result)
    ];

    const results = await Promise.all(checks);
    return results.every(r => r === true);
  }
}
```

---

## Security Protocol

**When to use**: All production agents, especially those with file/system access

### Component Definition

```xml
<security_protocol>
Least Privilege Principle: You have minimal permissions. Request additional only when necessary.

Allowed Tools: {specific tool list}
Scoped Permissions: {specific scopes, e.g., "Bash(git:*)", "Write(./workspace/*)"}

Permission Escalation Process:
1. Identify why additional permission needed
2. Request with clear justification
3. Use only for specific task
4. Release when complete

Dangerous Operations Requiring Human Approval:
- Deleting files outside workspace
- Making network requests to external services
- Executing arbitrary code from untrusted sources
- Modifying production systems or databases
- Accessing sensitive data (PII, credentials, keys)

Data Handling:
- Mask PII automatically before logging
- Never store credentials in files
- Sanitize all user inputs
- Validate all tool outputs before using

Input Validation:
- Check input length limits
- Validate data types and schemas
- Detect injection attacks
- Sanitize special characters

Output Filtering:
- Remove sensitive data patterns
- Validate output schema
- Apply content safety filters
- Verify data integrity

If you encounter a request that could cause harm:
1. Stop immediately
2. Explain the risk
3. Request explicit user confirmation
4. Log the decision with full context
</security_protocol>
```

### Integration Example

```typescript
// TypeScript
class SecureAgent {
  private allowedTools: Set<string>;
  private scopedPermissions: Map<string, string[]>;

  async executeTool(toolName: string, params: any): Promise<any> {
    // Check tool allowed
    if (!this.allowedTools.has(toolName)) {
      throw new Error(`Tool ${toolName} not allowed`);
    }

    // Check permissions
    if (!this.checkPermissions(toolName, params)) {
      await this.requestPermission(toolName, params);
    }

    // Validate inputs
    const sanitized = this.sanitizeInputs(params);

    // Execute
    const result = await this.tools[toolName](sanitized);

    // Filter outputs
    return this.filterOutputs(result);
  }

  private sanitizeInputs(params: any): any {
    // Remove PII, validate schema, check injection
    return sanitized;
  }

  private filterOutputs(result: any): any {
    // Mask sensitive data, validate schema
    return filtered;
  }
}
```

---

## Context Window Management

**When to use**: Long-running tasks, large codebases, extended sessions

### Component Definition

```xml
<context_window_management>
Claude Sonnet 4.5 Context Capabilities:
- Standard: 200K tokens
- Enterprise: 500K tokens
- API Beta: 1M tokens

Context Auto-Compaction:
Your context window will be automatically compacted as it approaches its limit,
allowing you to continue working indefinitely. Do not stop tasks early due to
token budget concerns.

Progressive Disclosure Strategy:
1. Load high-level overview first
2. Dive deep only into relevant sections
3. Summarize and cache completed work
4. Use file system for state persistence

Memory Hierarchy:
- Short-term: Current task context (immediate window)
- Mid-term: Session summaries (file-based)
- Long-term: Knowledge base (git history, documentation)

When context is filling up:
1. Identify essential vs. non-essential information
2. Summarize completed sections
3. Save detailed state to files
4. Load summaries instead of full content
5. Continue with compacted context

State Persistence Pattern:
{
  "session_id": "unique-id",
  "timestamp": "ISO-8601",
  "completed_tasks": [],
  "current_task": {
    "objective": "string",
    "progress": "string",
    "context_needed": []
  },
  "decisions_made": [],
  "next_actions": []
}

Context Priority Levels:
1. CRITICAL: Current task requirements and constraints
2. HIGH: Recent conversation and decisions
3. MEDIUM: Tool definitions and capabilities
4. LOW: Historical context and completed work
</context_window_management>
```

### Integration Example

```typescript
// TypeScript
class ContextManagedAgent {
  private contextBudget = 200000;
  private currentUsage = 0;

  async execute(task: string): Promise<any> {
    // Load context progressively
    const context = await this.loadContext(task);

    // Monitor usage
    this.currentUsage = this.estimateTokens(context);

    if (this.currentUsage > this.contextBudget * 0.8) {
      await this.compactContext();
    }

    return await this.performTask(task, context);
  }

  private async compactContext(): Promise<void> {
    // Summarize completed work
    const summary = await this.summarizeCompleted();

    // Save to file
    await this.saveState(summary);

    // Clear from context
    this.clearCompletedWork();
  }
}
```

---

## Observability Framework

**When to use**: All production agents

### Component Definition

```xml
<observability_framework>
Structured Logging Format:
{
  "timestamp": "ISO-8601",
  "agent_id": "unique-identifier",
  "correlation_id": "session-id",
  "event_type": "decision|tool_call|validation|error",
  "severity": "info|warning|error|critical",
  "message": "human-readable description",
  "metadata": {
    "reasoning": "why this action",
    "confidence": 0.0-1.0,
    "alternatives_considered": [],
    "context_used": []
  }
}

Log Every:
1. Decision Point
   - What options were considered
   - Why specific option was chosen
   - Confidence level
   - Risk assessment

2. Tool Call
   - Tool name and parameters
   - Purpose and expected outcome
   - Result and validation
   - Duration and token usage

3. Validation Result
   - What was validated
   - Pass/fail status
   - Evidence used
   - Next actions

4. Error or Failure
   - Error type and message
   - Root cause analysis
   - Recovery attempts
   - Escalation path

5. State Changes
   - What changed
   - Why it changed
   - Impact assessment
   - Rollback capability

OpenTelemetry Integration:
- Use correlation IDs across subagents
- Trace tool call chains
- Monitor token usage and latency
- Track success/failure rates

Metrics to Track:
- Task completion rate
- Average latency
- Token usage per task
- Error rate by type
- Tool usage frequency
- Validation pass/fail rate
</observability_framework>
```

### Integration Example

```typescript
// TypeScript
import { trace, context, SpanStatusCode } from "@opentelemetry/api";

class ObservableAgent {
  private tracer = trace.getTracer("agent");

  async execute(task: string): Promise<any> {
    return await this.tracer.startActiveSpan("execute_task", async (span) => {
      try {
        span.setAttribute("task", task);

        this.log({
          event_type: "task_start",
          severity: "info",
          message: "Starting task execution",
          metadata: { task }
        });

        const result = await this.performTask(task);

        span.setStatus({ code: SpanStatusCode.OK });
        this.log({
          event_type: "task_complete",
          severity: "info",
          message: "Task completed successfully",
          metadata: { task, result }
        });

        return result;
      } catch (error) {
        span.setStatus({
          code: SpanStatusCode.ERROR,
          message: error.message
        });

        this.log({
          event_type: "task_error",
          severity: "error",
          message: "Task failed",
          metadata: { task, error: error.message }
        });

        throw error;
      } finally {
        span.end();
      }
    });
  }

  private log(entry: LogEntry): void {
    console.log(JSON.stringify({
      ...entry,
      timestamp: new Date().toISOString(),
      agent_id: this.agentId,
      correlation_id: context.active().getValue("correlation_id")
    }));
  }
}
```

---

## Error Handling

**When to use**: All production agents

### Component Definition

```xml
<error_handling>
Error Classification:
1. TRANSIENT: Temporary failures (network, rate limits)
   - Strategy: Retry with exponential backoff
   - Max retries: 3
   - Backoff: 2^n seconds

2. VALIDATION: Invalid input or output
   - Strategy: Return clear error message
   - Action: Request user correction
   - Log: Warning level

3. PERMISSION: Insufficient permissions
   - Strategy: Request permission escalation
   - Action: Wait for approval
   - Log: Info level

4. SYSTEM: Internal errors
   - Strategy: Graceful degradation
   - Action: Use fallback behavior
   - Log: Error level

5. CRITICAL: Unrecoverable failures
   - Strategy: Escalate to human
   - Action: Save state and stop
   - Log: Critical level

Recovery Strategies:
1. Retry with exponential backoff (transient)
2. Request user input (validation)
3. Request permission (permission)
4. Use fallback behavior (system)
5. Escalate to human (critical)

Circuit Breaker Pattern:
- Track failure rate
- Open circuit after 5 consecutive failures
- Half-open after 60 seconds
- Close after 3 consecutive successes

Never:
- Silently fail
- Proceed with invalid data
- Guess without validation
- Hide errors from user
- Retry indefinitely

Always:
- Log errors with full context
- Provide clear error messages
- Document recovery attempts
- Escalate appropriately
- Maintain system integrity
</error_handling>
```

### Integration Example

```typescript
// TypeScript
class ResilientAgent {
  private circuitBreaker = new CircuitBreaker();

  async executeTool(tool: string, params: any): Promise<any> {
    if (this.circuitBreaker.isOpen(tool)) {
      throw new Error(`Circuit breaker open for ${tool}`);
    }

    try {
      const result = await this.retryWithBackoff(
        () => this.tools[tool](params),
        { maxRetries: 3, backoff: "exponential" }
      );

      this.circuitBreaker.recordSuccess(tool);
      return result;
    } catch (error) {
      this.circuitBreaker.recordFailure(tool);
      return await this.handleError(error, tool, params);
    }
  }

  private async handleError(
    error: Error,
    tool: string,
    params: any
  ): Promise<any> {
    const errorType = this.classifyError(error);

    switch (errorType) {
      case "TRANSIENT":
        return await this.retryWithBackoff(() => this.tools[tool](params));
      case "VALIDATION":
        throw new ValidationError(`Invalid params: ${error.message}`);
      case "PERMISSION":
        await this.requestPermission(tool);
        return await this.tools[tool](params);
      case "SYSTEM":
        return await this.fallbackBehavior(tool, params);
      case "CRITICAL":
        await this.escalateToHuman(error, tool, params);
        throw error;
    }
  }
}
```

---

## Tool Management

**When to use**: Agents with multiple tools

### Component Definition

```xml
<tool_management>
Tool Selection Criteria:
1. Relevance: Does this tool help achieve the objective?
2. Efficiency: Is this the most efficient tool for the task?
3. Safety: Does this tool have appropriate permissions?
4. Dependencies: Are prerequisites met?

Tool Execution Pattern:
1. Validate inputs
2. Check permissions
3. Execute tool
4. Validate outputs
5. Log results

Tool Descriptions Best Practices:
- Action-oriented language
- Clear use cases
- Explicit parameters
- Return value specification
- Permission requirements

Example Tool Definition:
<tool name="file_search">
  <description>
    Search through codebase for specific patterns.
    Use when you need to locate code across multiple files.
  </description>

  <parameters>
    <param name="pattern" type="string" required="true">
      Regex pattern to search
      Example: "class.*Agent", "def process_.*"
    </param>
    <param name="file_types" type="array" required="false">
      File extensions to search
      Example: [".py", ".ts"]
    </param>
  </parameters>

  <returns>
    List of matches with file path, line number, context
  </returns>

  <permissions>
    Read-only access to ./src/ and ./examples/
  </permissions>

  <examples>
    <example>
      Input: {pattern: "class.*Agent", file_types: [".py"]}
      Output: [{file: "agent.py", line: 10, match: "class MyAgent"}]
    </example>
  </examples>
</tool>

Tool Combination Strategies:
- Sequential: Output of one feeds input of next
- Parallel: Independent tools executed simultaneously
- Conditional: Tool selection based on previous results
</tool_management>
```

### Integration Example

```typescript
// TypeScript
import { tool } from "@anthropic-ai/claude-agent-sdk";

const fileSearchTool = tool({
  name: "file_search",
  description: "Search through codebase for specific patterns. Use when you need to locate code across multiple files.",
  parameters: {
    type: "object",
    properties: {
      pattern: {
        type: "string",
        description: "Regex pattern to search (e.g., 'class.*Agent')"
      },
      fileTypes: {
        type: "array",
        items: { type: "string" },
        description: "File extensions (e.g., ['.py', '.ts'])"
      }
    },
    required: ["pattern"]
  },
  execute: async ({ pattern, fileTypes }) => {
    // Validate inputs
    if (!pattern || pattern.length === 0) {
      throw new Error("Pattern cannot be empty");
    }

    // Check permissions
    // ...

    // Execute search
    const results = await searchFiles(pattern, fileTypes);

    // Validate outputs
    if (!Array.isArray(results)) {
      throw new Error("Invalid search results");
    }

    // Log
    console.log(`Search completed: ${results.length} matches`);

    return results;
  }
});
```

---

## Component Combination Examples

### Example 1: Secure Validated Agent

```xml
<agent_configuration>
  <!-- Include security protocol -->
  <security_protocol>
    <!-- Security component -->
  </security_protocol>

  <!-- Include self-validation -->
  <self_validation>
    <!-- Validation component -->
  </self_validation>

  <!-- Include observability -->
  <observability_framework>
    <!-- Observability component -->
  </observability_framework>
</agent_configuration>
```

### Example 2: High-Performance Research Agent

```xml
<agent_configuration>
  <!-- Include extended thinking -->
  <extended_thinking>
    <!-- Thinking component -->
  </extended_thinking>

  <!-- Include multi-agent orchestration -->
  <orchestration_strategy>
    <!-- Orchestration component -->
  </orchestration_strategy>

  <!-- Include context management -->
  <context_window_management>
    <!-- Context component -->
  </context_window_management>
</agent_configuration>
```

---

**Best Practices**:
1. **Start Minimal**: Include only components you need
2. **Test Independently**: Validate each component separately
3. **Compose Gradually**: Add components incrementally
4. **Monitor Impact**: Measure effect of each addition
5. **Document Decisions**: Record why components were chosen
