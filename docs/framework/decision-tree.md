# Agent Pattern Decision Tree

## 🎯 Quick Start: Choose Your Pattern

Use this decision tree before writing any prompts to select the optimal agent pattern for your use case.

```
┌─ Is the task sequence predictable and well-defined?
│  ├─ YES → Use WORKFLOW pattern (80% of cases)
│  │        ↓ Deterministic, auditable, fast
│  │        Examples: Data validation, report generation, form processing
│  │
│  └─ NO → Is dynamic decision-making required?
│     ├─ YES → Can a single agent handle it?
│     │  ├─ YES → Use SINGLE-AGENT pattern (15% of cases)
│     │  │        ↓ Dynamic but manageable complexity
│     │  │        Examples: Customer support, code debugging, research tasks
│     │  │
│     │  └─ NO → Are subtasks truly independent?
│     │     ├─ YES → Use MULTI-AGENT pattern (4% of cases)
│     │     │        ↓ Parallel exploration, distinct domains
│     │     │        Examples: Comprehensive market research, large codebase analysis
│     │     │
│     │     └─ NO → REFACTOR to single-agent with iteration
│     │                ↓ Dependencies kill multi-agent benefits
│     │
│     └─ NO → Use SIMPLE PROMPT (1% of cases)
│               ↓ Classification, simple generation
│               Examples: Text classification, basic Q&A
```

**Critical Rule**: Start with the simplest pattern. Add complexity ONLY when demonstrated improvement occurs.

---

## Pattern Selection Guide

### Pattern 1: Workflow (80% of use cases)

**When to choose:**
- ✅ Task has clear, predictable sequence
- ✅ Requirements are well-defined
- ✅ Steps can be predetermined
- ✅ Need deterministic, auditable results
- ✅ Cost efficiency is important

**Characteristics:**
- Deterministic execution path
- Easy to debug and test
- Lower token costs
- Precise, consistent outputs
- Simple to maintain

**Best for:**
- Data validation pipelines
- Report generation
- Form processing
- Automated workflows
- Standard operating procedures

**Example Flow:**
```
User Input → Classify Intent → Route to Handler → Execute Steps → Validate → Return
```

**When NOT to choose:**
- Tasks require adaptive decision-making
- Unknown edge cases are common
- Requirements change frequently
- Need exploratory behavior

---

### Pattern 2: Single-Agent (15% of use cases)

**When to choose:**
- ✅ Dynamic decision-making needed
- ✅ Context maintenance is important
- ✅ Complexity is manageable by one agent
- ✅ Tool selection needs to be adaptive
- ✅ Cost-effectiveness matters

**Characteristics:**
- Flexible and context-aware
- Maintains conversation state
- Can adapt to unexpected inputs
- More complex than workflow
- Higher cost than workflow but less than multi-agent

**Best for:**
- Customer support
- Code debugging and refactoring
- Research tasks (moderate complexity)
- Interactive problem-solving
- Conversational interfaces

**Example Flow:**
```
Agent → Evaluate Context → Select Tools → Execute → Validate → Iterate or Complete
```

**When NOT to choose:**
- Task is fully predictable (use workflow)
- Requires parallel exploration (use multi-agent)
- Simple classification task (use simple prompt)

---

### Pattern 3: Multi-Agent (4% of use cases)

**When to choose:**
- ✅ Subtasks are truly independent
- ✅ Parallel execution provides value
- ✅ Different domains of expertise needed
- ✅ Comprehensive exploration required
- ✅ Task value justifies 15x token cost

**Characteristics:**
- 90% faster for complex research
- Specialized expertise per subagent
- Scales token usage effectively
- Complex orchestration needed
- Highest cost but highest capability

**Best for:**
- Comprehensive market research
- Large codebase analysis
- Multi-domain problem solving
- Parallel exploration tasks
- Complex decision support

**Example Flow:**
```
Orchestrator → Decompose Task → Spawn Subagents → Monitor Progress → Synthesize Results
```

**When NOT to choose:**
- Subtasks have dependencies (use single-agent)
- Cost is a primary concern
- Task is straightforward (use workflow or single-agent)
- Real-time response needed

---

### Pattern 4: Simple Prompt (1% of use cases)

**When to choose:**
- ✅ Single, straightforward task
- ✅ No tool use required
- ✅ Classification or basic generation
- ✅ Minimal context needed

**Characteristics:**
- Simplest possible approach
- No tool calls
- Fast and cheap
- Limited capability

**Best for:**
- Text classification
- Simple Q&A
- Basic text generation
- Sentiment analysis

**Example:**
```
Prompt: "Classify this email as spam or not spam: {email_content}"
```

**When NOT to choose:**
- Multiple steps required
- Tool use needed
- Complex reasoning required

---

## Hybrid Pattern (Recommended for Production)

**Best for**: Most production systems

**Architecture:**
```
80-90% workflow-based + 10-20% dynamic tool calling
```

**Why it works:**
- Reliability of workflows for common cases
- Flexibility of agents for edge cases
- Cost control through workflow optimization
- Easier debugging with defined protocols

**Implementation:**
1. Define workflows for 80% of predictable tasks
2. Use single-agent for edge cases and exceptions
3. Add multi-agent only for specific complex subtasks
4. Monitor and optimize based on actual usage

