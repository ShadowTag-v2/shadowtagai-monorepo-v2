# Architecture Patterns

This guide provides detailed implementation patterns for building Claude agents, with production-ready examples and best practices.

---

## Table of Contents

1. [Workflow Pattern](#workflow-pattern)
2. [Single-Agent Pattern](#single-agent-pattern)
3. [Multi-Agent Pattern](#multi-agent-pattern)
4. [Hybrid Pattern](#hybrid-pattern)
5. [Comparison Matrix](#comparison-matrix)

---

## Workflow Pattern

**Use Cases**: 80% of production scenarios

### Overview

The Workflow pattern uses deterministic, predefined sequences to handle tasks. It's the most reliable, auditable, and cost-effective approach for predictable tasks.

### Architecture

```
User Input → Classify Intent → Route to Handler → Execute Steps → Validate → Return
```

### Key Characteristics

- **Deterministic**: Same input → Same execution path
- **Auditable**: Every step is logged and traceable
- **Efficient**: Minimal token usage
- **Testable**: Easy to write comprehensive tests
- **Maintainable**: Clear structure, easy to debug

### Implementation Pattern

```xml
<agent_configuration>
  <metadata>
    <agent_name>Data Validation Workflow</agent_name>
    <pattern>workflow</pattern>
    <version>1.0.0</version>
  </metadata>

  <role>
You are a data validation agent that processes user submissions through
a defined validation pipeline. You follow a strict, deterministic workflow
to ensure data quality and compliance.
  </role>

  <workflow_definition>
Step 1: CLASSIFY INPUT TYPE
- Identify data format (CSV, JSON, XML, etc.)
- Determine validation rules to apply
- Select appropriate schema

Step 2: SCHEMA VALIDATION
- Validate against predefined schema
- Check required fields
- Verify data types

Step 3: BUSINESS RULE VALIDATION
- Apply domain-specific rules
- Check constraints and relationships
- Validate calculations

Step 4: QUALITY CHECKS
- Check for duplicates
- Validate data ranges
- Verify referential integrity

Step 5: GENERATE REPORT
- Compile validation results
- List all errors and warnings
- Provide remediation guidance

Step 6: ROUTE FOR PROCESSING
- If valid: Route to processing pipeline
- If invalid: Return to user with errors
- If partial: Flag for manual review
  </workflow_definition>

  <tools>
- schema_validator: Validate data against schema
- rule_engine: Apply business rules
- quality_checker: Run quality checks
- report_generator: Create validation reports
  </tools>

  <quality_standards>
Every validation must:
- Process all records (no partial failures)
- Generate comprehensive error reports
- Complete within 30 seconds for <10MB files
- Achieve 100% rule coverage
  </quality_standards>
</agent_configuration>
```

### TypeScript Implementation

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

interface WorkflowStep {
  name: string;
  execute: (context: any) => Promise<any>;
  validate: (result: any) => boolean;
}

class WorkflowAgent {
  private steps: WorkflowStep[];
  private systemPrompt: string;

  constructor(steps: WorkflowStep[], systemPrompt: string) {
    this.steps = steps;
    this.systemPrompt = systemPrompt;
  }

  async execute(input: any): Promise<any> {
    let context = { input, results: {} };

    for (const step of this.steps) {
      console.log(`Executing step: ${step.name}`);

      try {
        const result = await step.execute(context);

        if (!step.validate(result)) {
          throw new Error(`Validation failed for step: ${step.name}`);
        }

        context.results[step.name] = result;
      } catch (error) {
        console.error(`Error in step ${step.name}:`, error);
        throw error;
      }
    }

    return context.results;
  }
}

// Example usage
const dataValidationWorkflow = new WorkflowAgent(
  [
    {
      name: "classify_input",
      execute: async (context) => {
        const result = await query({
          prompt: `Classify this data format: ${JSON.stringify(context.input)}`,
          options: { systemPrompt: workflowPrompt },
        });
        return result;
      },
      validate: (result) => result !== null,
    },
    {
      name: "schema_validation",
      execute: async (context) => {
        // Schema validation logic
        return { valid: true, errors: [] };
      },
      validate: (result) => Array.isArray(result.errors),
    },
    // Additional steps...
  ],
  workflowPrompt,
);
```

### Python Implementation

```python
from claude_agent_sdk import query, ClaudeAgentOptions
from typing import List, Dict, Any, Callable
from dataclasses import dataclass

@dataclass
class WorkflowStep:
    name: str
    execute: Callable[[Dict[str, Any]], Any]
    validate: Callable[[Any], bool]

class WorkflowAgent:
    def __init__(self, steps: List[WorkflowStep], system_prompt: str):
        self.steps = steps
        self.system_prompt = system_prompt

    async def execute(self, input_data: Any) -> Dict[str, Any]:
        context = {"input": input_data, "results": {}}

        for step in self.steps:
            print(f"Executing step: {step.name}")

            try:
                result = await step.execute(context)

                if not step.validate(result):
                    raise ValueError(f"Validation failed for step: {step.name}")

                context["results"][step.name] = result
            except Exception as error:
                print(f"Error in step {step.name}: {error}")
                raise

        return context["results"]

# Example usage
async def classify_input(context):
    result = None
    async for message in query(
        prompt=f"Classify this data format: {context['input']}",
        options=ClaudeAgentOptions(system_prompt=workflow_prompt)
    ):
        result = message
    return result

data_validation_workflow = WorkflowAgent(
    steps=[
        WorkflowStep(
            name="classify_input",
            execute=classify_input,
            validate=lambda r: r is not None
        ),
        # Additional steps...
    ],
    system_prompt=workflow_prompt
)
```

### Best Practices

1. **Define Clear Steps**: Each step should have a single, well-defined purpose
2. **Validate Between Steps**: Check results before proceeding
3. **Log Everything**: Record every step execution and result
4. **Handle Errors Gracefully**: Provide clear error messages and recovery paths
5. **Make It Testable**: Each step should be independently testable
6. **Keep It Simple**: Don't add complexity you don't need

### When to Use Workflow

✅ **Good fit:**

- Data validation and transformation
- Report generation
- Form processing
- Standard operating procedures
- Compliance workflows
- ETL pipelines

❌ **Poor fit:**

- Exploratory research
- Unpredictable user interactions
- Creative problem-solving
- Tasks requiring adaptation

---

## Single-Agent Pattern

**Use Cases**: 15% of production scenarios

### Overview

The Single-Agent pattern uses dynamic decision-making to handle tasks with variable requirements. The agent selects tools and approaches based on context.

### Architecture

```
Agent → Evaluate Context → Select Tools → Execute → Validate → Iterate or Complete
```

### Key Characteristics

- **Adaptive**: Adjusts approach based on context
- **Contextual**: Maintains state across interactions
- **Flexible**: Handles edge cases dynamically
- **Interactive**: Can ask clarifying questions
- **Moderate Cost**: 2-5x workflow cost

### Implementation Pattern

```xml
<agent_configuration>
  <metadata>
    <agent_name>Customer Support Agent</agent_name>
    <pattern>single-agent</pattern>
    <version>1.0.0</version>
  </metadata>

  <role>
You are a customer support agent for TechCorp, specializing in resolving
technical issues, billing questions, and account management. You have 5 years
of experience and are known for patient, clear communication.
  </role>

  <core_capabilities>
Primary Capabilities:
- Diagnose technical issues through systematic questioning
- Access and modify customer account information
- Process refunds and billing adjustments
- Escalate complex issues appropriately
- Provide clear, step-by-step guidance

Available Tools:
- account_lookup(customer_id): Get customer information
- order_history(customer_id): View past orders
- process_refund(order_id, amount): Issue refunds
- create_ticket(issue_details): Escalate to specialists
- knowledge_search(query): Search help documentation
  </core_capabilities>

  <execution_philosophy>
Workflow Pattern: Dynamic Single-Agent

Core Loop:
1. Gather context → Ask clarifying questions, look up account info
2. Take action → Use appropriate tools to resolve issue
3. Verify work → Confirm resolution with customer
4. Iterate or complete → Continue until issue resolved or escalated

Default Behavior:
- Empathetic and patient
- Thorough but efficient
- Ask before taking major actions (refunds, cancellations)
  </execution_philosophy>

  <quality_standards>
Every interaction must:
- Resolve issue or provide clear next steps
- Maintain professional, empathetic tone
- Complete within company SLA (target: <5 minutes)
- Document all actions taken

Before completing:
1. Confirm customer satisfaction
2. Verify issue is fully resolved
3. Document resolution in system
  </quality_standards>

  <constraints>
Must NOT:
- Issue refunds >$500 without manager approval
- Access accounts without verification
- Make promises outside company policy
- Share sensitive customer data

Resource Limits:
- Maximum 10 tool calls per interaction
- Escalate if unable to resolve within 15 minutes
  </constraints>
</agent_configuration>
```

### TypeScript Implementation

```typescript
import { query, tool } from "@anthropic-ai/claude-agent-sdk";

interface AgentContext {
  customerId?: string;
  conversationHistory: Message[];
  issueResolved: boolean;
}

class SingleAgent {
  private systemPrompt: string;
  private tools: any[];
  private context: AgentContext;

  constructor(systemPrompt: string, tools: any[]) {
    this.systemPrompt = systemPrompt;
    this.tools = tools;
    this.context = {
      conversationHistory: [],
      issueResolved: false,
    };
  }

  async handleInteraction(userMessage: string): Promise<string> {
    this.context.conversationHistory.push({
      role: "user",
      content: userMessage,
    });

    const result = await query({
      prompt: this.buildPrompt(userMessage),
      options: {
        systemPrompt: this.systemPrompt,
        tools: this.tools,
        maxTokens: 4000,
      },
    });

    this.context.conversationHistory.push({
      role: "assistant",
      content: result,
    });

    return result;
  }

  private buildPrompt(userMessage: string): string {
    const history = this.context.conversationHistory.map((m) => `${m.role}: ${m.content}`).join("\n");

    return `
Conversation history:
${history}

Current customer message:
${userMessage}

Please respond appropriately using available tools.
    `;
  }
}

// Define tools
const accountLookupTool = tool({
  name: "account_lookup",
  description: "Look up customer account information by customer ID",
  parameters: {
    type: "object",
    properties: {
      customerId: { type: "string", description: "Customer ID" },
    },
    required: ["customerId"],
  },
  execute: async ({ customerId }) => {
    // Implementation
    return {
      /* account data */
    };
  },
});

// Create agent
const supportAgent = new SingleAgent(supportAgentPrompt, [accountLookupTool /* other tools */]);
```

### Python Implementation

```python
from claude_agent_sdk import query, ClaudeAgentOptions, tool
from typing import List, Dict, Any
from dataclasses import dataclass, field

@dataclass
class Message:
    role: str
    content: str

@dataclass
class AgentContext:
    customer_id: str = None
    conversation_history: List[Message] = field(default_factory=list)
    issue_resolved: bool = False

class SingleAgent:
    def __init__(self, system_prompt: str, tools: List[Any]):
        self.system_prompt = system_prompt
        self.tools = tools
        self.context = AgentContext()

    async def handle_interaction(self, user_message: str) -> str:
        self.context.conversation_history.append(
            Message(role="user", content=user_message)
        )

        prompt = self._build_prompt(user_message)
        result = None

        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                system_prompt=self.system_prompt,
                tools=self.tools,
                max_tokens=4000
            )
        ):
            result = message

        self.context.conversation_history.append(
            Message(role="assistant", content=result)
        )

        return result

    def _build_prompt(self, user_message: str) -> str:
        history = "\n".join([
            f"{m.role}: {m.content}"
            for m in self.context.conversation_history
        ])

        return f"""
Conversation history:
{history}

Current customer message:
{user_message}

Please respond appropriately using available tools.
        """

# Define tools
@tool
async def account_lookup(customer_id: str) -> Dict[str, Any]:
    """Look up customer account information by customer ID"""
    # Implementation
    return {}

# Create agent
support_agent = SingleAgent(
    system_prompt=support_agent_prompt,
    tools=[account_lookup]
)
```

### Best Practices

1. **Maintain Context**: Keep conversation history and state
2. **Clear Tool Descriptions**: Help agent select appropriate tools
3. **Graceful Degradation**: Handle tool failures gracefully
4. **Validation Loops**: Verify actions before finalizing
5. **Observability**: Log all decisions and tool calls
6. **Escalation Paths**: Define when to ask for help

### When to Use Single-Agent

✅ **Good fit:**

- Customer support
- Interactive problem-solving
- Code debugging and refactoring
- Research tasks (moderate complexity)
- Conversational interfaces
- Dynamic workflow execution

❌ **Poor fit:**

- Fully predictable tasks (use workflow)
- Requires parallel exploration (use multi-agent)
- Simple classification (use simple prompt)

---

## Multi-Agent Pattern

**Use Cases**: 4% of production scenarios

### Overview

The Multi-Agent pattern decomposes complex tasks into independent subtasks, each handled by a specialized subagent. An orchestrator coordinates the subagents and synthesizes results.

### Architecture

```
Orchestrator → Decompose Task → Spawn Subagents → Monitor Progress → Synthesize Results
```

### Key Characteristics

- **Parallel Execution**: 90% faster for complex research
- **Specialized Expertise**: Each agent focuses on specific domain
- **Scalable**: Handles very complex tasks
- **Independent Subtasks**: Minimal dependencies between agents
- **High Cost**: ~15x token usage vs workflow

### Implementation Pattern

```xml
<orchestrator_configuration>
  <metadata>
    <agent_name>Market Research Orchestrator</agent_name>
    <pattern>multi-agent</pattern>
    <version>1.0.0</version>
  </metadata>

  <role>
You are an orchestrator agent coordinating specialized research subagents
to conduct comprehensive market analysis. You decompose research questions
into independent subtasks and synthesize results into coherent reports.
  </role>

  <orchestration_strategy>
Task Decomposition:
1. Analyze research question
2. Identify independent dimensions to explore
3. Assign each dimension to specialized subagent
4. Define clear output format for each subagent
5. Set boundaries to prevent overlap

Subagent Types:
- competitor_analyst: Analyzes competitor landscape
- market_trends_researcher: Identifies market trends
- customer_insights_analyst: Gathers customer data
- regulatory_researcher: Reviews regulations and compliance
- financial_analyst: Analyzes financial aspects

Delegation Pattern:
- 3-5 subagents for standard research
- 5-10 subagents for comprehensive analysis
- Each gets: objective, context, tools, output format, boundaries

Synthesis Approach:
1. Wait for all subagents to complete
2. Identify overlaps and contradictions
3. Cross-reference facts across sources
4. Resolve conflicts by source quality
5. Synthesize into executive summary
  </orchestration_strategy>

  <subagent_template>
<subagent_task>
  <agent_id>{unique_identifier}</agent_id>
  <objective>{single_focused_goal}</objective>
  <context>{relevant_background}</context>
  <tools>{specific_tools_allowed}</tools>
  <output_format>
    {
      "findings": [{
        "fact": "string",
        "source": "string",
        "confidence": 0.0-1.0,
        "date": "ISO-8601"
      }],
      "summary": "string",
      "limitations": "string"
    }
  </output_format>
  <boundaries>
    - Focus ONLY on {specific_domain}
    - Do NOT overlap with {other_agents}
    - Complete within {time_limit}
  </boundaries>
</subagent_task>
  </subagent_template>

  <quality_standards>
Final report must:
- Synthesize ALL subagent findings
- Resolve contradictions explicitly
- Cite sources for every fact
- Note confidence levels
- Identify research gaps

Before finalizing:
1. Cross-reference facts across subagents
2. Verify no contradictions remain unresolved
3. Ensure comprehensive coverage
4. Validate all citations
  </quality_standards>
</orchestrator_configuration>
```

### TypeScript Implementation

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

interface SubagentTask {
  agentId: string;
  objective: string;
  context: string;
  tools: any[];
  outputFormat: any;
  boundaries: string[];
}

interface SubagentResult {
  agentId: string;
  findings: any[];
  summary: string;
  limitations: string;
}

class MultiAgentOrchestrator {
  private orchestratorPrompt: string;
  private subagentPromptTemplate: string;

  constructor(orchestratorPrompt: string, subagentPromptTemplate: string) {
    this.orchestratorPrompt = orchestratorPrompt;
    this.subagentPromptTemplate = subagentPromptTemplate;
  }

  async executeResearch(researchQuestion: string): Promise<any> {
    // Step 1: Decompose task
    const tasks = await this.decompose task(researchQuestion);

    // Step 2: Execute subagents in parallel
    const results = await Promise.all(
      tasks.map(task => this.executeSubagent(task))
    );

    // Step 3: Synthesize results
    const finalReport = await this.synthesizeResults(results);

    return finalReport;
  }

  private async decomposeTask(researchQuestion: string): Promise<SubagentTask[]> {
    const result = await query({
      prompt: `
Decompose this research question into independent subtasks:
${researchQuestion}

Return a JSON array of subtasks with: agentId, objective, context, boundaries
      `,
      options: { systemPrompt: this.orchestratorPrompt }
    });

    return JSON.parse(result);
  }

  private async executeSubagent(task: SubagentTask): Promise<SubagentResult> {
    const subagentPrompt = this.buildSubagentPrompt(task);

    const result = await query({
      prompt: task.objective,
      options: {
        systemPrompt: subagentPrompt,
        tools: task.tools,
        maxTokens: 8000
      }
    });

    return {
      agentId: task.agentId,
      ...JSON.parse(result)
    };
  }

  private buildSubagentPrompt(task: SubagentTask): string {
    return this.subagentPromptTemplate
      .replace("{agent_id}", task.agentId)
      .replace("{objective}", task.objective)
      .replace("{context}", task.context)
      .replace("{boundaries}", task.boundaries.join("\n"));
  }

  private async synthesizeResults(results: SubagentResult[]): Promise<any> {
    const synthesisPrompt = `
Synthesize these research findings into a comprehensive report:

${JSON.stringify(results, null, 2)}

Identify overlaps, resolve contradictions, and create executive summary.
    `;

    const finalReport = await query({
      prompt: synthesisPrompt,
      options: {
        systemPrompt: this.orchestratorPrompt,
        maxTokens: 16000
      }
    });

    return JSON.parse(finalReport);
  }
}

// Usage
const orchestrator = new MultiAgentOrchestrator(
  orchestratorPrompt,
  subagentPromptTemplate
);

const report = await orchestrator.executeResearch(
  "Analyze the competitive landscape for AI coding assistants in 2025"
);
```

### Python Implementation

```python
from claude_agent_sdk import query, ClaudeAgentOptions
from typing import List, Dict, Any
from dataclasses import dataclass
import asyncio
import json

@dataclass
class SubagentTask:
    agent_id: str
    objective: str
    context: str
    tools: List[Any]
    output_format: Dict[str, Any]
    boundaries: List[str]

@dataclass
class SubagentResult:
    agent_id: str
    findings: List[Dict[str, Any]]
    summary: str
    limitations: str

class MultiAgentOrchestrator:
    def __init__(self, orchestrator_prompt: str, subagent_prompt_template: str):
        self.orchestrator_prompt = orchestrator_prompt
        self.subagent_prompt_template = subagent_prompt_template

    async def execute_research(self, research_question: str) -> Dict[str, Any]:
        # Step 1: Decompose task
        tasks = await self.decompose_task(research_question)

        # Step 2: Execute subagents in parallel
        results = await asyncio.gather(*[
            self.execute_subagent(task) for task in tasks
        ])

        # Step 3: Synthesize results
        final_report = await self.synthesize_results(results)

        return final_report

    async def decompose_task(self, research_question: str) -> List[SubagentTask]:
        prompt = f"""
Decompose this research question into independent subtasks:
{research_question}

Return a JSON array of subtasks with: agentId, objective, context, boundaries
        """

        result = None
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(system_prompt=self.orchestrator_prompt)
        ):
            result = message

        tasks_data = json.loads(result)
        return [SubagentTask(**task) for task in tasks_data]

    async def execute_subagent(self, task: SubagentTask) -> SubagentResult:
        subagent_prompt = self._build_subagent_prompt(task)

        result = None
        async for message in query(
            prompt=task.objective,
            options=ClaudeAgentOptions(
                system_prompt=subagent_prompt,
                tools=task.tools,
                max_tokens=8000
            )
        ):
            result = message

        result_data = json.loads(result)
        return SubagentResult(agent_id=task.agent_id, **result_data)

    def _build_subagent_prompt(self, task: SubagentTask) -> str:
        return self.subagent_prompt_template.format(
            agent_id=task.agent_id,
            objective=task.objective,
            context=task.context,
            boundaries="\n".join(task.boundaries)
        )

    async def synthesize_results(self, results: List[SubagentResult]) -> Dict[str, Any]:
        synthesis_prompt = f"""
Synthesize these research findings into a comprehensive report:

{json.dumps([r.__dict__ for r in results], indent=2)}

Identify overlaps, resolve contradictions, and create executive summary.
        """

        final_report = None
        async for message in query(
            prompt=synthesis_prompt,
            options=ClaudeAgentOptions(
                system_prompt=self.orchestrator_prompt,
                max_tokens=16000
            )
        ):
            final_report = message

        return json.loads(final_report)

# Usage
orchestrator = MultiAgentOrchestrator(
    orchestrator_prompt=orchestrator_prompt,
    subagent_prompt_template=subagent_prompt_template
)

report = await orchestrator.execute_research(
    "Analyze the competitive landscape for AI coding assistants in 2025"
)
```

### Best Practices

1. **True Independence**: Ensure subtasks are truly independent
2. **Clear Boundaries**: Define what each subagent should/shouldn't do
3. **Conflict Resolution**: Plan how to handle contradictions
4. **Cost Justification**: Ensure task value warrants 15x cost
5. **Parallel Execution**: Maximize parallelization benefits
6. **Comprehensive Synthesis**: Don't just concatenate results

### When to Use Multi-Agent

✅ **Good fit:**

- Comprehensive market research
- Large codebase analysis
- Multi-domain problem solving
- Parallel exploration tasks
- Complex decision support

❌ **Poor fit:**

- Sequential dependencies
- Cost-sensitive tasks
- Real-time requirements
- Simple research

---

## Hybrid Pattern

**Recommended for Production**

### Overview

The Hybrid pattern combines deterministic workflows for common cases (80-90%) with dynamic agent behavior for edge cases (10-20%). This provides the reliability of workflows with the flexibility of agents.

### Architecture

```
Input → Classify →
  ├─ Common Case (80%) → Workflow → Response
  └─ Edge Case (20%) → Agent → Response
```

### Implementation

```typescript
class HybridAgent {
  private workflows: Map<string, Workflow>;
  private dynamicAgent: SingleAgent;

  async handle(input: any): Promise<any> {
    // Classify input
    const category = await this.classifyInput(input);

    // Route to workflow or agent
    if (this.workflows.has(category)) {
      return await this.workflows.get(category).execute(input);
    } else {
      return await this.dynamicAgent.handleInteraction(input);
    }
  }

  private async classifyInput(input: any): Promise<string> {
    // Fast classification logic
    return category;
  }
}
```

### Benefits

- **Cost Control**: 80-90% handled by cheap workflows
- **Flexibility**: Edge cases handled dynamically
- **Reliability**: Predictable for common cases
- **Scalability**: Easy to optimize common paths

---

## Comparison Matrix

| Aspect               | Workflow  | Single-Agent | Multi-Agent | Hybrid |
| -------------------- | --------- | ------------ | ----------- | ------ |
| **Use Cases**        | 80%       | 15%          | 4%          | 1%     |
| **Cost**             | $         | $$$          | $$$$        | $$     |
| **Speed**            | Fast      | Medium       | Slow        | Fast   |
| **Flexibility**      | Low       | High         | Very High   | Medium |
| **Complexity**       | Low       | Medium       | High        | Medium |
| **Testability**      | Excellent | Good         | Fair        | Good   |
| **Observability**    | Excellent | Good         | Complex     | Good   |
| **Production Ready** | ✅        | ✅           | ⚠️          | ✅     |

---

## Pattern Selection Guidelines

1. **Start Simple**: Always begin with the simplest pattern
2. **Measure First**: Don't add complexity without data
3. **Cost Awareness**: Understand token implications
4. **Test Thoroughly**: Validate before production
5. **Monitor Always**: Observe actual usage patterns
6. **Iterate Based on Data**: Optimize based on metrics

---

**Remember**: The best pattern is the simplest one that meets your requirements. Start simple, add complexity only when justified.
