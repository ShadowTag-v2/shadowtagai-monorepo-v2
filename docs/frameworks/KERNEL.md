# KERNEL Prompt Engineering Framework

## Overview

KERNEL is a prompt engineering framework discovered through analysis of 1000+ real-world prompts. It provides six consistent patterns that improve prompt success rates, reduce token usage, and ensure reproducible results across different AI models.

**KERNEL is model-agnostic** - works consistently across GPT-5, Claude, Gemini, and Llama.

## Measured Impact

Real metrics from applying KERNEL to 1000 prompts:

- **First-try success**: 72% → 94% (+22 percentage points)
- **Time to useful result**: -67%
- **Token usage**: -58%
- **Accuracy improvement**: +340%
- **Revisions needed**: 3.2 → 0.4 (-87%)

## The Six Patterns

### K - Keep it Simple

**Principle**: One clear goal per prompt.

**Bad Example**:

```
I need help writing something about Redis. I'm thinking about maybe covering caching,
persistence, data structures, clustering, and perhaps some best practices for production
deployments. Also maybe some comparison with other caching solutions and when to use what...
```

**Good Example**:

```
Write a technical tutorial on Redis caching
```

**Impact**: 70% less token usage, 3x faster responses

**Guidelines**:

- Replace verbose context dumps with concise goal statements
- Limit introductory context to 1-2 sentences maximum
- State the end goal directly

---

### E - Easy to Verify

**Principle**: Include clear success criteria.

**Bad Example**:

```
Make the documentation engaging and user-friendly
```

**Good Example**:

```
Rewrite the documentation with:
- 3 code examples minimum
- Step-by-step installation guide
- Troubleshooting section with 5 common issues
```

**Impact**: 85% success rate with clear criteria vs 41% without

**Guidelines**:

- Replace subjective requirements ("engaging", "clean", "professional") with measurable ones
- Specify exact quantities where possible
- Define what "done" looks like
- If you can't verify success, AI can't deliver it

---

### R - Reproducible Results

**Principle**: Same prompt should work next week, next month.

**Bad Example**:

```
Analyze current trends in machine learning and latest best practices
```

**Good Example**:

```
Analyze machine learning trends from January-December 2024, focusing on:
- Transformer architecture improvements
- Model compression techniques (quantization, pruning)
- Production deployment patterns
```

**Impact**: 94% consistency across 30 days in tests

**Guidelines**:

- Avoid temporal references ("current", "latest", "recent", "modern")
- Use specific versions, dates, or ranges
- Specify exact technologies/frameworks/libraries
- Make prompts self-contained

---

### N - Narrow Scope

**Principle**: One prompt = one goal.

**Bad Example**:

```
Build a complete REST API with authentication, database models, tests,
documentation, deployment scripts, and monitoring
```

**Good Example**:

```
Prompt 1: Design database schema for user authentication
Prompt 2: Implement JWT authentication endpoints
Prompt 3: Write integration tests for auth flow
[Continue with separate prompts for each component]
```

**Impact**: 89% satisfaction for single-goal vs 41% for multi-goal prompts

**Guidelines**:

- Don't combine code + docs + tests in one request
- Split complex tasks into sequential prompts
- Each prompt should have one primary deliverable
- Chain prompts instead of creating complex ones

---

### E - Explicit Constraints

**Principle**: Tell AI what NOT to do.

**Bad Example**:

```
Write a Python script to process data
```

**Good Example**:

```
Write a Python script to process data
Constraints:
- No external libraries except pandas
- No functions over 20 lines
- No global variables
- Include type hints
- Maximum execution time: 5 seconds
```

**Impact**: Constraints reduce unwanted outputs by 91%

**Guidelines**:

- Specify forbidden libraries/patterns
- Set code quality bounds (line limits, complexity)
- Define performance requirements
- Specify what to avoid (anti-patterns, deprecated features)

---

### L - Logical Structure

**Principle**: Format every prompt with consistent sections.

**Template**:

```
1. Context (input)
2. Task (function)
3. Constraints (parameters)
4. Format (output)
```

**Example Application**:

**Before KERNEL**:

```
Help me write a script to process some data files and make them more efficient
```

Result: 200 lines of generic, unusable code

**After KERNEL**:

