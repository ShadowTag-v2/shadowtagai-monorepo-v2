# PanelGPT Debate Skill

## Model
opus

## Purpose
Simulate panel discussions among multiple expert personas to enhance reasoning, error correction, and comprehensive problem-solving. Experts discuss, critique, and refine ideas step-by-step to reach accurate consensus.

## Enforcement
- Level: suggest
- Priority: critical

---

## Core Mechanism

### Panel Structure
- 3-5 expert personas with distinct viewpoints
- Optional moderator to facilitate
- Step-by-step contributions with critiques
- Consensus or evaluation at end

### Key Innovation
By embedding debate in the prompt, the LLM generates responses as multiple experts who:
1. Propose solutions
2. Critique each other
3. Refine based on feedback
4. Converge on best answer

---

## Implementation Templates

### Basic Panel Prompt
```
3 experts are discussing the question with a panel discussion, trying to solve it step by step, and make sure the result is correct and avoid penalty.

Question: [PROBLEM]

Expert 1: [First thought]
Expert 2: [Critique of Expert 1 + own thought]
Expert 3: [Synthesis + refinement]

[Continue rounds until consensus]

Final Answer: [SOLUTION]
```

### Named Experts with Roles
```
You are a panel of three experts - Alice, Bob, and Charles.

When given [TASK TYPE], your task is to [OBJECTIVE].

You will do this via a panel discussion, trying to solve it step by step and make sure that the result is correct.

At each stage make sure to critique and check each other's work - pointing out any possible errors.

Problem: [PROBLEM]

Alice: [Initial proposal]
Bob: [Critique + alternative]
Charles: [Synthesis]

[Continue until consensus]

Final Answer: [SOLUTION]
```

### With Moderator (Interactive)
```
You are moderating a panel discussion with the following experts:
- [Expert 1]: [Specialty]
- [Expert 2]: [Specialty]
- [Expert 3]: [Specialty]

Topic: [TOPIC]

Round 1:
Moderator: [Question]
Expert 1: [Response]
Expert 2: [Response with critique]
Expert 3: [Synthesis]

Moderator Summary: [Key points and next question]

[Continue rounds]

Final Consensus: [CONCLUSION]
```

---

## Use Cases

### Arithmetic/Logic Reasoning
```
3 experts are discussing this math problem with a panel discussion, trying to solve it step by step, and make sure the result is correct and avoid penalty.

Problem: [MATH PROBLEM]

Expert 1 (Calculator): Let me start with the basic operations...
Expert 2 (Verifier): I'll check that calculation - I see an error in step 2...
Expert 3 (Optimizer): Good catch. Here's the corrected approach...

Final Answer: [SOLUTION]
```
**Result**: 89.9% accuracy on GSM8K (vs 85.4% CoT, 84.2% ToT)

### Code Documentation
```
You are a panel of three experts on code documentation - Alice, Bob and Charles.

When given a diff containing code changes, your task is to determine any updates required to the docstrings in the code.

You will do this via a panel discussion, trying to solve it step by step and make sure that the result is correct.

At each stage make sure to critique and check each other's work - pointing out any possible errors.

Diff: [CODE CHANGES]

Alice: I suggest updating the docstring for function X because...
Bob: I disagree - that change isn't necessary because...
Charles: I agree with Bob. However, we should update Y because...

Final Answer: [JSON list of required updates]
```
**Result**: Error rate reduced from 40% (CoT) to 20%

### Interdisciplinary Analysis
```
You are Henry, moderating a panel on [TOPIC].

Panelists:
- Dr. Smith (Technical Expert)
- Prof. Jones (Business Strategist)
- Ms. Chen (User Experience)

Question: [COMPLEX QUESTION]

Dr. Smith: From a technical perspective...
Prof. Jones: The business implications are...
Ms. Chen: Users would experience...

Henry (Summary): Key themes emerging are...

[Continue with follow-up questions]

Consensus: [BALANCED CONCLUSION]
```

---

## Expert Persona Examples

### Technical Panel
- **Optimist**: Sees possibilities, proposes solutions
- **Skeptic**: Questions assumptions, finds holes
- **Pragmatist**: Balances ideals with constraints

### Domain Panel
- **Architect**: System design, patterns
- **Security**: Vulnerabilities, risks
- **Performance**: Efficiency, scalability

### Business Panel
- **Revenue**: Monetization, growth
- **Operations**: Feasibility, resources
- **Customer**: Experience, adoption

---

## Accuracy Mechanisms

### Penalty Avoidance
Include phrase: "make sure the result is correct and avoid penalty"
- Motivates error checking
- Increases self-correction

### Explicit Critique
Require: "At each stage make sure to critique and check each other's work"
- Forces peer review
- Catches logical errors

### Structured Output
Request specific format (JSON, list, etc.)
- Reduces ambiguity
- Easier validation

---

## Auto-Activation Triggers

### Keywords
- "panel"
- "experts discuss"
- "debate"
- "multiple perspectives"
- "critique"
- "consensus"

### Intent Patterns
- Complex reasoning tasks
- Code review/documentation
- Interdisciplinary questions
- Decisions requiring multiple viewpoints
- Error-prone calculations

### Problem Types
- Arithmetic reasoning
- Code analysis
- Design decisions
- Business strategy
- Technical trade-offs

---

## Quality Gates

- Minimum 3 experts participating
- Each expert provides critique of others
- Explicit consensus or majority vote
- Final answer clearly stated
- Reasoning traceable through discussion

---

## Metrics

- **GSM8K**: 89.9% accuracy (vs 85.4% CoT)
- **Code Documentation**: 20% error rate (vs 40% CoT)
- **Interdisciplinary**: More balanced, comprehensive responses

---

## Advantages

- Improves accuracy through debate
- Handles interdisciplinary topics
- Zero-shot and cost-effective
- Transparent reasoning via discussion

## Limitations

- Increases token usage (verbose)
- Relies on LLM role-playing quality
- Sensitive to prompt wording
- Best for reasoning tasks with debate value

---

## Integration Notes

### With ToT
PanelGPT adds social collaboration to ToT's branching exploration.

### With CoT
Each expert uses CoT within their contribution.

### With RCR
Panel provides critique phase; refinement follows.

### With Action Verb Analysis
Decompose problem first, then debate each verb's implementation.
