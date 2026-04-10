# Prompt Frameworks Skill

## Model

sonnet

## Purpose

Structured prompt engineering templates for crafting effective AI inputs. Provides RTF, TAG, BAB, CARE, and RISE frameworks for consistent, targeted responses.

## Enforcement


- Level: suggest

- Priority: high

---

## Frameworks

### RTF (Role-Task-Format)

**Use for**: Role-playing prompts, content generation

```

Role: Act as a [ROLE]
Task: Create a [TASK]
Format: Deliver in [FORMAT]

```

**Example**:

```

Role: Act as a Facebook Ad Marketer
Task: Design a compelling ad campaign for sustainable fashion
Format: Include headline, body copy, CTA, and targeting suggestions

```

---

### TAG (Task-Action-Goal)

**Use for**: Goal-oriented or performance tasks

```

Task: Define the [TASK]
Action: State the [ACTION] required
Goal: Specify the [GOAL] outcome

```

**Example**:

```

Task: Improve team performance metrics
Action: Analyze current workflows and identify bottlenecks
Goal: Increase productivity score from 6.0 to 7.5 within Q1

```

---

### BAB (Before-After-Bridge)

**Use for**: Transformation planning, copywriting

```

Before: Explain problem [BEFORE] state
After: Describe desired [AFTER] state
Bridge: Define the [BRIDGE] to connect them

```

**Example**:

```

Before: Website ranks page 5 for target keywords
After: Achieve top 10 ranking within 90 days
Bridge: Implement technical SEO audit, content optimization, and backlink strategy

```

---

### CARE (Context-Action-Result-Example)

**Use for**: Contextual tasks with examples

```

Context: Give the [CONTEXT]
Action: Describe [ACTION] needed
Result: Clarify the [RESULT] expected
Example: Provide [EXAMPLE] for reference

```

**Example**:

```

Context: Launching sustainable clothing line for Gen Z
Action: Create social media campaign
Result: Drive 10K signups in first month
Example: Reference Patagonia's "Don't Buy This Jacket" campaign

```

---

### RISE (Role-Input-Steps-Expectation)

**Use for**: Detailed, process-oriented tasks

```

Role: Specify the [ROLE]
Input: Describe [INPUT] data
Steps: Ask for [STEPS] to follow
Expectation: Describe the [EXPECTATION]

```

**Example**:

```

Role: Content strategist
Input: Audience insights (25-34 tech professionals), past blog performance
Steps: 1. Audit existing content 2. Identify gaps 3. Create editorial calendar
Expectation: Increase blog visitors by 40% in 6 months

```

---

## Auto-Activation Triggers

### Keywords


- "prompt template"

- "framework"

- "RTF"

- "TAG"

- "BAB"

- "CARE"

- "RISE"

- "structure prompt"

### Intent Patterns


- Requesting structured input format

- Content generation tasks

- Goal-oriented planning

- Transformation projects

---

## Quality Gates


- Each framework component must be filled

- Output format explicitly specified

- Example provided when using CARE

- Goal measurable when using TAG/RISE

---

## Integration Notes


- Combine with CoT for step-by-step reasoning within frameworks

- Use with ToT for exploring multiple framework approaches

- Layer with RCR for iterative refinement of prompts
