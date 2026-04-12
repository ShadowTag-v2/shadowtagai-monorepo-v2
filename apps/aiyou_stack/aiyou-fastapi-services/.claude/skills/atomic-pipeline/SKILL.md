# Atomic Pipeline Orchestration

**Purpose:** Multi-model code generation pipeline using Gemini, Perplexity, Grok, and n-autoresearch/Kosmos/BioAgents
**Enforcement:** `"suggest"`
**Priority:** `"high"`
**Version:** 1.0.0

---

## Overview

The Atomic Pipeline implements a "slow is smooth, smooth is fast" philosophy for AI-assisted code generation.

### Pipeline Stages

```

INTAKE → RESEARCH → TRENDS → EXECUTION → PUBLISH
   ↓         ↓          ↓          ↓          ↓
Gemini   Perplexity   Grok    n-autoresearch/Kosmos/BioAgents   Git/Vertex/Colab

```

### Model Responsibilities

| Model | Role | Cost |
|-------|------|------|
| **Gemini 3 Pro** | Parse requirements, design, generate tests | ~$0.087/design |
| **Perplexity Sonar** | Deep research, documentation, citations | $5/1K searches |
| **Grok Code Fast** | X trends, business context, rapid coding | $0.15/M input |
| **n-autoresearch/Kosmos/BioAgents** | Distributed execution (600 agents) | Internal |

---

## When to Use This Skill

Activate for:

- Complex multi-file implementations

- Features requiring research

- Trend-aware development

- Distributed code generation

- End-to-end feature shipping

Keywords: `atomic`, `pipeline`, `generate`, `implement`, `ship`, `build feature`

---

## Quick Start

### Basic Pipeline Run

```python
from atomic_pipeline import AtomicPipelineOrchestrator

async with AtomicPipelineOrchestrator() as pipeline:
    result = await pipeline.run(
        requirements="Build a real-time notification system with WebSocket support",
        context={"framework": "FastAPI", "frontend": "React"},
    )

    print(f"Completed {result.completed_tasks}/{result.total_tasks} tasks")
    print(f"Duration: {result.duration_seconds:.1f}s")

```

### Frontend Design (@omarsar0 Pattern)

```python
async with AtomicPipelineOrchestrator() as pipeline:
    design = await pipeline.design_frontend(
        description="Admin dashboard with data tables and charts",
        framework="React",
        style_system="MUI",
    )
    # design.design_spec contains Gemini's creative direction
    # design.documentation contains Perplexity's research
    # design.trends contains Grok's analysis

```

---

## Pipeline Stages Explained

### 1. INTAKE (Gemini 3 Pro)

"Slow is smooth" - Take time to understand requirements.

```python

# Gemini parses requirements into atomic tasks

parsed = await gemini.parse_requirements("""
    Build a user authentication system with:

    - Email/password login

    - OAuth (Google, GitHub)

    - 2FA support

    - Session management
""")

# Returns: atomic_tasks, dependencies, acceptance_criteria

```

### 2. RESEARCH (Perplexity Sonar)

Gather documentation, examples, and best practices.

```python
research = await perplexity.research_topic(
    topic="FastAPI OAuth implementation",
    depth="comprehensive",
    focus_areas=["security", "token handling"],
)

# Returns: findings with citations

```

### 3. TRENDS (Grok Code Fast)

Apply current community preferences.

```python
trends = await grok.analyze_trends(
    topic="Python authentication libraries 2025",
    context="Building for production FastAPI app",
)

# Returns: current discussions, sentiment, recommendations

```

### 4. EXECUTION (n-autoresearch/Kosmos/BioAgents)

"Smooth is fast" - Execute with good preparation.

```python
code = await grok.generate_code(
    task="Implement OAuth2 with Google provider",
    language="python",
    test_requirements=True,
)

tests = await gemini.generate_tests(
    code=code.content,
    framework="pytest",
    coverage_target="comprehensive",
)

```

### 5. PUBLISH (Git → Vertex → Colab)

Push to version control and notebooks.

```python
await runner.publish_to_git(
    files=["auth.py", "test_auth.py"],
    commit_message="feat(auth): Add OAuth2 Google provider",
)

```

---

## Headless Antigravity Runner

For distributed execution across multiple instances:

```python
from atomic_pipeline import AntigravityRunner, AntigravityConfig

config = AntigravityConfig(
    pods=3,                    # 3 pods
    instances_per_pod=3,       # × 3 instances each = 9 total
    inline_instances=10,       # + 10 inline with Gemini Assist
    enable_gemini_assist=True,
    enable_grok=True,
    enable_perplexity=True,
)

runner = AntigravityRunner(config)
await runner.start()

# Execute batch of tasks in parallel

results = await runner.execute_batch(tasks, parallel=3)

```

---

## Configuration

### Environment Variables

```bash

# Required API Keys

GEMINI_API_KEY=your_gemini_key
PERPLEXITY_API_KEY=your_perplexity_key
XAI_API_KEY=your_grok_key

# Optional: Publishing

GIT_REMOTE=redacted@shadowtag-v4.local:org/repo.git
VERTEX_PROJECT=your-gcp-project
COLAB_DRIVE_FOLDER=folder_id

```

### Pipeline Config

```python
from atomic_pipeline import PipelineConfig

config = PipelineConfig(
    max_concurrent_tasks=3,
    enable_research=True,
    enable_trends=True,
    git_auto_commit=True,
    vertex_publish=False,
    colab_publish=False,
    autoresearch_url="http://localhost:8600",
)

```

---

## Adding Custom Hooks

Extend pipeline behavior at any stage:

```python
async def log_research(task):
    print(f"Research complete for {task.id}: {len(task.research_result['citations'])} citations")

pipeline.add_hook(
    stage=PipelineStage.RESEARCH,
    hook=log_research,
    pre=False,  # Post-hook
)

```

---

## Integration with n-autoresearch/Kosmos/BioAgents

The pipeline integrates with the n-autoresearch/Kosmos/BioAgents swarm (600 agents):

```python

# Dispatch directly to swarm

result = await runner.dispatch_to_monkeys({
    "task": "Generate API endpoints",
    "code": generated_code,
    "tests": generated_tests,
})

```

Swarm composition: 570 Flash agents + 30 Pro agents

---

## Best Practices


1. **Atomic tasks** - Break work into smallest implementable units

2. **Research first** - Let Perplexity gather context before coding

3. **Check trends** - Grok catches community preferences

4. **Parallel execution** - Use git worktrees for speed

5. **Comprehensive tests** - Gemini generates tests alongside code

6. **Git discipline** - Auto-commit preserves context

---

## Example: Full Feature Implementation

```python

# Implement a complete feature with the atomic pipeline

async def implement_feature(description: str):
    async with AtomicPipelineOrchestrator() as pipeline:
        result = await pipeline.run(
            requirements=description,
            context={
                "codebase": "FastAPI + React",
                "style": "production-ready",
                "tests": "comprehensive",
            },
        )

        # Output results
        for task in result.tasks:
            if task.status == "completed":
                print(f"✓ {task.description}")
                if task.execution_result:
                    print(f"  Files: {task.execution_result.get('files', [])}")
            else:
                print(f"✗ {task.description}: {task.error}")

        print(f"\nPipeline completed in {result.duration_seconds:.1f}s")
        print(f"Stage timings: {result.stage_timings}")

        return result

# Usage

await implement_feature("Add user profile page with avatar upload and preferences")

```

---

**Last Updated:** 2025-11-27
**Maintained By:** ShadowTagAi
**Philosophy:** "Slow is smooth, smooth is fast"
