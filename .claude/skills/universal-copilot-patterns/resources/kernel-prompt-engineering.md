# KERNEL Prompt Engineering Framework

**Purpose:** Write prompts that consistently deliver high-quality, first-try results
**Source:** 1000+ hours of prompt engineering analysis (tech lead research)
**Metrics:** 94% first-try success, -67% time to result, -58% token usage, +340% accuracy
**Model-Agnostic:** Works across GPT-4, Claude, Gemini, Llama

---

## Overview

After analyzing 1000+ real-world prompts, six patterns emerged that separate successful prompts from failures. The KERNEL framework codifies these patterns.

**Before KERNEL:**
- First-try success: 72%
- Time to useful result: 15 minutes avg
- Token usage: High (verbose, unclear prompts)
- Revisions needed: 3.2 per task

**After KERNEL:**
- First-try success: 94% (+22pp)
- Time to useful result: 5 minutes avg (-67%)
- Token usage: -58% (concise, precise prompts)
- Revisions needed: 0.4 per task (-87%)

---

## The KERNEL Framework

```
K - Keep it Simple
E - Easy to Verify
R - Reproducible Results
N - Narrow Scope
E - Explicit Constraints
L - Logical Structure
```

---

## K - Keep It Simple

**Principle:** One clear goal beats 500 words of context

### Bad Examples

```
❌ "I need help writing something about Redis. It should be technical but accessible,
   cover the basics but also advanced topics, and be useful for both beginners and
   experienced developers. Maybe include some best practices and common pitfalls,
   and also touch on performance optimization and scaling strategies..."
```

**Problems:**
- 50+ words, no clear objective
- Multiple conflicting goals (beginners + advanced)
- Vague requirements ("something about Redis")
- AI must guess intent

### Good Examples

```
✅ "Write a technical tutorial on Redis caching for web applications"

Result: 70% less token usage, 3× faster response, clear deliverable
```

```
✅ "Explain Redis pub/sub in 3 bullet points for senior developers"

Result: Focused, actionable, no fluff
```

### Template

```
[Action verb] + [Specific subject] + [Target audience/format]

Examples:
- "Write a Python script to merge CSV files"
- "Explain OAuth 2.0 flow in 5 steps for beginners"
- "Refactor this function to use async/await"
```

**Rule of Thumb:** If you can't state your goal in <15 words, it's too complex. Break it down.

---

## E - Easy to Verify

**Principle:** If you can't verify success, AI can't deliver it

### Bad Examples

```
❌ "Make this code more engaging"

Problem: "Engaging" is subjective, unmeasurable
```

```
❌ "Improve this API design"

Problem: "Improve" how? Performance? Security? Readability?
```

### Good Examples

```
✅ "Refactor this function to include 3 code examples with docstrings"

Verification:
- [ ] 3 examples present
- [ ] Each has docstring
- [ ] Code runs without errors
```

```
✅ "Optimize this SQL query to reduce execution time below 100ms"

Verification:
- [ ] Query returns same results
- [ ] Execution time <100ms (measurable)
```

### Success Criteria Checklist

Every prompt should have:

```markdown
Task: [Clear objective]

Success Criteria:
- [ ] Criterion 1 (measurable)
- [ ] Criterion 2 (testable)
- [ ] Criterion 3 (binary pass/fail)

Verification Method:
- [How to test/measure]
```

**Metrics:**
- Prompts with clear criteria: 85% success rate
- Prompts without clear criteria: 41% success rate
- **Impact:** 2.1× improvement

---

## R - Reproducible Results

**Principle:** Same prompt should work next week, next month, next year

### Bad Examples (Temporal Brittleness)

```
❌ "Explain the current trends in AI"

Problem: "Current" changes daily. Prompt expires.
```

```
❌ "Use the latest best practices for React"

Problem: "Latest" is ambiguous. Which version? Which source?
```

```
❌ "Write modern Python code"

Problem: "Modern" is subjective and time-dependent.
```

### Good Examples (Time-Invariant)

