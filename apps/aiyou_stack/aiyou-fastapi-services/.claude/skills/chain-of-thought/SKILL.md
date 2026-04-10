# Chain-of-Thought (CoT) Skill

## Model

sonnet

## Purpose

Enhance reasoning by breaking complex problems into intermediate steps before arriving at a final answer. Mimics human cognitive processes to reduce errors and hallucinations.

## Enforcement


- Level: suggest

- Priority: high

---

## Core Mechanism

### Zero-Shot CoT

Append phrase to prompt:

```

Let's think step by step.

```

### Few-Shot CoT

Provide examples demonstrating sequential reasoning before the actual query.

---

## Implementation Pattern

### Step Structure


1. **Understand**: Clarify the problem

2. **Decompose**: Break into sub-problems

3. **Solve**: Address each step sequentially

4. **Synthesize**: Combine for final answer

5. **Verify**: Check logic and answer

### Prompt Template

```

Problem: [PROBLEM]

Let's think step by step:

Step 1: [First reasoning step]
Step 2: [Second reasoning step]
Step 3: [Third reasoning step]
...

Therefore, the answer is: [FINAL ANSWER]

```

---

## Use Cases

### Math/Logic

```

Problem: If John has 5 apples and gives 2 to Mary, then buys 3 more, how many does he have?

Let's think step by step:
Step 1: John starts with 5 apples
Step 2: John gives 2 to Mary: 5 - 2 = 3 apples
Step 3: John buys 3 more: 3 + 3 = 6 apples

Therefore, the answer is: 6 apples

```

### Code Generation

```

Task: Write a function to find the longest palindrome substring

Let's think step by step:
Step 1: Consider expanding from center approach
Step 2: For each index, expand outward checking for palindrome
Step 3: Track the longest found
Step 4: Handle both odd and even length palindromes

Implementation:
[CODE]

```

### Decision Making

```

Decision: Should we migrate to microservices?

Let's think step by step:
Step 1: Assess current monolith pain points
Step 2: Evaluate team capacity for distributed systems
Step 3: Calculate migration cost vs. maintenance cost
Step 4: Consider latency/complexity tradeoffs

Recommendation: [DECISION WITH REASONING]

```

---

## Auto-Activation Triggers

### Keywords


- "step by step"

- "think through"

- "reason about"

- "break down"

- "explain reasoning"

- "show work"

### Intent Patterns


- Complex calculations

- Multi-step logic problems

- Decision analysis

- Code implementation requiring planning

### Problem Types


- Mathematical reasoning

- Logical deduction

- Code architecture decisions

- Business analysis

---

## Quality Gates


- Each step must logically follow from previous

- No skipped reasoning jumps

- Final answer explicitly stated

- Steps can be independently verified

---

## Metrics


- **Accuracy**: CoT improves accuracy 5-15% on reasoning benchmarks

- **Transparency**: Every conclusion traceable to explicit step

- **Error Detection**: Easier to identify where reasoning fails

---

## Integration Notes


- **With ToT**: Use CoT within each branch of thought tree

- **With RCR**: Apply CoT in refinement cycles

- **With MAD**: Each agent uses CoT for their reasoning

- **With Prompt Frameworks**: Embed CoT in RISE "Steps" component

---

## Limitations


- May increase verbosity

- Less effective for simple factual queries

- Best for tasks requiring logic, not creativity
