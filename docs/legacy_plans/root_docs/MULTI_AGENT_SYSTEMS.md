# Multi-Agent Systems for Code Generation

## Overview

This document covers multi-agent frameworks and collaboration patterns for software engineering tasks. These systems leverage multiple AI agents working together to generate, test, debug, and optimize code, often outperforming single-agent approaches by 5-10% on benchmarks.

**Related Documents:**

- [ADVANCED_PROMPTING.md](ADVANCED_PROMPTING.md) - RCR and debate techniques
- [CODE_BENCHMARKS.md](CODE_BENCHMARKS.md) - Evaluation datasets
- [EVALUATION_METRICS.md](EVALUATION_METRICS.md) - Performance measurement

---

## Table of Contents

1. [Introduction to Multi-Agent Code Collaboration](#introduction)
2. [Key Frameworks (2025)](#key-frameworks-2025)
3. [AgentCoder Deep Dive](#agentcoder-deep-dive)
4. [Collaboration Patterns](#collaboration-patterns)
5. [Implementation Examples](#implementation-examples)
6. [Best Practices](#best-practices)

---

## Introduction

### Why Multi-Agent Systems?

**Single-Agent Limitations:**

- Hallucinations in code generation
- Missed edge cases
- Lack of self-correction
- No quality validation

**Multi-Agent Advantages:**

- **Specialization**: Agents focus on specific roles (coding, testing, review)
- **Debate**: Multiple perspectives reduce errors
- **Iteration**: Self-correction through feedback loops
- **Validation**: Built-in testing and verification

### Core Principles

```
1. Role Separation: Coder | Tester | Reviewer | Optimizer
2. Communication: Structured message passing
3. Iteration: Feedback loops until quality threshold
4. Consensus: Voting or arbitration for final decisions
```

---

## Key Frameworks (2025)

### Comprehensive Comparison

| Framework      | Focus                 | Architecture              | Key Features                                                                     | Best For                          |
| -------------- | --------------------- | ------------------------- | -------------------------------------------------------------------------------- | --------------------------------- |
| **MetaGPT**    | Full SDLC simulation  | SOPs + role-based         | Product manager, architect, engineer roles; MGX for natural language programming | End-to-end app development        |
| **AutoGen**    | Conversational agents | Dynamic groups            | Tool use, human-in-loop, flexible conversations                                  | Collaborative coding, debugging   |
| **CrewAI**     | Task orchestration    | Hierarchical              | Task delegation, easy integration                                                | SE pipelines, planning            |
| **LangGraph**  | Stateful workflows    | Graph-based               | Cycles/loops, complex interactions                                               | Custom multi-agent apps           |
| **AgentCoder** | Code generation       | Producer-Tester-Optimizer | Self-optimization loops, test-driven                                             | Benchmark performance (HumanEval) |

### Framework Selection Guide

```python
def select_framework(use_case, complexity, integration_needs):
    if use_case == "production_app" and complexity == "high":
        return "MetaGPT"
    elif use_case == "research" and integration_needs == "flexible":
        return "AutoGen"
    elif use_case == "pipeline" and complexity == "medium":
        return "CrewAI"
    elif use_case == "custom_workflow":
        return "LangGraph"
    elif use_case == "code_optimization":
        return "AgentCoder"
```

---

## AgentCoder Deep Dive

### Overview

**AgentCoder** (2023-2025) is a specialized multi-agent framework for code generation using three collaborative agents: Programmer, Test Designer, and Test Executor.

### Architecture

```
┌─────────────────────────────────────────────────────┐
│              AgentCoder Workflow                     │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐                                   │
│  │   Task Input │                                   │
│  └──────┬───────┘                                   │
│         │                                           │
│         ▼                                           │
│  ┌──────────────────┐                              │
│  │ Programmer Agent │  (CoT-based generation)      │
│  │  - Initial code  │                              │
│  └──────┬───────────┘                              │
│         │                                           │
│         ▼                                           │
│  ┌──────────────────────┐                          │
│  │ Test Designer Agent  │  (Independent test gen)  │
│  │  - Basic tests       │                          │
│  │  - Edge cases        │                          │
│  │  - Large scale       │                          │
│  └──────┬───────────────┘                          │
│         │                                           │
│         ▼                                           │
│  ┌──────────────────────┐                          │
│  │ Test Executor Agent  │  (Run in local env)      │
│  │  - Execute tests     │                          │
│  │  - Collect feedback  │                          │
│  └──────┬───────────────┘                          │
│         │                                           │
│         ├──────► Pass? ──► Output final code       │
│         │                                           │
│         └──────► Fail? ──► Back to Programmer      │
│                          (with error feedback)      │
│                                                      │
│  [Iterate until pass or budget exhausted]          │
└─────────────────────────────────────────────────────┘
```

### Agent Roles

#### 1. Programmer Agent

**Responsibilities:**

- Generate initial code using Chain-of-Thought
- Refine code based on test feedback
- Implement fixes for failing tests

**Prompt Template:**

```
You are a software programmer.
Complete the function using Chain-of-Thought:

1. Understand and Clarify: Analyze the task
2. Algorithm/Method Selection: Choose efficient approach
3. Pseudocode Creation: Outline steps
4. Code Generation: Implement in Python

Input Code Snippet:
{task_description}

[If refinement round:]
Previous code failed with errors: {error_messages}
Refine the code to fix them.
```

#### 2. Test Designer Agent

**Responsibilities:**

- Create comprehensive test cases independently
- Cover basic, edge, and large-scale scenarios
- No access to implementation (avoids overfitting)

**Prompt Template:**

```
As a tester, create comprehensive test cases:

1. Basic Test Cases:
   - Verify fundamental functionality under normal conditions

2. Edge Test Cases:
   - Extreme or unusual conditions
   - Boundary values, empty inputs, special characters

3. Large Scale Test Cases:
   - Performance and scalability
   - Large data samples

Input (function signature only):
{function_signature}

Do NOT see the implementation. Create tests independently.
```

#### 3. Test Executor Agent

**Responsibilities:**

- Run tests in isolated environment
- Collect execution feedback (pass/fail, errors)
- Provide detailed error messages to Programmer

**Process:**

```python
def execute_tests(code, tests):
    errors = []
    local_env = {}
    try:
        exec(code, local_env)  # Load function
        for test in tests:
            exec(test, local_env)  # Run assertions
    except AssertionError as e:
        errors.append(f"AssertionError: {e}")
    except Exception as e:
        errors.append(f"RuntimeError: {e}")
    return errors
```

### Performance Results

| Benchmark      | Metric      | AgentCoder | GPT-4 Baseline | Improvement |
| -------------- | ----------- | ---------- | -------------- | ----------- |
| **HumanEval**  | Pass@1      | 96.3%      | ~85%           | +11.3%      |
| **MBPP**       | Pass@1      | 91.8%      | ~80%           | +11.8%      |
| **Token Cost** | Tokens/task | Lower      | Baseline       | -15-20%     |

**Key Advantages:**

- Independent test generation reduces bias
- Iterative refinement catches edge cases
- Lower cost than naive sampling approaches

### Integration with RCR

**Adapted for Code:**

```
1. REFLECT: Programmer reviews own code for bugs
2. CRITIQUE: Reviews test failures and error messages
3. REFINE: Updates code with fixes and optimizations

Enhanced Prompt:
"Reflect on your previous code, identify bugs based on test failures.
Critique the approach - are there efficiency issues?
Refine with corrected implementation, explaining changes."
```

---

## Collaboration Patterns

### 1. Pipeline Pattern

**Structure:** Sequential agent chain

```
Input → Agent A → Agent B → Agent C → Output

Example (Code Documentation):
Task → Analyzer → Documenter → Reviewer → Final Docs
```

**Use Cases:**

- Linear workflows
- Clear dependencies
- Document generation

**Pros/Cons:**

- ✓ Simple, easy to debug
- ✗ No parallelization
- ✗ Bottlenecks if one agent slow

### 2. Debate Pattern

**Structure:** Multiple agents discuss, vote on solutions

```
     Input
       ↓
   ┌───┴───┬───────┐
   ↓       ↓       ↓
Agent 1  Agent 2  Agent 3
   │       │       │
   └───┬───┴───────┘
       ↓
   Moderator/Vote
       ↓
     Output
```

**Use Cases:**

- Complex reasoning
- Multiple valid approaches
- Quality assurance

**Implementation (PanelGPT-style):**

```python
def debate_code_solution(task, num_agents=3, rounds=3):
    agents = [CodeAgent(f"Agent_{i}") for i in range(num_agents)]
    solutions = [agent.generate(task) for agent in agents]

    for round_num in range(rounds):
        critiques = []
        for i, agent in enumerate(agents):
            # Critique peers
            peers = [s for j, s in enumerate(solutions) if j != i]
            critique = agent.critique(peers)
            critiques.append(critique)

        # Refine based on critiques
        solutions = [
            agent.refine(solutions[i], critiques)
            for i, agent in enumerate(agents)
        ]

    # Vote on best solution
    return vote(solutions)
```

### 3. Hierarchical Pattern

**Structure:** Boss agent delegates to worker agents

```
      Boss Agent
     /     |     \
    /      |      \
Worker1  Worker2  Worker3
   |       |       |
   └───────┴───────┘
          ↓
   Consolidated Output
```

**Use Cases:**

- Task decomposition
- Large projects
- Different expertise areas

**Example (MetaGPT):**

```
Product Manager (Boss)
├── Architect (Design system)
├── Engineer (Implement)
└── Tester (Validate)
```

**Advantages:**

- ~5% better robustness than chains
- Clear responsibility assignment
- Scalable to large teams

### 4. Graph Pattern

**Structure:** Arbitrary connections, cycles allowed

```
   A ←→ B
   ↕    ↕
   C ←→ D

Agents can communicate in any direction
Loops enable iterative refinement
```

**Framework:** LangGraph

**Use Cases:**

- Complex state machines
- Conditional workflows
- Optimization loops

---

## Implementation Examples

### AgentCoder (Full Example)

**See full implementation in user-provided content** - Python script with:

- Programmer, Test Designer, Test Executor
- OpenAI API integration
- Iteration loop with feedback

**Key Code:**

```python
def agent_coder(task, max_iterations=5):
    # 1. Generate initial code
    code = programmer_agent.generate(task)

    # 2. Generate independent tests
    tests = test_designer_agent.create_tests(task)

    # 3. Iterate with executor feedback
    for iteration in range(max_iterations):
        errors = test_executor.run(code, tests)
        if not errors:
            return code  # Success!

        # Refine with feedback
        code = programmer_agent.refine(code, errors)

    return code  # Return best effort
```

### AutoGen Multi-Agent Example

```python
import autogen

# Define agents
config_list = [{"model": "gpt-4", "api_key": "..."}]

assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={"config_list": config_list}
)

code_reviewer = autogen.AssistantAgent(
    name="code_reviewer",
    system_message="Review code for bugs and style issues.",
    llm_config={"config_list": config_list}
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    code_execution_config={"work_dir": "coding"},
    human_input_mode="NEVER"
)

# Multi-agent conversation
user_proxy.initiate_chat(
    assistant,
    message="Write a function to find prime numbers up to n."
)

# Code review
user_proxy.send(
    message="Please review the code above.",
    recipient=code_reviewer
)
```

### MetaGPT Example (Simplified)

```python
from metagpt.software_company import SoftwareCompany
from metagpt.roles import ProductManager, Architect, Engineer

# Create company with roles
company = SoftwareCompany()
company.hire([
    ProductManager(),
    Architect(),
    Engineer()
])

# Run development
company.run_project(
    idea="Create a web app for task management with FastAPI backend"
)

# Outputs: Architecture docs, code files, tests
```

---

## Best Practices

### 1. Agent Role Design

**Clear Separation of Concerns:**

```python
# Good: Specialized roles
class ProgrammerAgent:
    def generate_code(self, spec): ...

class TesterAgent:
    def create_tests(self, spec): ...

class ReviewerAgent:
    def review_code(self, code): ...

# Bad: Monolithic agent
class MonolithAgent:
    def do_everything(self, task): ...
```

### 2. Communication Protocols

**Structured Messages:**

```python
{
    "from": "programmer_agent",
    "to": "test_executor",
    "type": "code_submission",
    "content": {
        "code": "def foo(): ...",
        "iteration": 2
    },
    "timestamp": "2025-11-08T10:30:00Z"
}
```

### 3. Feedback Loops

**Limit Iterations:**

```python
MAX_ITERATIONS = 5  # Prevent infinite loops
CONVERGENCE_THRESHOLD = 0.95  # Stop if tests pass rate high enough

for i in range(MAX_ITERATIONS):
    if test_pass_rate >= CONVERGENCE_THRESHOLD:
        break
```

### 4. Fault Tolerance

**Handle Agent Failures:**

```python
def robust_agent_call(agent, task, retries=3):
    for attempt in range(retries):
        try:
            return agent.process(task)
        except Exception as e:
            if attempt == retries - 1:
                # Fallback to simpler agent or default
                return fallback_agent.process(task)
            continue
```

### 5. Cost Management

**Token Usage Optimization:**

```python
# Expensive: Full conversation history every time
def expensive_debate(task):
    full_history = []
    for round in range(10):
        full_history.append(agent.generate(task, context=full_history))
    return full_history

# Efficient: Summarize history
def efficient_debate(task):
    summary = ""
    for round in range(10):
        response = agent.generate(task, context=summary)
        summary = summarize(summary + response)  # Keep summary, not full history
    return response
```

---

## Future Directions

### Emerging Trends (2025+)

1. **Self-Evolving Teams**: Agents that learn optimal collaboration patterns
2. **Multi-Modal Agents**: Handling code, diagrams, documentation
3. **Cross-Language Collaboration**: Polyglot agent teams
4. **Human-AI Hybrid Teams**: Seamless integration with developers
5. **Agentic IDEs**: Built-in multi-agent assistants

### Research Areas

- Optimal agent pool sizes for different tasks
- Communication efficiency vs. solution quality trade-offs
- Adversarial robustness in multi-agent systems
- Transfer learning across agent roles

---

## Resources

### Official Repositories

- **MetaGPT**: [github.com/geekan/MetaGPT](https://github.com/geekan/MetaGPT)
- **AutoGen**: [github.com/microsoft/autogen](https://github.com/microsoft/autogen)
- **LangGraph**: [github.com/langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)
- **CrewAI**: [github.com/joaomdmoura/crewAI](https://github.com/joaomdmoura/crewAI)

### Papers

- "AgentCoder: Multi-Agent Code Generation" (2023-2024)
- "Communicative Agents for Software Development" (ChatDev, 2023)
- "MetaGPT: Meta Programming for Multi-Agent Collaborative Framework" (2023)

### Related Documentation

- [ADVANCED_PROMPTING.md](ADVANCED_PROMPTING.md) - RCR for code agents
- [CODE_BENCHMARKS.md](CODE_BENCHMARKS.md) - Evaluation standards
- [COMPREHENSIVE_GUIDE.md](COMPREHENSIVE_GUIDE.md) - Integrated usage

---

## Version History

- **v1.0** (2025-11-08): Initial comprehensive documentation
  - Added framework comparison table
  - Detailed AgentCoder architecture
  - Collaboration patterns with examples
  - Best practices and implementation guides

---

## See Also

- [PROMPT_FRAMEWORKS.md](PROMPT_FRAMEWORKS.md) - Basic prompting
- [ADVANCED_PROMPTING.md](ADVANCED_PROMPTING.md) - DTE, MAD, RCR
- [CODE_BENCHMARKS.md](CODE_BENCHMARKS.md) - Performance evaluation