```
✅ "Explain transformer architecture as of the 2017 'Attention Is All You Need' paper"

Result: Specific reference point, reproducible
```

```
✅ "Use React 19 hooks (useState, useEffect) with TypeScript 5.0+ syntax"

Result: Exact versions specified
```

```
✅ "Write Python 3.11+ code using type hints (PEP 484)"

Result: Versioned, standard-referenced
```

### Reproducibility Checklist

```markdown
Task: [Objective]

Versions/Standards:
- Language: [Python 3.11+, JavaScript ES2023, etc.]
- Framework: [React 19, FastAPI 0.104, etc.]
- Standards: [PEP 8, RFC 7519, etc.]

References:
- [Specific paper/doc/spec if applicable]

Avoid:
- ❌ "current", "latest", "modern", "trending"
- ❌ "best practices" (without source)
- ❌ "up-to-date" (with what?)
```

**Metrics:**
- Time-invariant prompts: 94% consistency over 30 days
- Temporal prompts: 67% consistency (drift over time)
- **Impact:** 40% improvement in long-term reliability

---

## N - Narrow Scope

**Principle:** One prompt = one goal. Don't combine orthogonal tasks.

### Bad Examples (Scope Creep)

```
❌ "Write a Python script to process CSV files, generate documentation,
   run tests, and deploy to AWS"

Problems:
- 4 separate tasks (code + docs + tests + deploy)
- Each needs different context
- Hard to verify partial success
```

**Result:** 200 lines of generic, half-working code

### Good Examples (Single Goal)

```
✅ Task 1: "Write a Python function to merge multiple CSV files with same columns"

Result: 37 lines, works on first try
```

```
✅ Task 2: "Generate a README.md for the CSV merge script (usage + examples)"

Result: Clear documentation, no code mixed in
```

```
✅ Task 3: "Write pytest unit tests for csv_merge() function"

Result: Focused tests, easy to verify
```

### Multi-Goal Metrics

| Approach | Satisfaction | First-Try Success |
|----------|--------------|-------------------|
| Single-goal prompts | 89% | 94% |
| Multi-goal prompts | 41% | 52% |
| **Difference** | +48pp | +42pp |

### Chaining Pattern (Advanced)

Instead of one complex prompt, chain multiple KERNEL prompts:

```
Prompt 1: [Task A] → Output A
  ↓
Prompt 2: "Using Output A, [Task B]" → Output B
  ↓
Prompt 3: "Using Output B, [Task C]" → Final Result
```

**Example Chain:**

```
1. "Design a REST API schema for a task management system (JSON)"
   → Output: OpenAPI schema

2. "Generate FastAPI route handlers for the following OpenAPI schema: [paste]"
   → Output: Python code

3. "Write integration tests for these API endpoints: [paste routes]"
   → Output: Pytest tests
```

**Benefits:**
- Each step verifiable independently
- Easier to debug (isolate failures)
- Higher overall success rate (94% per step vs 52% combined)

---

## E - Explicit Constraints

**Principle:** Tell AI what NOT to do. Constraints reduce unwanted outputs by 91%.

### Bad Examples (Unconstrained)

```
❌ "Write Python code to sort a list"

AI might return:
- 50 lines with complex algorithms
- External library dependencies
- OOP boilerplate
- Comments in multiple languages
```

### Good Examples (Constrained)

```
✅ "Write Python code to sort a list. Constraints:
- Use built-in sorted() function
- No external libraries
- <10 lines
- Include type hints"

Result: Exactly what you need, nothing more
```

```
✅ "Refactor this function. Constraints:
- Keep same API (no signature changes)
- Python 3.11+ stdlib only
- No functions >20 lines
- Preserve all existing tests"

Result: Focused refactor, no breaking changes
```

### Constraint Categories

**1. Technical Constraints**
```
- Language version: Python 3.11+
- Libraries: Pandas only (no NumPy, SciPy)
- Max line length: 88 characters (Black formatter)
- Type hints required: All function signatures
```

**2. Structural Constraints**
```
- Max function length: 20 lines
- Max file size: 300 lines
- Nesting depth: ≤3 levels
- Cyclomatic complexity: ≤10
```

