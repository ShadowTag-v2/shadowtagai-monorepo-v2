# Gemini Design Wizard

**Purpose:** Route frontend design tasks to Gemini 3 Pro for creative direction, then integrate with Opus 4.5
**Enforcement:** `"suggest"`
**Priority:** `"high"`
**Version:** 1.0.0

---

## Overview

This skill implements the @omarsar0 pattern for shipping features 10x faster:
- **Gemini 3 Pro** leads creative direction and generates designs (~$0.087 per design at 7K tokens)
- **Opus 4.5** integrates the results into production code

### Cost Breakdown
- Gemini 3 Pro: ~7K tokens per design
- Cost per design: ~$0.087
- V1 designs are production-ready

---

## When to Use This Skill

Activate when user requests:
- Frontend component design
- UI/UX specifications
- Design system components
- Page layouts and architecture
- Interactive prototypes

Keywords: `design`, `component`, `UI`, `UX`, `layout`, `frontend`, `interface`

---

## Workflow (10x Faster Feature Shipping)

### Step 1: Plan with Context
Gather requirements from user:
- What component/feature?
- Framework (React, Vue, etc.)
- Style system (MUI, Tailwind, etc.)
- Design constraints

### Step 2: Gemini Design Generation
Call the atomic pipeline's Gemini client:

```python
from atomic_pipeline.clients import GeminiClient

async with GeminiClient() as gemini:
    design_spec = await gemini.design_component(
        description="User dashboard with metrics cards",
        framework="React",
        style_system="MUI",
    )
```

### Step 3: Research with Perplexity
Gather documentation and best practices:

```python
from atomic_pipeline.clients import PerplexityClient

async with PerplexityClient() as perplexity:
    docs = await perplexity.find_documentation(
        technology="React MUI",
        specific_feature="Dashboard components",
    )
```

### Step 4: Opus Integration
Using the design spec from Gemini, implement the component with Claude Code.

---

## Design Spec Format

Gemini returns structured JSON:

```json
{
    "component_name": "MetricsDashboard",
    "description": "Dashboard displaying key metrics with interactive cards",
    "props": [
        {"name": "metrics", "type": "Metric[]", "required": true},
        {"name": "onCardClick", "type": "(id: string) => void", "required": false}
    ],
    "styling": {
        "approach": "sx prop",
        "key_styles": {
            "container": "responsive grid",
            "cards": "elevation with hover effects"
        }
    },
    "accessibility": [
        "ARIA labels for screen readers",
        "Keyboard navigation between cards",
        "Focus indicators"
    ],
    "test_cases": [
        "renders all metrics",
        "handles empty state",
        "triggers callback on click",
        "responsive at breakpoints"
    ],
    "code_skeleton": "// Component structure..."
}
```

---

## Full Pipeline Example

```python
from atomic_pipeline import AtomicPipelineOrchestrator

async with AtomicPipelineOrchestrator() as pipeline:
    # @omarsar0 pattern: Gemini designs, Opus integrates
    result = await pipeline.design_frontend(
        description="E-commerce product grid with filters",
        framework="React",
        style_system="MUI",
    )

    # Result contains:
    # - design_spec: Gemini's creative direction
    # - documentation: Perplexity research
    # - trends: Grok's current best practices
    # - cost_estimate: ~$0.087
```

---

## Integration with @omarsar0 Workflow

1. **Plan**: Use ChatPRD or gather requirements
2. **Break down**: Gemini atomizes into tickets
3. **Create tickets**: Linear integration
4. **Auto-generate plans**: Claude Code + Linear MCP
5. **Parallel implementation**: Git worktrees
6. **Feature branch/PR**: Claude Code automation
7. **Code review**: Claude Code initial review
8. **Merge**: Manual verification

---

## Environment Variables

```bash
GEMINI_API_KEY=your_gemini_api_key
PERPLEXITY_API_KEY=your_perplexity_api_key
XAI_API_KEY=your_grok_api_key
```

---

## Best Practices

1. **Trust Gemini's V1** - First designs are production-ready
2. **Use structured output** - JSON specs integrate cleanly
3. **Research before implementing** - Perplexity finds edge cases
4. **Check trends** - Grok catches community preferences
5. **Parallel execution** - Use git worktrees for speed

---

**Last Updated:** 2025-11-27
**Maintained By:** ShadowTagAi
**Pattern Credit:** @omarsar0