```
Task: Python script to merge CSVs
Input: Multiple CSVs in ./data/, identical column structure
Constraints:
- Pandas only
- Under 50 lines
- Preserve column order
Output: Single merged.csv in ./output/
Verify: Run on test_data/ directory
```

Result: 37 lines, worked on first try

---

## Usage Patterns

### Basic Prompt Structure

```
CONTEXT:
[What is the current situation/input]

TASK:
[What specific action needs to be performed]

CONSTRAINTS:
- [Technical constraint 1]
- [Limitation 2]
- [Requirement 3]

OUTPUT FORMAT:
[Exact format expected]

VERIFICATION:
[How to validate success]
```

### Advanced: Prompt Chaining

Instead of one complex prompt, chain multiple KERNEL prompts where each feeds into the next:

```
Prompt 1 (Analysis):
Task: Analyze codebase structure
Input: ./src directory
Constraints: Focus on API endpoints only
Output: JSON list of endpoints with methods
Verify: Count matches route definitions

Prompt 2 (Documentation):
Task: Generate API documentation
Input: [Output from Prompt 1]
Constraints: OpenAPI 3.0 format
Output: swagger.yaml
Verify: Validates against OpenAPI spec

Prompt 3 (Testing):
Task: Create integration tests
Input: [Output from Prompt 1]
Constraints: pytest, <100 lines per test
Output: test_api.py
Verify: All tests pass
```

---

## Model-Specific Notes

### Claude (Sonnet, Opus)

- Excels with structured constraints
- Responds well to explicit anti-patterns
- Use detailed output format specifications

### GPT (4, 5)

- Benefits from examples in constraints
- Strong with logical structure
- May need more explicit scope narrowing

### Gemini

- Performs well with context-task separation
- Responsive to verification criteria
- Good at maintaining reproducibility with specific versions

### Llama

- Requires more explicit constraints
- Benefits from simpler language in task descriptions
- Keep context sections especially concise

---

## Common Anti-Patterns to Avoid

❌ **Vague objectives**: "make it better", "improve performance", "clean up"
✅ **Specific goals**: "reduce function complexity to <10", "improve latency to <100ms", "refactor to single responsibility"

❌ **Multiple goals**: "build the API and write docs and add tests"
✅ **Single focus**: "build the API" (then separate prompts for docs and tests)

❌ **No constraints**: "write a function"
✅ **Clear bounds**: "write a pure function, <15 lines, type hints required"

❌ **Temporal references**: "use latest best practices"
✅ **Specific standards**: "follow PEP 8 style guide, Python 3.11+ features"

---

## KERNEL Checklist

Before submitting a prompt, verify:

- [ ] **K - Keep it Simple**: Single clear goal stated upfront?
- [ ] **E - Easy to Verify**: Concrete success criteria defined?
- [ ] **R - Reproducible**: No temporal/relative references?
- [ ] **N - Narrow Scope**: Only one primary deliverable?
- [ ] **E - Explicit Constraints**: What NOT to do specified?
- [ ] **L - Logical Structure**: Context → Task → Constraints → Output?

---

## Integration with PNKLN Core Stack™

KERNEL principles apply across all PNKLN component analyses:

1. **Judge Systems**: Clear validation criteria (E), narrow scope to single validation type (N)
2. **Ingestion Layers**: Explicit ethical constraints (E), reproducible source configs (R)
3. **API Services**: Structured input/output specs (L), simple endpoint goals (K)
4. **Analysis Prompts**: Verifiable metrics (E), narrow analysis scope (N)

See: [Gemini Ingestion Layer Prompt](../prompts/gemini-ingestion-layer.md) for a complete example applying KERNEL.

---

## References

- Original research: 1000+ prompts analyzed over 1 year
- Tested across: GPT-5, Claude Sonnet/Opus, Gemini 2.0 Pro, Llama
- Production deployment: Used in tech lead workflows
- Team adoption: 2x improvement in AI-assisted development velocity

---

## Version History

- **v1.0** (2025-11-15): Initial framework documentation
- Based on 1000 hours of prompt engineering analysis

---

## Next Steps

1. **Apply KERNEL**: Use the checklist on your next prompt
2. **Measure Impact**: Track before/after metrics (success rate, revisions, time)
3. **Share Results**: Contribute improvements back to framework
4. **Tool Integration**: Use KERNEL linting/validation tools (see `src/prompt_engineering/`)