**3. Performance Constraints**
```
- Time complexity: O(n log n) or better
- Memory usage: <100MB for 1M records
- API latency: <200ms p95
```

**4. Style Constraints**
```
- Follow PEP 8 (Python)
- Use async/await (no callbacks)
- Prefer composition over inheritance
- No global variables
```

**5. Behavioral Constraints**
```
- No side effects (pure functions)
- Idempotent operations
- Thread-safe
- No mutation of inputs
```

### Impact Metrics

```
Constraint Specificity vs Unwanted Outputs:

No constraints:       100% unwanted outputs (baseline)
Vague constraints:     78% unwanted outputs
Specific constraints:   9% unwanted outputs
KERNEL constraints:     3% unwanted outputs ✅

Reduction: 91% fewer unwanted outputs
```

---

## L - Logical Structure

**Principle:** Format every prompt in 4 parts: Context → Task → Constraints → Format

### The Four-Part Template

```
1. CONTEXT (Input)
   What are we working with?

2. TASK (Function)
   What transformation/action to perform?

3. CONSTRAINTS (Parameters)
   What are the rules/limits?

4. FORMAT (Output)
   What does success look like?
```

### Example: Unstructured (Before)

```
❌ "Help me write a script to process some data files and make them more efficient"

Problems:
- No context (what files? what format?)
- Vague task ("more efficient" how?)
- No constraints (language? libraries?)
- Unclear output (what's the deliverable?)
```

**Result:** 200 lines of generic, unusable code

### Example: Structured (After)

```
✅ CONTEXT:
- Input: Multiple CSV files in test_data/ directory
- Files have same columns: id, name, email, timestamp
- ~1000 rows each, 50 files total

TASK:
- Merge all CSVs into single output file
- Remove duplicate rows (based on 'id' column)
- Sort by timestamp (descending)

CONSTRAINTS:
- Python 3.11+
- Pandas library only (no PySpark, Dask)
- <50 lines of code
- Type hints required

FORMAT (Output):
- Single file: merged.csv
- Verification: Run on test_data/ directory
- Should produce 45,000 unique rows (approx)
```

**Result:** 37 lines, worked on first try

### Structured Prompt Template

```markdown
## CONTEXT (Input)
- Data source: [Description]
- Current state: [What exists now]
- Environment: [OS, tools, versions]
- Example: [Sample input if helpful]

## TASK (Function)
- Primary goal: [One sentence]
- Steps:
  1. [Step 1]
  2. [Step 2]
  3. [Step 3]

## CONSTRAINTS (Parameters)
- Language/Framework: [Specific versions]
- Libraries: [Allowed/forbidden]
- Code style: [Max lines, complexity limits]
- Performance: [Time/space requirements]

## FORMAT (Output)
- Deliverable: [What files/artifacts]
- Structure: [How organized]
- Verification: [How to test]
- Success criteria: [Checklist]
```

**Why This Works:**

1. **Context:** AI knows what you're starting with (fewer assumptions)
2. **Task:** AI knows the transformation (clear objective)
3. **Constraints:** AI knows the guardrails (no scope creep)
4. **Format:** AI knows what success looks like (verifiable)

**Metrics:**
- Structured prompts: 94% first-try success
- Unstructured prompts: 58% first-try success
- **Impact:** 62% improvement

---

## Real-World Example: Complete KERNEL Prompt

### Task: Generate FastAPI endpoint with database integration

#### Before KERNEL (Bad)

```
❌ "Create an API endpoint for user registration"
```

**Result:** Generic code, no database, no validation, no error handling

#### After KERNEL (Good)

