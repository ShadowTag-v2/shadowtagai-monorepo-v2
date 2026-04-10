# Multi-Agent Debate (MAD) Skill

## Model
opus

## Purpose
Leverage iterative debates among multiple virtual agents to enhance reasoning, factuality, and problem-solving. Agents propose, critique, and refine through multiple rounds to reach accurate consensus, with optional DTE self-evolution.

## Enforcement
- Level: suggest
- Priority: critical

---

## Core Mechanism

### Agent Structure
- 2-5 agents with distinct roles/perspectives
- Multiple debate rounds (3-5 typical)
- REFLECT-CRITIQUE-REFINE (RCR) prompting
- Consensus or judge evaluation at end

### Key Innovation
Through iterative argumentation:
1. Overcome individual biases
2. Reduce hallucinations
3. Self-correct errors
4. Achieve robust consensus

---

## RCR Prompting Strategy

### For Each Round

#### 1. REFLECT
Agent critiques own previous reasoning:
```
Self-critique: I need to review my previous answer...
- Error found: [specific issue]
- Improvement needed: [correction]
```

#### 2. CRITIQUE
Evaluate exactly two peers:
```
Critique of Agent 2: Their step 3 has a flaw because...
Critique of Agent 3: Good reasoning but missing edge case...
```

#### 3. REFINE
Update response based on feedback:
```
Refined Answer: Based on critiques, I now propose...
Novel Step: [new reasoning not in prior traces]
```

---

## Implementation Templates

### Basic MAD Prompt
```
You are Agent [ID] in a multi-agent debate to solve [TASK TYPE]:

Problem: [PROBLEM]

Your previous answer: [PREVIOUS]

Other agents' solutions: [CONTEXT]

This is debate round [N]. Please:
1. REFLECT on your reasoning - identify any errors
2. CRITIQUE two peers - point out specific flaws
3. REFINE your answer - include novel steps if changing

If your answer is correct, defend it.
If you made an error, explain and correct it.
If another agent is right, explain why and adopt their approach.

Final answer must be in format: \boxed{answer}
```

### Math Reasoning (GSM8K)
```
You are Agent {agent_id} in a multi-agent debate to solve the following math problem:

Problem: {question}

{own_previous}

Here are the solutions from other agents: {context}

This is debate round {round_num}. Please carefully analyze all solutions—including your own—identify any errors in reasoning, and provide your revised solution.

• If you believe your previous answer is correct, explain why and defend it.
• If you believe you made an error, explain the error and provide a corrected solution.
• If you believe another agent's answer is correct, explain why you agree with it.

Your final answer must be in the format \boxed{{answer}} at the end.
```

### Science Reasoning (ARC)
```
You are Agent {agent_id} in a multi-agent debate to solve the following scientific problem:

Problem: {question}

{own_previous}

Here are the solutions from other agents: {context}

This is debate round {round_num}. Please carefully analyze all solutions—including your own—identify any misconceptions or flawed scientific reasoning, and provide your revised solution.

• If you believe your previous answer is correct, explain the scientific principles supporting your answer.
• If you believe you made an error, explain the scientific misconception and provide a corrected solution.
• If you believe another agent's answer is correct, explain why their scientific reasoning is sound.

Your final answer must be in the format \boxed{{answer}} at the end.
```

### Code Review/Debugging
```
You are Agent {agent_id} in a multi-agent debate to debug and refine the following code:

Problem: {question}

{own_previous}
Execution Feedback: {execution_feedback}

Here are the solutions from other agents: {context}

This is debate round {round_num}. Please carefully analyze all solutions—including your own—identify any runtime errors, test failures, or security issues, and provide your refined code solution.

• If your code is correct, explain how it passes tests and defend it.
• If you made an error, explain the issue based on feedback and provide corrected code.
• If another agent's code is better, explain why and incorporate it.

Your final code must be in a Python fenced code block followed by \boxed{{final_answer}}.
```

---

## Agent Role Examples

### Debate Roster
```python
AGENT_ROLES = {
    "OPTIMIST": "Sees possibilities, proposes ambitious solutions",
    "SKEPTIC": "Questions assumptions, finds edge cases",
    "PRAGMATIST": "Balances ideals with constraints",
    "SYNTHESIZER": "Combines best elements from all",
}
```

### Technical Roster
```python
TECHNICAL_ROLES = {
    "ARCHITECT": "System design, patterns, structure",
    "SECURITY": "Vulnerabilities, risks, compliance",
    "PERFORMANCE": "Efficiency, scalability, optimization",
    "QUALITY": "Testing, edge cases, reliability",
}
```

---

## DTE Self-Evolution Integration

MAD produces debate traces for DTE training:

### 1. DEBATE Phase
Run RCR-MAD to generate diverse reasoning traces.

### 2. TRAIN Phase
Use GRPO on traces to update policy:
- Reward correct answers
- Penalize errors
- Weight for elegance/simplicity

### 3. EVOLVE Phase
Generate evolved model version.

### 4. VALIDATE Phase
Benchmark against test cases.

### 5. ACCEPT/REJECT
Keep if improvement > threshold (3%).

---

## Metrics

- **GSM-Plus**: +8.92% over original model
- **GSM8K**: +0.84% (near ceiling)
- **MATH**: +4.11%
- **ARC-Challenge**: +8.88% for larger models
- **Sycophancy**: Reduced from 0.28 to 0.13

---

## Auto-Activation Triggers

### Keywords
- "debate"
- "multi-agent"
- "RCR"
- "reflect critique refine"
- "consensus"
- "multiple perspectives"

### Intent Patterns
- Complex reasoning requiring verification
- Tasks prone to hallucination
- Decisions needing diverse viewpoints
- Error-prone calculations
- Code review/debugging

### Problem Types
- Mathematical reasoning
- Scientific analysis
- Code generation/review
- Adversarial robustness
- Complex decision-making

---

## Quality Gates

- Minimum 3 agents participating
- RCR applied in each round
- Explicit critique of peers
- Novel steps when changing answers
- Clear consensus or majority vote
- Traceable reasoning through rounds

---

## Advantages

- 5-9% accuracy gains on benchmarks
- Reduces biases and hallucinations
- Self-corrects through critique
- Scalable for complex tasks
- Transferable to single models via DTE

## Limitations

- Computationally expensive (multiple rounds)
- Performance varies with prompt tuning
- Risk of error propagation if agent "poisoned"
- Less effective for simple tasks

---

## Comparison to PanelGPT

| Aspect | PanelGPT | MAD |
|--------|----------|-----|
| Rounds | Often single | Multiple iterative |
| Training | None | Optional DTE/GRPO |
| Complexity | Simpler | More sophisticated |
| Use Case | Quick consensus | Robust reasoning |

---

## Integration Notes

### With DTE
MAD is the debate engine for DTE self-evolution.

### With GRPO
Debate traces train policy via group relative advantages.

### With ToT
Use MAD for multi-agent exploration of tree branches.

### With Action Verb Analysis
Decompose problem first, then debate each verb's solution.

### With Glicko-2
Rate agents based on debate performance for selection.
