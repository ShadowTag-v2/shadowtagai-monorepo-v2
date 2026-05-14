
# ULTRATHINK Framework

> "The people who are crazy enough to think they can change the world are the ones who do." — Steve Jobs

An integrated Skills, Agents & Prompts framework that synthesizes Steve Jobs' design philosophy with modern AI agent architectures, prompt engineering methodologies, and wealth acceleration strategies.

## Philosophy

ULTRATHINK embodies Steve Jobs' approach to creation:

1. **Design-First Thinking**: Every output is scrutinized for elegance before functionality
2. **Boy Scout Rule**: Leave every file, codebase, and deliverable cleaner than found
3. **Assumption Interrogation**: Question every "why," seeking the most elegant solution
4. **Pinkln Elegance**: Achieved not by what remains to add, but by what can be removed
5. **Reality Distortion Field**: When something seems impossible, ultrathink harder

## Architecture

```
ULTRATHINK Framework
├── Skills (Reusable Expertise)
│   ├── Design Audit & Refinement
│   ├── War Game Architecture
│   ├── Iteration & Refinement Cycle
│   ├── Multi-LLM Reasoning Synthesis
│   └── Wealth Monetization Architecture
│
├── Agents (Specialized Personas)
│   ├── Chief Design Officer (CDO)
│   ├── Chief Architect
│   ├── Chief Wealth Officer (CWO)
│   ├── Chief Reasoning Officer (CRO)
│   └── Chief Experience Officer (CXO)
│
├── Multi-Agent Systems
│   ├── PanelGPT Debate Circle
│   ├── Multi-Agent Debate (MAD)
│   └── Cross-Functional Task Force
│
└── Foundation Prompts
    └── Core philosophy embeddings
```

## Quick Start

### Installation

```bash
# Python
pip install -e .

# Or add to requirements.txt
# ultrathink @ file:///path/to/ultrathink
```

### Basic Usage

```python
from ultrathink import UltrathinkOrchestrator, TaskType

# Initialize orchestrator
orchestrator = UltrathinkOrchestrator()

# Execute a task
result = await orchestrator.execute(
    task="Review this API design for elegance",
    task_type=TaskType.DESIGN_REVIEW
)

print(result["result"].content)
```

### Using Specific Agents

```python
from ultrathink import ChiefDesignOfficer, AgentContext, AgentRole

# Initialize CDO
cdo = ChiefDesignOfficer()

# Create context
context = AgentContext(
    task="Audit this user interface for simplicity",
    role=AgentRole.CDO,
    metadata={"ui_description": "Complex dashboard with 50+ widgets"}
)

# Execute
response = await cdo.execute(context)
print(response.content)
```

### Using Skills Directly

```python
from ultrathink import UltrathinkOrchestrator, SkillType

orchestrator = UltrathinkOrchestrator()

# Execute design audit skill
result = await orchestrator.execute_skill(
    skill_type=SkillType.DESIGN_AUDIT,
    content="Your code/content here",
    parameters={}
)

print(result.result)
print(result.improvements)
```

## Skills

### 1. Design Audit & Refinement

Autonomously scours for design improvements without changing functionality.

**Activation Triggers**: "review this", "audit this", "make this beautiful"

```python
result = await orchestrator.execute(
    "Audit this codebase for elegance",
    TaskType.DESIGN_REVIEW
)
```

### 2. War Game Architecture

Creates clear, well-reasoned plans that anyone could execute.

**Activation Triggers**: "architect this", "plan the system", "war game"

```python
result = await orchestrator.execute(
    "Design a scalable microservices architecture",
    TaskType.ARCHITECTURE_PLANNING
)
```

### 3. Iteration & Refinement Cycle

Iterates relentlessly until output reaches "insanely great" status.

**Activation Triggers**: "iterate", "refine", "polish", "improve"

```python
result = await orchestrator.execute(
    "Refine this user experience until perfect",
    TaskType.ITERATIVE_REFINEMENT
)
```

### 4. Multi-LLM Reasoning Synthesis

Leverages CoT, ToT, PanelGPT, and MAD for robust solutions.

**Activation Triggers**: "analyze thoroughly", "reason carefully", "think deeply"

```python
result = await orchestrator.execute(
    "Solve this complex architectural decision",
    TaskType.REASONING_PROBLEM
)
```

### 5. Wealth Monetization Architecture

Turns attention into income at scale.

**Activation Triggers**: "monetization", "revenue", "pricing strategy"

```python
result = await orchestrator.execute(
    "Design a monetization strategy for 50K newsletter subscribers",
    TaskType.MONETIZATION_STRATEGY
)
```

## Agents

### Chief Design Officer (CDO)

Embodies Steve Jobs' eye for design. Questions every assumption.

**Use When**: Design review, elegance assessment, UI/UX audit

### Chief Architect

Plans like Da Vinci. War-games before building.

**Use When**: System design, architecture planning, technical strategy

### Chief Wealth Officer (CWO)

Spots money-making opportunities others miss.

**Use When**: Monetization strategy, revenue optimization, funnel design

### Chief Reasoning Officer (CRO)