**Example:**
```typescript
// Main workflow handles common paths
const workflow = defineWorkflow({
  steps: [
    classifyIntent,
    routeToHandler,
    executeStandard,
    validate
  ]
});

// Agent handles exceptions
const agent = createAgent({
  onException: (error, context) => {
    // Dynamic problem-solving
    return handleDynamically(error, context);
  }
});
```

---

## Decision Checklist

Before selecting a pattern, answer these questions:

### Predictability Assessment
- [ ] Can I enumerate all possible task sequences?
- [ ] Are the requirements stable and well-defined?
- [ ] Is the success criteria clear and measurable?

**If all YES → Consider Workflow**

### Complexity Assessment
- [ ] Does the task require exploring multiple approaches?
- [ ] Are there unknown edge cases to handle?
- [ ] Does context need to be maintained across steps?

**If all YES → Consider Single-Agent**

### Parallelization Assessment
- [ ] Can the task be split into independent subtasks?
- [ ] Would parallel execution provide 2x+ speedup?
- [ ] Is the task value worth 15x token cost?

**If all YES → Consider Multi-Agent**

### Simplicity Assessment
- [ ] Is this a single, atomic task?
- [ ] Can it be solved without tools?
- [ ] Is response time critical?

**If all YES → Consider Simple Prompt**

---

## Cost vs. Capability Matrix

```
Cost →
│
│  Simple Prompt  │  Workflow      │  Single-Agent  │  Multi-Agent
├─────────────────┼────────────────┼────────────────┼──────────────
Capability
│  Low            │  Medium        │  High          │  Very High
│  $              │  $$            │  $$$           │  $$$$
│  Fast           │  Fast          │  Medium        │  Slow
│  No tools       │  Fixed tools   │  Dynamic tools │  Many tools
│  Simple tasks   │  Predictable   │  Adaptive      │  Complex
```

**Rule of Thumb:**
- Start at the left (simplest)
- Move right only when needed
- Measure improvement before committing

---

## Common Mistakes

### Mistake 1: Over-Engineering Early
**Problem**: Using multi-agent when workflow would suffice

**Solution**:
- Start with workflow
- Add complexity only when proven necessary
- Measure actual improvement

**Example:**
```
❌ Bad: Multi-agent for simple data validation
✅ Good: Workflow with defined validation steps
```

### Mistake 2: Under-Engineering for Scale
**Problem**: Using simple prompt for complex production system

**Solution**:
- Consider future requirements
- Plan for observability and error handling
- Use appropriate pattern for production needs

**Example:**
```
❌ Bad: Simple prompt for customer support system
✅ Good: Single-agent with tools and error handling
```

### Mistake 3: Ignoring Cost Implications
**Problem**: Multi-agent for high-volume, low-value tasks

**Solution**:
- Calculate cost per task
- Consider token usage
- Optimize for cost-effectiveness

**Example:**
```
❌ Bad: Multi-agent for every support ticket
✅ Good: Workflow for common cases, agent for complex ones
```

### Mistake 4: No Validation of Choice
**Problem**: Selecting pattern based on assumption, not data

**Solution**:
- Test multiple patterns
- Measure success rate, cost, latency
- Choose based on evidence

---

## Pattern Migration Path

### From Simple to Complex

**Phase 1: Start Simple**
```
Simple Prompt → Measure performance → Identify limitations
```

**Phase 2: Add Structure**
```
Workflow → Define steps → Measure improvement → Identify edge cases
```

**Phase 3: Add Flexibility**
```
Single-Agent → Handle edge cases → Measure coverage → Identify parallel opportunities
```

**Phase 4: Add Parallelization (if needed)**
```
Multi-Agent → Optimize orchestration → Measure speedup → Justify cost
```

### From Complex to Simple

**Pattern Simplification:**
1. Monitor actual usage patterns
2. Identify common paths (80% of traffic)
3. Convert common paths to workflows
4. Keep dynamic handling for edge cases
5. Measure cost reduction

---

## Success Metrics by Pattern

### Workflow Pattern
- **Task Completion**: 95%+
- **Latency**: <1s for most tasks
- **Cost**: Baseline (1x)
- **Error Rate**: <2%

### Single-Agent Pattern
- **Task Completion**: 85-95%
- **Latency**: 1-5s
- **Cost**: 2-5x workflow
- **Error Rate**: 2-5%

### Multi-Agent Pattern
- **Task Completion**: 90-98%
- **Latency**: 5-30s
- **Cost**: 15x workflow
- **Error Rate**: 1-3%

### Simple Prompt
- **Task Completion**: 70-85%
- **Latency**: <500ms
- **Cost**: 0.5x workflow
- **Error Rate**: 5-10%

---

## Quick Reference

| Pattern | Use When | Avoid When | Cost | Complexity |
|---------|----------|------------|------|------------|
| Simple Prompt | Single atomic task | Multiple steps needed | $ | Low |
| Workflow | Predictable sequence | Dynamic decisions needed | $$ | Low-Medium |
| Single-Agent | Dynamic decisions | Fully predictable or needs parallelization | $$$ | Medium |
| Multi-Agent | Independent parallel tasks | Sequential dependencies | $$$$ | High |
| Hybrid | Production systems | Prototyping | $$-$$$ | Medium-High |

---

**Remember**: The best pattern is the simplest one that meets your requirements. Start simple, add complexity only when justified by data.