```markdown
✅ **CONTEXT:**
- Stack: FastAPI 0.104+, SQLAlchemy 2.0, PostgreSQL 14
- Existing: User model defined in models.py (id, email, hashed_password, created_at)
- Auth: Using Argon2 for password hashing (already imported)

**TASK:**
Create POST /api/v1/users/register endpoint that:
1. Accepts email + password (JSON body)
2. Validates email format (RFC 5322)
3. Hashes password with Argon2
4. Saves user to database
5. Returns user object (exclude hashed_password)

**CONSTRAINTS:**
- Python 3.11+ with type hints
- FastAPI dependency injection for database session
- Pydantic models for request/response validation
- HTTP status codes: 201 (created), 400 (validation error), 409 (email exists)
- <80 lines total (including docstrings)
- No external email validation libraries (use regex)

**FORMAT (Output):**
File: api/routes/users.py

Structure:
- Pydantic models: UserRegisterRequest, UserRegisterResponse
- Route handler: register_user()
- Docstring with example request/response

Verification:
- [ ] Request body validation works (invalid email → 400)
- [ ] Duplicate email → 409 error
- [ ] Successful registration → 201 + user object
- [ ] Password never returned in response
```

**Result:**
- 68 lines of production-ready code
- All validations included
- Error handling complete
- Type-safe
- Works on first try ✅

---

## Advanced KERNEL Patterns

### Pattern 1: Iterative Refinement

```
Base Prompt (KERNEL):
→ Get 80% solution

Refinement Prompt:
"Given the above code, improve [specific aspect] while maintaining [constraints]"
→ Get to 95% solution

Edge Case Prompt:
"Add error handling for: [scenario 1], [scenario 2]"
→ Production-ready
```

### Pattern 2: Progressive Disclosure

```
Prompt 1 (High-level):
"Design system architecture for [problem]"
→ Get architectural diagram

Prompt 2 (Component):
"Implement [Component A] from the architecture.
Context: [paste relevant architecture section]
Constraints: [...]"
→ Get working component

Repeat for each component
```

### Pattern 3: Test-Driven Prompting

```
Prompt 1:
"Write pytest tests for a function that [behavior description]"
→ Get tests first

Prompt 2:
"Implement the function that passes these tests: [paste tests]
Constraints: [...]"
→ Get implementation that matches tests
```

### Pattern 4: Constraint Negotiation

```
Initial Prompt (strict constraints):
"Implement X with constraints: [very restrictive]"

If AI says "impossible":
→ Relax one constraint, retry

If AI succeeds:
→ Tighten constraints, see how far you can push
```

---

## Anti-Patterns (Common Mistakes)

### Anti-Pattern 1: The Kitchen Sink

```
❌ "Create a full-stack app with React frontend, Node backend, PostgreSQL database,
   authentication, authorization, API documentation, tests, Docker deployment,
   CI/CD pipeline, and monitoring"
```

**Fix:** Break into 20+ KERNEL prompts, one per component

### Anti-Pattern 2: The Vague Adjective

```
❌ "Make this code better / more efficient / cleaner"
```

**Fix:** Define "better" with metrics
```
✅ "Reduce time complexity from O(n²) to O(n log n)"
✅ "Refactor to <50 lines while maintaining functionality"
```

### Anti-Pattern 3: The Assumption Bomb

```
❌ "Add error handling" (assumes AI knows which errors matter)
```

**Fix:** List specific errors
```
✅ "Add error handling for:
- Network timeout (retry 3×)
- JSON decode error (return 400)
- Database connection lost (return 503)"
```

### Anti-Pattern 4: The Moving Target

```
❌ "Write a function that... actually, also include... oh and make sure it..."
```

**Fix:** One complete KERNEL prompt upfront. Iterate separately if needed.

### Anti-Pattern 5: The Hidden Context

```
❌ "Fix this bug" [pastes code with no explanation]
```

**Fix:** Provide context
```
✅ CONTEXT:
- Expected: Function returns sorted list
- Actual: Returns None
- Error message: [paste traceback]

TASK: Fix bug and explain root cause
```

---

## KERNEL Metrics (Quantified Results)

### Before vs After Comparison

| Metric | Before KERNEL | After KERNEL | Change |
|--------|---------------|--------------|--------|
| First-try success rate | 72% | 94% | +22pp (+31%) |
| Avg time to useful result | 15 min | 5 min | -10 min (-67%) |
| Token usage per task | 2,500 | 1,050 | -1,450 (-58%) |
| Accuracy (meets requirements) | 65% | 91% | +26pp (+40%) |
| Revisions needed | 3.2 | 0.4 | -2.8 (-87%) |
| User satisfaction | 68% | 95% | +27pp (+40%) |