Orchestrates multi-method reasoning for robust correctness.

**Use When**: High-stakes decisions, complex problem-solving, validation

### Chief Experience Officer (CXO)

Iterates until insanely great. Guardian of quality.

**Use When**: Refinement, polish, iterative improvement

## Multi-Agent Systems

### PanelGPT Debate Circle

Expert personas debate and converge on solutions.

```python
from ultrathink import PanelGPTDebate, AgentContext, AgentRole

panel = PanelGPTDebate()
context = AgentContext(
    task="Should we pivot to B2B or B2C?",
    role=AgentRole.CRO
)

result = await panel.debate(context, rounds=3)
print(result.consensus)
```

### Multi-Agent Debate (MAD)

Adversarial debate for high-stakes correctness.

```python
from ultrathink import MultiAgentDebate

mad = MultiAgentDebate()
result = await mad.debate(context, rounds=3)
print(result.final_solution)
```

### Cross-Functional Task Force

All chief officers working in concert.

```python
from ultrathink import CrossFunctionalTaskForce

task_force = CrossFunctionalTaskForce()
# Agents are auto-registered by orchestrator
result = await task_force.execute_mission(context)
```

## Foundation Prompts

Access core philosophy prompts:

```python
from ultrathink import FoundationPrompts

prompts = FoundationPrompts()

# Entry protocol
entry = prompts.ultrathink_entry_protocol()

# Design audit
audit = prompts.design_audit_deep_dive()

# War game architecture
war_game = prompts.war_game_architecture()

# Multi-method reasoning
reasoning = prompts.multi_method_reasoning()

# Monetization audit
monetization = prompts.monetization_audit()

# Iteration
iteration = prompts.iterate_until_great()
```

## Configuration

```python
from ultrathink import UltrathinkOrchestrator, UltrathinkConfig

config = UltrathinkConfig(
    model="claude-sonnet-4-5-20250929",
    temperature=0.7,
    max_tokens=4096,
    enable_extended_thinking=True,
    security_mode=True,
    iteration_limit=5,
    confidence_threshold=0.8
)

orchestrator = UltrathinkOrchestrator(config)
```

## Examples

### Example 1: Product Launch

```python
orchestrator = UltrathinkOrchestrator()

result = await orchestrator.execute(
    "We're launching a new SaaS product. Need full strategy.",
    TaskType.HOLISTIC_INITIATIVE
)

# Returns responses from all agents:
# - CDO: Design & UX audit
# - Architect: Technical architecture
# - CWO: Monetization strategy
# - CRO: Risk validation
# - CXO: Final polish
```

### Example 2: Revenue Optimization

```python
result = await orchestrator.execute_skill(
    skill_type=SkillType.WEALTH,
    content="""
    Current state:
    - 50,000 email subscribers
    - $50K/year revenue
    - Single product at $97
    - No upsell funnel
    """,
    parameters={
        "revenue_goal": 1000000,
        "audience_size": 50000,
        "engagement_rate": 0.15
    }
)

print(result.result)  # Full monetization strategy
```

### Example 3: Multi-Method Problem Solving

```python
result = await orchestrator.execute(
    "Should we build in-house or buy a third-party solution?",
    TaskType.STRATEGIC_DECISION
)

# Uses PanelGPT with Optimist, Skeptic, Pragmatist
print(result.consensus)
print(result.confidence)
```

## Integration with Claude Agent SDK

```python
from claude_agent_sdk import query, ClaudeAgentOptions
from ultrathink import FoundationPrompts

prompts = FoundationPrompts()

# Use ULTRATHINK entry protocol as system prompt
async for message in query(
    prompt="Design an elegant API",
    options=ClaudeAgentOptions(
        system_prompt=prompts.ultrathink_entry_protocol()
    )
):
    print(message)
```

## Best Practices

1. **Start with Entry Protocol**: Always prime sessions with `ultrathink_entry_protocol()`
2. **Let Orchestrator Route**: Use `TaskType` classification for automatic routing
3. **Use Skills for Focused Tasks**: Direct skill execution for specific expertise
4. **Deploy Multi-Agents for Complex Decisions**: PanelGPT/MAD for high stakes
5. **Iterate Relentlessly**: The first version is never good enough
6. **Trust the Reasoning Audit Trail**: Every decision is documented

## Philosophy in Action

> **Pinkln Elegance**: "Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away."

Every component of ULTRATHINK embodies this principle:

- **Skills** remove complexity while preserving power
- **Agents** question assumptions to find simpler paths
- **Prompts** distill philosophy into actionable guidance
- **Multi-Agents** debate to eliminate weak reasoning

## Contributing

When extending ULTRATHINK:

1. **Follow the Boy Scout Rule**: Leave it cleaner
2. **Question Assumptions**: Why must it work this way?
3. **Design First**: Elegance before functionality
4. **Document Reasoning**: Show your thinking
5. **War-Game It**: Test failure modes

## License

Proprietary - pinkln

---

**"We're here to put a dent in the universe. Otherwise why else even be here?"** — Steve Jobs

At pinkln, we own the Reality Distortion Field. Let's build something beautiful.
