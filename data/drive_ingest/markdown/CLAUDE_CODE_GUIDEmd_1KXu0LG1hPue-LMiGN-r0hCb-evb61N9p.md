# pinkln Agent Architecture System - Claude Code Guide

**"Insanely Great AI Systems Through Elegant Orchestration in Claude Code"**

Complete guide for running the pinkln Agent Architecture System in Anthropic's Claude Code environment.

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Core Concepts](#core-concepts)
5. [Usage Examples](#usage-examples)
6. [Advanced Patterns](#advanced-patterns)
7. [Configuration](#configuration)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [API Reference](#api-reference)

## Introduction

### What is pinkln + Claude Code?

The pinkln Agent Architecture System integrated with Claude Code brings the power of:

- **9 Core Directives** (Ultrathink philosophy)
- **Adaptive Reasoning** (CoT, ToT, MAD, DTE strategies)
- **Multi-Agent Collaboration** (Council of Excellence)
- **Automatic Excellence Validation** (Boy Scout Rule)
- **Local Development** (Run entirely in Claude Code CLI)

### Why Use This Integration?

- **Local First**: Run powerful AI workflows on your machine
- **Version Controlled**: All prompts, configs, and sessions in git
- **Cost Effective**: Use Claude API directly, no additional platforms
- **Developer Friendly**: Python API, CLI tools, and async support
- **Marketplace Ready**: Access to pinkln superpowers marketplace

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/ShadowTag-v2-fastapi-services.git
cd ShadowTag-v2-fastapi-services

# Install dependencies
pip install -r requirements-claude.txt

# Set API key
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 2. Run Your First Agent

```python
from pinkln_claude_integration import ClaudePnklnAgent

agent = ClaudePnklnAgent()
result = await agent.execute(
    "What are the top 3 revenue opportunities for a $50K/month SaaS business?"
)
print(result['solution'])
```

### 3. Try the Demo

```bash
python claude_code_demo.py --demo revenue
```

## Installation

### Prerequisites

- **Python 3.9+**
- **Claude Code** installed (Anthropic's official CLI)
- **Anthropic API Key** (get from console.anthropic.com)

### Step-by-Step Installation

#### 1. Install Claude Code

```bash
# macOS/Linux
npm install -g @anthropic-ai/claude-code

# Or using pip
pip install anthropic-claude-code
```

#### 2. Install Python Dependencies

```bash
pip install -r requirements-claude.txt
```

The requirements include:

```
anthropic>=0.39.0
pydantic>=2.0.0
pyyaml>=6.0
python-dotenv>=1.0.0
aiohttp>=3.11.0
```

#### 3. Configure API Key

Option A: Environment Variable

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Option B: .env File

```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

Option C: Config File

```yaml
# claude_code_config.yaml
claude_code:
  api:
    api_key_env: 'ANTHROPIC_API_KEY'
```

#### 4. Verify Installation

```bash
python -c "from pinkln_claude_integration import ClaudePnklnAgent; print('✓ Ready!')"
```

## Core Concepts

### 1. The pinkln OS

The heart of the system - embodies the "Ultrathink like Steve Jobs" philosophy:

```python
from pinkln.core.master_system import PnklnOS

pinkln_os = PnklnOS()

# Assess complexity of any challenge
complexity = pinkln_os.assess_complexity("Your challenge here")

# Get appropriate reasoning strategy
strategy = pinkln_os.select_reasoning_strategy(complexity)
```

**Complexity Levels:**

- `0.0 - 0.3`: Simple → Chain of Thought
- `0.3 - 0.6`: Medium → Tree of Thoughts
- `0.6 - 0.9`: Complex → Multi-Agent Debate
- `0.9 - 1.0`: Maximum → Debate-Train-Evolve

### 2. ClaudePnklnAgent

The main interface for Claude Code integration:

```python
from pinkln_claude_integration import ClaudePnklnAgent

agent = ClaudePnklnAgent(
    model="claude-sonnet-4-5",  # or claude-opus-4, claude-haiku-4
    session_id="my-session"  # optional session tracking
)

result = await agent.execute(
    challenge="Your challenge",
    role="Agent Role",  # e.g., "Monetization Architect"
    enable_validation=True  # apply pinkln standards
)
```

### 3. Reasoning Strategies

The system automatically selects the best approach:

**Chain of Thought (CoT)**

- Linear, step-by-step reasoning
- Best for: Calculations, simple analysis
- Speed: Fast

**Tree of Thoughts (ToT)**

- Explores multiple solution paths
- Best for: Decision making, trade-off analysis
- Speed: Medium

**Multi-Agent Debate (MAD)**

- Multiple perspectives debate to consensus
- Best for: Complex decisions, strategy
- Speed: Slower, higher quality

**Debate-Train-Evolve (DTE)**

- Evolutionary improvement cycles
- Best for: Maximum complexity challenges
- Speed: Slowest, highest quality

### 4. Skills and Agents

**Skills** are atomic capabilities:

- ResearchExplorerSkill
- DesignCriticSkill
- CopyConverterSkill
- MonetizationArchitectSkill
- WorkflowRefinerSkill
- PromptCraftSkill

**Agents** are autonomous personas combining multiple skills:

- WealthAcceleratorAgent
- DesignAgent
- ResearchAgent
- ProjectDeepAgent

### 5. The Boy Scout Rule

Every operation applies the Boy Scout Rule:

```python
result = await agent.execute(challenge)

# Result includes cleanup metadata
print(result['boy_scout_metadata'])
# {
#   'files_touched': [...],
#   'cleanup_actions': [...],
#   'cleaner_than_found': True
# }
```

## Usage Examples

### Example 1: Revenue Optimization

```python
from pinkln_claude_integration import ClaudePnklnAgent

agent = ClaudePnklnAgent()

challenge = """
I run a SaaS business:
- $15K MRR
- 300 users at $50/month
- 82% retention
- $250 CAC

What are my top 3 revenue leaks and quick wins?
"""

result = await agent.execute(challenge, role="Monetization Architect")
print(f"Strategy: {result['strategy']}")
print(result['solution']['content'])
```

### Example 2: Multi-Agent Debate

```python
from pinkln_claude_integration import ClaudePnklnAgent

agent = ClaudePnklnAgent()

perspectives = [
    {"role": "Optimist", "focus": "growth opportunities"},
    {"role": "Skeptic", "focus": "risks and challenges"},
    {"role": "Pragmatist", "focus": "execution reality"}
]

result = await agent.multi_agent_debate(
    "Should we raise VC funding or bootstrap?",
    perspectives,
    synthesize=True
)

# Access each perspective
for p in result['perspectives']:
    print(f"{p['role']}: {p['response']['solution']}")

# Get final synthesis
print(result['synthesis']['solution'])
```

### Example 3: Design Critique

```python
from pinkln_claude_integration import ClaudePnklnAgent

agent = ClaudePnklnAgent()

result = await agent.execute(
    """
    Review our checkout flow:
    1. Cart page with 8 upsells
    2. Account creation (required, 12 fields)
    3. Shipping form (9 fields)
    4. Payment form (8 fields)
    5. Review page
    6. Confirmation

    Conversion rate is 8%. What's wrong?
    """,
    role="Design Critic"
)

print(result['solution']['content'])
```

### Example 4: Iterative Refinement

```python
from pinkln_claude_integration import ClaudePnklnAgent

agent = ClaudePnklnAgent()

# Initial draft
result1 = await agent.execute(
    "Write a landing page headline for AI code review tool",
    role="Copy Converter"
)

# Critique and refine
result2 = await agent.execute(
    f"Critique and improve: {result1['solution']}",
    role="Copy Converter"
)

# Final excellence pass
result3 = await agent.execute(
    f"Make this insanely great: {result2['solution']}",
    role="Copy Converter"
)

print("Final version:", result3['solution'])
```

### Example 5: Using Skills Directly

```python
from pinkln_claude_integration import ClaudePnklnAgent

agent = ClaudePnklnAgent()

# Execute research skill
result = await agent.skill_execution(
    skill_name="research",
    task_context={
        "topic": "AI monetization trends 2024",
        "depth": "comprehensive"
    }
)

print(result['solution']['content'])
```

### Example 6: Session Tracking

```python
from pinkln_claude_integration import ClaudePnklnAgent

# Create named session
agent = ClaudePnklnAgent(session_id="product-strategy-session")

# Run multiple challenges
await agent.execute("Challenge 1...")
await agent.execute("Challenge 2...")
await agent.execute("Challenge 3...")

# Get session summary
summary = agent.get_session_summary()
print(f"Completed {summary['challenges_completed']} challenges")
print(f"Duration: {summary['duration_minutes']:.1f} minutes")
```

## Advanced Patterns

### Pattern 1: Council of Excellence

Simulate expert panel discussions:

```python
async def council_decision(question: str):
    agent = ClaudePnklnAgent()

    council = [
        {"role": "CEO", "focus": "business strategy"},
        {"role": "CTO", "focus": "technical feasibility"},
        {"role": "CFO", "focus": "financial impact"},
        {"role": "COO", "focus": "operational complexity"}
    ]

    result = await agent.multi_agent_debate(question, council, synthesize=True)
    return result['synthesis']

decision = await council_decision("Should we build vs buy our CRM?")
```

### Pattern 2: Complexity-Adaptive Pipeline

Automatically adjust strategy based on complexity:

```python
from pinkln.core.master_system import PnklnOS

async def adaptive_analyze(challenge: str):
    pinkln_os = PnklnOS()
    agent = ClaudePnklnAgent()

    # Assess complexity
    complexity = pinkln_os.assess_complexity(challenge)

    # Route to appropriate handler
    if complexity < 0.3:
        # Quick analysis
        return await agent.execute(challenge, role="Analyst")
    elif complexity < 0.6:
        # Tree of thoughts exploration
        return await agent.execute(challenge, role="Strategic Analyst")
    else:
        # Full multi-agent debate
        perspectives = [
            {"role": "Optimist", "focus": "opportunities"},
            {"role": "Realist", "focus": "constraints"}
        ]
        return await agent.multi_agent_debate(challenge, perspectives)
```

### Pattern 3: Iterative Excellence Loop

Automatically refine until meeting pinkln standards:

```python
async def iterate_to_excellence(initial_challenge: str, max_iterations: int = 5):
    agent = ClaudePnklnAgent()

    result = await agent.execute(initial_challenge)

    for i in range(max_iterations):
        if result.get('metadata', {}).get('excellence_achieved'):
            print(f"Excellence achieved in {i} iterations!")
            break

        # Critique current result
        critique_prompt = f"""
        Current solution: {result['solution']}

        Apply pinkln principles to improve:
        1. Simplify ruthlessly
        2. Obsess over details
        3. Question assumptions

        Provide improved version.
        """

        result = await agent.execute(critique_prompt)

    return result
```

### Pattern 4: Skill Composition

Combine multiple skills:

```python
async def comprehensive_product_analysis(product_idea: str):
    agent = ClaudePnklnAgent()

    # Research the market
    research = await agent.skill_execution("research", {
        "topic": f"Market for {product_idea}"
    })

    # Design the solution
    design = await agent.skill_execution("design", {
        "concept": product_idea,
        "context": research['solution']
    })

    # Monetization strategy
    monetization = await agent.skill_execution("monetization", {
        "product": product_idea,
        "research": research['solution'],
        "design": design['solution']
    })

    return {
        "research": research,
        "design": design,
        "monetization": monetization
    }
```

### Pattern 5: Batch Processing

Process multiple challenges efficiently:

```python
async def batch_analyze(challenges: list[str]):
    agent = ClaudePnklnAgent(session_id="batch-analysis")

    results = []
    for challenge in challenges:
        result = await agent.execute(challenge)
        results.append(result)

    summary = agent.get_session_summary()

    return {
        "results": results,
        "summary": summary
    }

challenges = [
    "Optimize our pricing page",
    "Improve email onboarding",
    "Design referral program"
]

batch_results = await batch_analyze(challenges)
```

## Configuration

### Configuration File Structure

`claude_code_config.yaml`:

```yaml
claude_code:
  default_model: 'claude-sonnet-4-5'
  api:
    max_tokens: 4096
    temperature: 1.0

pinkln:
  reasoning:
    basic_threshold: 0.3
    exploratory_threshold: 0.6
    collaborative_threshold: 0.9

  validation:
    enable_validation: true
    max_iterations: 10
    excellence_threshold: 0.85

session:
  enable_tracking: true
  persist_sessions: true
  sessions_dir: './sessions'

logging:
  level: 'INFO'
  log_to_file: true
  log_file: './logs/pinkln.log'
```

### Loading Custom Configuration

```python
from pathlib import Path
from pinkln_claude_integration import ClaudePnklnAgent

agent = ClaudePnklnAgent(
    config_path=Path("./my_custom_config.yaml")
)
```

### Environment Variables

```bash
# Required
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional
export PINKLN_ENV="production"
export PINKLN_LOG_LEVEL="INFO"
export PINKLN_SESSION_DIR="./sessions"
export PINKLN_CACHE_DIR="./.cache/pinkln"
```

## Best Practices

### 1. Complexity-First Design

Always assess complexity before execution:

```python
pinkln_os = PnklnOS()
complexity = pinkln_os.assess_complexity(challenge)

if complexity < 0.3:
    # Use simpler, faster approach
    result = await quick_analyze(challenge)
else:
    # Use full agent system
    result = await agent.execute(challenge)
```

### 2. Session Management

Use named sessions for related work:

```python
# Product strategy session
product_agent = ClaudePnklnAgent(session_id="product-strategy-2024")

# Marketing session
marketing_agent = ClaudePnklnAgent(session_id="marketing-q1")
```

### 3. Role Selection

Choose appropriate roles for tasks:

| Task Type           | Role                   |
| ------------------- | ---------------------- |
| Revenue analysis    | Monetization Architect |
| Design feedback     | Design Critic          |
| Copywriting         | Copy Converter         |
| Research            | Research Explorer      |
| Process improvement | Workflow Refiner       |
| Prompt creation     | Prompt Craftsman       |

### 4. Validation Control

Enable validation for important decisions:

```python
# High stakes decision - enable validation
result = await agent.execute(
    "Should we pivot the business?",
    enable_validation=True
)

# Quick draft - skip validation
result = await agent.execute(
    "Draft a tweet about our new feature",
    enable_validation=False
)
```

### 5. Error Handling

Implement robust error handling:

```python
from anthropic import APIError

async def safe_execute(challenge: str):
    agent = ClaudePnklnAgent()

    try:
        result = await agent.execute(challenge)
        return result
    except APIError as e:
        print(f"API Error: {e}")
        # Fallback or retry logic
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

### 6. Cost Optimization

Monitor and optimize token usage:

```python
# Track session costs
agent = ClaudePnklnAgent(session_id="cost-tracking")

# Run multiple tasks
for task in tasks:
    await agent.execute(task)

# Review summary
summary = agent.get_session_summary()
# Implement cost tracking based on summary
```

## Troubleshooting

### Common Issues

#### Issue 1: "Module not found: pinkln"

**Solution:**

```bash
# Ensure you're in the repository root
cd /path/to/ShadowTag-v2-fastapi-services

# Verify pinkln directory exists
ls -la pinkln/

# Run with proper Python path
PYTHONPATH=. python your_script.py
```

#### Issue 2: "API key not found"

**Solution:**

```bash
# Set environment variable
export ANTHROPIC_API_KEY="sk-ant-..."

# Or create .env file
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# Verify it's set
python -c "import os; print(os.getenv('ANTHROPIC_API_KEY'))"
```

#### Issue 3: Slow responses

**Solutions:**

- Use appropriate model (Haiku for simple tasks)
- Reduce max_tokens
- Disable validation for drafts
- Check network connection
- Consider caching results

```python
# Use faster model
agent = ClaudePnklnAgent(model="claude-haiku-4")

# Reduce tokens
result = await agent.execute(challenge, max_tokens=2048)
```

#### Issue 4: Import errors

**Solution:**

```bash
# Reinstall dependencies
pip install -r requirements-claude.txt --force-reinstall

# Verify imports
python -c "from pinkln_claude_integration import ClaudePnklnAgent"
```

### Getting Help

- **Documentation**: Read this guide thoroughly
- **Examples**: Check `claude_code_demo.py`
- **Issues**: GitHub issues in the repository
- **Claude Code Docs**: https://docs.anthropic.com/claude-code

## API Reference

### ClaudePnklnAgent

#### Constructor

```python
ClaudePnklnAgent(
    model: str = "claude-sonnet-4-5",
    config_path: Optional[Path] = None,
    session_id: Optional[str] = None
)
```

#### Methods

**execute()**

```python
async execute(
    challenge: str,
    role: str = "pinkln Agent",
    max_tokens: int = 4096,
    temperature: float = 1.0,
    enable_validation: bool = True
) -> Dict[str, Any]
```

**multi_agent_debate()**

```python
async multi_agent_debate(
    challenge: str,
    perspectives: List[Dict[str, str]],
    synthesize: bool = True
) -> Dict[str, Any]
```

**skill_execution()**

```python
async skill_execution(
    skill_name: str,
    task_context: Dict[str, Any]
) -> Dict[str, Any]
```

**get_session_summary()**

```python
get_session_summary() -> Dict[str, Any]
```

### PnklnOS

#### Methods

**assess_complexity()**

```python
assess_complexity(problem: str) -> float
```

**select_reasoning_strategy()**

```python
select_reasoning_strategy(complexity: float) -> str
```

**create_agent_prompt()**

```python
create_agent_prompt(
    agent_role: str,
    task: str,
    **kwargs
) -> str
```

## Appendix

### Model Selection Guide

| Model             | Use Case                  | Speed  | Cost    | Quality   |
| ----------------- | ------------------------- | ------ | ------- | --------- |
| Claude Opus 4     | Maximum capability tasks  | Slow   | Highest | Best      |
| Claude Sonnet 4.5 | Balanced performance      | Medium | Medium  | Excellent |
| Claude Haiku 4    | High-volume, simple tasks | Fast   | Lowest  | Good      |

### Complexity Factors

The system assesses complexity based on:

- Text length
- Number of questions
- Requirement keywords ("must", "should")
- Multi-part structure
- Conditional logic

### Reasoning Strategy Matrix

| Complexity | Strategy            | Typical Use Cases          |
| ---------- | ------------------- | -------------------------- |
| 0.0 - 0.3  | Chain of Thought    | Calculations, simple Q&A   |
| 0.3 - 0.6  | Tree of Thoughts    | Decisions, comparisons     |
| 0.6 - 0.9  | Multi-Agent Debate  | Strategy, complex analysis |
| 0.9 - 1.0  | Debate-Train-Evolve | Maximum complexity         |

---

**"The people who are crazy enough to think they can change the world are the ones who do."** 🚀

Built with craftsmanship. Designed for excellence. Running in Claude Code.