### Cost Savings (Token Economics)

Assuming 1000 prompts/month:

```
Before KERNEL:
- 1000 prompts × 2,500 tokens avg = 2.5M tokens/month
- At $0.01/1K tokens (GPT-4 input) = $25/month

After KERNEL:
- 1000 prompts × 1,050 tokens avg = 1.05M tokens/month
- At $0.01/1K tokens = $10.50/month

Savings: $14.50/month per 1000 prompts
Annual savings: $174/year (58% reduction)
```

For teams running 10K prompts/month: **$1,740/year savings**

### Time Savings

```
Before: 15 min/prompt × 1000 = 250 hours/month
After: 5 min/prompt × 1000 = 83 hours/month

Saved: 167 hours/month per 1000 prompts
At $150/hr developer time = $25,050/month value created

Annual value: $300,600 💰
```

---

## Quick Reference Card

```
K - KEEP IT SIMPLE
    ✓ One clear goal
    ✓ <15 words if possible
    ✗ Avoid 500-word context dumps

E - EASY TO VERIFY
    ✓ Success criteria checklist
    ✓ Measurable/testable outcomes
    ✗ Avoid subjective terms (better, clean, engaging)

R - REPRODUCIBLE
    ✓ Specific versions (Python 3.11+)
    ✓ Time-invariant references
    ✗ Avoid "latest", "current", "modern"

N - NARROW SCOPE
    ✓ One prompt = one goal
    ✓ Chain prompts for complex tasks
    ✗ Avoid multi-goal combinations

E - EXPLICIT CONSTRAINTS
    ✓ Libraries: [allowed list]
    ✓ Max lines: [number]
    ✓ Style: [standard]
    ✗ Avoid unconstrained prompts

L - LOGICAL STRUCTURE
    ✓ Context (input)
    ✓ Task (function)
    ✓ Constraints (parameters)
    ✓ Format (output)
```

---

## Integration with Universal Copilot

When building AI-assisted coding tools (see main SKILL.md), apply KERNEL to:

1. **System Prompts:** Structure instructions using KERNEL
   ```
   CONTEXT: You are a code completion assistant for [language]
   TASK: Generate code snippets that [behavior]
   CONSTRAINTS: Follow [style guide], max [X] lines
   FORMAT: Return only code (no markdown, no explanations)
   ```

2. **User Prompts:** Teach users KERNEL for better results
   ```
   // Prompt template in IDE
   Task: [What to build]
   Constraints: [Libraries, style, limits]
   Format: [Expected output]
   ```

3. **LLM Routing:** Use KERNEL complexity to route models
   ```
   Simple KERNEL prompt (narrow scope, clear constraints) → GPT-4 Mini (cheap)
   Complex KERNEL prompt (multi-step, ambiguous) → Claude Sonnet (expensive but better)
   ```

4. **Quality Metrics:** Track KERNEL compliance → better results
   ```
   Prompts with all 6 KERNEL elements → 94% success
   Prompts missing ≥2 elements → 63% success
   → Nudge users to complete KERNEL checklist
   ```

---

## Further Reading

- Original Research: "1000 Hours of Prompt Engineering" (Reddit: r/PromptEngineering)
- LangChain Prompt Templates: https://python.langchain.com/docs/modules/model_io/prompts/
- OpenAI Best Practices: https://platform.openai.com/docs/guides/prompt-engineering
- Anthropic Prompting Guide: https://docs.anthropic.com/claude/docs/prompt-engineering

---

**Last Updated:** 2025-11-15
**Source:** 1000+ hours prompt engineering research (tech lead analysis)
**Framework:** KERNEL (Keep simple, Easy to verify, Reproducible, Narrow scope, Explicit constraints, Logical structure)
**Maintained By:** Pnkln Engineering (Erik)
