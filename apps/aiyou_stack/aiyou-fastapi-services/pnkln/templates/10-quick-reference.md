# Template 10: Quick Reference Guide

## Purpose
Fast access to common PNKLN commands and patterns.

---

## Skill Activation Cheat Sheet

### Research Explorer
```
@research [TOPIC]
research: [TOPIC]
```
**Best for**: Market research, competitive analysis, assumption validation

---

### Design Critic
```
@design-critique [ARTIFACT]
critique: [DESIGN]
```
**Best for**: UI/UX review, simplification suggestions

---

### Copy Converter
```
@copy [TYPE]
write copy for [PURPOSE]
```
**Best for**: Landing pages, emails, ads, CTAs

---

### Monetization Architect
```
@revenue
design monetization strategy
```
**Best for**: Pricing strategy, revenue models, subscription design

---

### Workflow Refiner
```
optimize workflow: [DESCRIPTION]
simplify process: [DESCRIPTION]
```
**Best for**: Process optimization, automation, bottleneck removal

---

### Prompt Craft
```
@prompt create prompt for [TASK]
craft: [TASK DESCRIPTION]
```
**Best for**: Creating AI prompts, instruction optimization

---

## Agent Activation Shortcuts

### Research Agent
```
@research [TOPIC] --depth=exhaustive
```

### Design Agent
```
@design-critique [FILE] --ruthless
```

### Copy Agent
```
@copy landing_page for [PRODUCT]
```

### Revenue Agent
```
@revenue-architect
```

### Project Deep Agent (Orchestrator)
```
@project-deep [PROJECT DESCRIPTION]
/orchestrate --project=[NAME]
```

---

## Common Workflows

### New Product Launch
```
@project-deep Launch new product

Product: [NAME]
Target: [AUDIENCE]
Timeline: [DEADLINE]
Goals: [METRICS]
```

### Marketing Campaign
```
Execute marketing campaign:
- Campaign: [NAME]
- Channels: [EMAIL, TWITTER, etc.]
- Goal: [KPI]
```

### Revenue Optimization
```
Optimize revenue for:
- Current MRR: [$X]
- Goal MRR: [$Y]
- Timeline: [MONTHS]
```

---

## Pro Tips

### 1. Chain Skills
Instead of:
```
research topic X
[wait for result]
then use result to design pricing
```

Do this:
```
@project-deep

1. Research: [TOPIC]
2. Based on research, design pricing
3. Create pricing page copy
```

### 2. Be Specific with Context
❌ Bad:
```
research ai agents
```

✅ Good:
```
research: AI agent orchestration frameworks for 2025
Focus: developer tools market
Depth: exhaustive
Perspectives: technical, business, competitive
```

### 3. Use Templates
Don't start from scratch. Copy template from `/pnkln/templates/` and fill in blanks.

### 4. Set Clear Goals
❌ Bad:
```
help with pricing
```

✅ Good:
```
design pricing strategy
Current MRR: $10K
Goal MRR: $50K in 6 months
Target: indie developers
```

### 5. Trust the Orchestrator
For complex projects, use `@project-deep` instead of manually coordinating agents.

---

## Keyboard Shortcuts (Mental Model)

- `@research` = "Go deep on this topic"
- `@design-critique` = "Jobs-style design review"
- `@copy` = "Write high-converting copy"
- `@revenue` = "Design monetization"
- `@prompt` = "Create AI instructions"
- `@project-deep` = "Handle entire project"

---

## Troubleshooting Quick Fixes

### "Skill didn't activate"
→ Be more explicit: use `@skill-name` or `skill-name:`

### "Output too generic"
→ Add more context, constraints, examples

### "Wrong agent activated"
→ Use explicit mention: `@agent-name`

### "Result not what I expected"
→ Provide examples of desired output format

---

## Common Use Cases

| I want to... | Use this... | Example |
|--------------|-------------|---------|
| Understand a market | Research Explorer | `research: SaaS tools for developers` |
| Review a design | Design Critic | `@design-critique ./mockup.png --ruthless` |
| Write landing page | Copy Converter | `@copy landing_page for AI tool` |
| Design pricing | Monetization Architect | `@revenue design pricing for SaaS` |
| Simplify workflow | Workflow Refiner | `optimize: our feature dev process` |
| Create AI prompt | Prompt Craft | `@prompt create prompt for X` |
| Launch product | Project Deep Agent | `@project-deep launch new product` |

---

## Time Estimates

| Task | Manual | With PNKLN | Savings |
|------|--------|------------|---------|
| Market research | 2-4 hours | 15-30 min | 80% |
| Design critique | 30-60 min | 5-15 min | 75% |
| Landing page copy | 1-2 hours | 5-10 min | 85% |
| Pricing strategy | 2-3 hours | 10-20 min | 85% |
| Workflow optimization | 1-2 hours | 10-20 min | 80% |
| Prompt engineering | 30-60 min | 5-10 min | 80% |
| Full product launch | 2-3 days | 4-6 hours | 90% |

---

## Best Practices

1. ✅ **Start with a template** from `/pnkln/templates/`
2. ✅ **Be specific** about context, goals, constraints
3. ✅ **Use @mentions** for explicit activation
4. ✅ **Trust the orchestrator** for complex projects
5. ✅ **Provide examples** of desired output
6. ✅ **Set clear metrics** for success
7. ✅ **Iterate** - refine based on results

---

## Anti-Patterns (Don't Do This)

1. ❌ Vague requests: "help with my product"
2. ❌ No context: "research this" (what? why? how deep?)
3. ❌ Missing goals: "design pricing" (for what revenue target?)
4. ❌ Fighting the agent: Micromanaging each step
5. ❌ Ignoring templates: Starting from scratch every time

---

## Getting Help

- **Full docs**: See `/pnkln/integration-guide.md`
- **Templates**: Browse `/pnkln/templates/`
- **Skills reference**: Check `/pnkln/skills-registry.yaml`
- **Agents reference**: Check `/pnkln/agents-registry.yaml`

---

## Remember

> The goal isn't to replace human judgment, it's to amplify it.
>
> Use PNKLN to handle the research, analysis, and first-draft creation.
> You provide the vision, strategy, and final decisions.

---

**Version**: 1.0.0
**Last Updated**: 2025-11-15
