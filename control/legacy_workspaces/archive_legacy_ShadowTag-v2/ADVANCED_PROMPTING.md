# Advanced Prompting Techniques

## Overview
This document covers advanced prompt engineering techniques that extend beyond basic frameworks (RTF, TAG, BAB, CARE, RISE). These methods leverage sophisticated reasoning strategies, multi-agent collaboration, and self-evolution mechanisms to enhance LLM performance on complex tasks.

**Related Documents:**
- [PROMPT_FRAMEWORKS.md](PROMPT_FRAMEWORKS.md) - Basic prompt engineering frameworks
- [MULTI_AGENT_SYSTEMS.md](MULTI_AGENT_SYSTEMS.md) - Multi-agent collaboration patterns
- [CODE_BENCHMARKS.md](CODE_BENCHMARKS.md) - Evaluation benchmarks
- [EVALUATION_METRICS.md](EVALUATION_METRICS.md) - Rating and scoring systems

---

## Table of Contents
1. [Chain-of-Thought (CoT) Prompting](#chain-of-thought-cot-prompting)
2. [Tree of Thoughts (ToT) Prompting](#tree-of-thoughts-tot-prompting)
3. [PanelGPT Prompting](#panelgpt-prompting)
4. [Multi-Agent Debate (MAD)](#multi-agent-debate-mad)
5. [DTE Framework](#dte-framework-debate-train-evolve)
6. [REFLECT-CRITIQUE-REFINE (RCR)](#reflect-critique-refine-rcr)
7. [Comparison Matrix](#comparison-matrix)

---

## Chain-of-Thought (CoT) Prompting

### Overview
Chain-of-Thought (CoT) prompting enhances LLM reasoning by encouraging step-by-step breakdowns of complex problems. Introduced around 2022, it's particularly effective for logic, math, and multi-step decision-making tasks.

### Key Characteristics
- **Purpose**: Improves reasoning transparency and accuracy
- **Method**: Append phrases like "Let's think step by step" or provide few-shot examples
- **Best For**: Analytical tasks, mathematical problems, logical deductions

### Example

```
Question: If a train travels 120 miles in 2 hours, what is its average speed?

CoT Prompt:
Let's think step by step:
1. We need to find average speed
2. The formula is: Speed = Distance / Time
3. Distance = 120 miles
4. Time = 2 hours
5. Speed = 120 / 2 = 60 miles per hour

Answer: 60 miles per hour
```

### Pros and Cons

**Pros:**
- Improves accuracy in complex scenarios
- Transparent, interpretable outputs
- Easy to integrate with other techniques
- Research-backed effectiveness

**Cons:**
- Can produce verbose responses
- Less effective for simple or creative tasks
- May introduce unnecessary steps for straightforward problems

---

## Tree of Thoughts (ToT) Prompting

### Overview
Tree of Thoughts (ToT), introduced in 2023 by researchers from Princeton University and Google DeepMind, extends CoT by structuring reasoning as a tree-like exploration. It allows models to generate multiple reasoning paths, evaluate them, and backtrack when needed.

### How It Works

1. **Thought Decomposition**: Break problems into manageable steps
2. **Thought Generation**: Generate multiple potential solutions per step
3. **State Evaluation**: Assess viability using:
   - **Value-Based**: Rate each state (sure/likely/impossible)
   - **Vote-Based**: Compare and vote on best options
4. **Search Navigation**: Use BFS or DFS to explore promising paths

### Key Components

| Component | Description | Role |
|-----------|-------------|------|
| **Thoughts** | Partial solutions or reasoning steps | Form tree nodes for branching |
| **Tree Structure** | Hierarchical organization | Enables exploration and backtracking |
| **Self-Evaluation** | LLM assesses its own thoughts | Prunes weak paths |
| **Search Algorithms** | BFS, DFS, or beam search | Navigates tree efficiently |

### Example: Game of 24

```
Problem: Use 4, 9, 10, 13 to make 24

ToT Propose Prompt:
Input: 4 9 10 13
Possible next steps:
13 - 10 = 3 (left: 3 4 9)
9 - 4 = 5 (left: 5 10 13)
4 * 9 = 36 (left: 10 13 36)
...

ToT Value Prompt:
Evaluate if given numbers can reach 24 (sure/likely/impossible)
3 4 9
9 - 3 = 6 (left: 4 6)
4 * 6 = 24
sure

Final Solution:
4 * (9 - (13 - 10)) = 24
```

### Performance
- **Game of 24**: ~74% success with GPT-4 vs. ~4% for basic prompting
- **Mini-Crosswords**: ~20% solve rate vs. <5% for CoT
- **Creative Writing**: 7.56/10 coherence vs. 6.93 for CoT

### Pros and Cons

**Pros:**
- Excels at complex, non-linear problems
- Enables self-correction through backtracking
- Outperforms CoT on puzzles and planning tasks
- No model fine-tuning required

**Cons:**
- Computationally intensive (multiple LLM calls)
- Requires clear evaluation criteria
- Generic search may need customization
- Best for specific problem types (puzzles, planning)

---

## PanelGPT Prompting

### Overview
PanelGPT (2023-2024) simulates a panel discussion among multiple expert personas to enhance reasoning through debate and consensus-building. It emphasizes social dynamics over algorithmic search.

### Structure

```
Core Prompt Template:
"3 experts are discussing the question with a panel discussion,
trying to solve it step by step, and make sure the result is
correct and avoid penalty."
```

### Key Components

| Component | Description |
|-----------|-------------|
| **Expert Personas** | 3-5 simulated experts with distinct viewpoints |
| **Moderator** | Optional role to guide discussion |
| **Step-by-Step Iteration** | Incremental contributions with critiques |
| **Accuracy Clauses** | "Avoid penalty" motivates error checking |
| **Consensus Mechanism** | Final agreement among experts |

### Example: Code Documentation

```
Prompt:
You are a panel of three experts on code documentation - Alice, Bob, and Charles.
When given a diff containing code changes, determine required docstring updates.
Conduct a panel discussion, solving step by step and checking each other's work.

Process:
- Alice: Suggests docstring change
- Bob: Critiques as unnecessary
- Charles: Agrees with Bob
Result: JSON list of verified updates
```

### Performance Gains
- **GSM8K Math**: 89.9% vs. 85.4% (CoT) and 84.2% (ToT)
- **Code Documentation**: 20% error rate vs. 40% (CoT)
- **Interdisciplinary Tasks**: More balanced, comprehensive responses

### Pros and Cons

**Pros:**
- Reduces errors through peer critique
- Handles interdisciplinary topics well
- Zero-shot, cost-effective for simple setups
- Promotes transparent reasoning

**Cons:**
- Increases token usage and costs (2x in some cases)
- Sensitive to wording ("panel" vs. "discussion")
- Relies on LLM's role-playing quality
- Can hallucinate in specialized domains

---

## Multi-Agent Debate (MAD)

### Overview
Multi-Agent Debate (MAD, 2023-2024) extends PanelGPT with more formalized debate structures, often incorporating iterative rounds, voting mechanisms, and specialized agent roles. Used in frameworks like AutoGen.

### How It Works

1. **Agent Initialization**: Define 2-5 agents with roles/perspectives
2. **Debate Rounds**: Agents propose → critique → refine (3-5 rounds)
3. **Critique Mechanisms**: REFLECT-CRITIQUE-REFINE patterns
4. **Consensus/Evaluation**: Judge agent or group vote
5. **Output Synthesis**: Compile final answer

### Example Structure

```
Round 1:
Agent 1 (Optimist): Proposes solution A
Agent 2 (Skeptic): Critiques solution A
Agent 3 (Pragmatist): Suggests hybrid approach

Round 2:
Agents refine based on critiques...

Final:
Judge evaluates arguments and selects best solution
```

### Performance
- **Question-Answering**: Up to 84% accuracy on MATH dataset
- **Adversarial Robustness**: Reduces toxicity, improves safety
- **Code Generation**: 5-9% accuracy gains on benchmarks

### Comparison to Related Techniques

| Technique | Structure | Best For |
|-----------|-----------|----------|
| **CoT** | Linear steps | Basic logic/math |
| **ToT** | Branching tree | Puzzles/planning |
| **PanelGPT** | Persona discussion | Interdisciplinary Q&A |
| **MAD** | Iterative debate | Complex reasoning, adversarial defense |

---

## DTE Framework (Debate, Train, Evolve)

### Overview
DTE (2025) is a ground-truth-free self-evolution mechanism that combines multi-agent debate with reinforcement learning to autonomously improve LLM reasoning capabilities.

### Three-Phase Process

#### 1. DEBATE Phase
- Multi-agent debates generate diverse reasoning traces
- Uses RCR (Reflect-Critique-Refine) prompting
- Produces consensus answers and consolidated rationales

#### 2. TRAIN Phase
- Fine-tunes model using GRPO (Group Relative Policy Optimization)
- Trains on debate-generated data without external labels
- Uses LoRA for efficient parameter updates

#### 3. EVOLVE Phase
- Iteratively updates agent pool with evolved models
- Incorporates learned capabilities into future debates
- Continues until performance plateaus

### Mathematical Foundation

**Reward Function:**
```
r(q, y) = w_ans · 𝟙[y = y*] + w_fmt · f_format(y) + w_len · exp(-|y| / τ)
```

Where:
- `y*` = consensus answer from debate
- `f_format` = format adherence check
- Weights: w_ans=2.0, w_fmt=0.5, w_len=0.5

**GRPO Update:**
```
R'_A = R_A + K × (S_A - E_A)
```

### Performance Results

| Dataset | Average Gain | Best Example |
|---------|-------------|--------------|
| GSM-Plus | +8.92% | Qwen-1.5B: +13.92% |
| GSM8K | +0.84% | Llama-8B: +10.55% |
| MATH | +4.11% | Qwen-7B: +5.2% |
| ARC-Challenge | +3.67% | Llama-8B: +8.88% |

### Key Innovations
- No ground-truth labels required
- Self-improves through iterative evolution
- Reduces sycophancy (agents blindly following others)
- Strong cross-domain generalization

---

## REFLECT-CRITIQUE-REFINE (RCR)

### Overview
RCR is a structured prompting strategy within DTE that guides multi-agent debates to reduce errors, sycophancy, and verbosity bias.

### Three-Step Process

#### 1. REFLECT
Agent self-assesses prior reasoning for errors

```
Prompt Element:
"Carefully analyze your previous solution, identifying any errors
in reasoning, calculations, or assumptions."
```

#### 2. CRITIQUE
Evaluate exactly two peer responses, highlighting flaws

```
Prompt Element:
"Review the solutions from other agents. Point out any:
- Calculation errors
- Flawed assumptions
- Logical inconsistencies
- Missed edge cases"
```

#### 3. REFINE
Update response, adding novel steps if answer changes

```
Prompt Element:
"Provide your revised solution:
• If correct: Explain why and defend with examples
• If erroneous: Explain the error and provide corrected solution
• If adopting peer's answer: Explain why their reasoning is superior"
```

### Domain-Specific Variants

#### Math Reasoning
```
You are Agent {agent_id} in a multi-agent debate to solve:
Problem: {question}
{own_previous}
Here are solutions from other agents: {context}

This is round {round_num}. Analyze all solutions—including your own—
identify any calculation errors, and provide your revised solution.

• If previous answer correct: Explain why and defend it
• If error found: Explain the error and provide corrected solution
• If another agent correct: Explain why you agree

Final answer must be in format \boxed{{answer}}
```

#### Science Reasoning
```
Identify any misconceptions or flawed scientific reasoning...
• Explain the scientific principles supporting your answer
• Explain the scientific misconception if erroneous
• Explain why their scientific reasoning is sound if agreeing
```

#### Commonsense Reasoning
```
Identify any flawed assumptions or logical inconsistencies...
• Explain logical reasoning and real-world knowledge
• Explain flawed assumption or inconsistency
• Explain alignment with commonsense knowledge
```

#### Code Review (Adapted)
```
Identify any bugs, inefficiencies, logical errors, or missed edge cases...
• Defend with execution examples if correct
• Explain bug/inefficiency and provide corrected code
• Explain better approach (complexity, readability) if adopting
```

### Performance Impact
- **Sycophancy Reduction**: 0.28 → 0.13 (halved on GSM-Plus)
- **Verbosity Gap**: Reduced by 43%
- **Accuracy Gains**: +0.7 to +3.7 points across benchmarks
- **State Transitions**: Incorrect→Correct probability 0.12 → 0.20

---

## Comparison Matrix

### When to Use Each Technique

| Technique | Complexity | Cost | Best Use Cases | Key Advantage |
|-----------|-----------|------|----------------|---------------|
| **CoT** | Low | Low | Basic math, simple logic | Transparency, ease of use |
| **ToT** | High | High | Puzzles, planning, games | Exploration, backtracking |
| **PanelGPT** | Medium | Medium | Interdisciplinary questions | Diverse perspectives |
| **MAD** | High | High | Complex reasoning, adversarial tasks | Debate-driven accuracy |
| **DTE+RCR** | Very High | Very High | Self-evolution, benchmark improvement | Ground-truth-free learning |

### Combination Strategies

**CoT + ToT:**
```
Use CoT for individual thought generation within ToT tree nodes
Example: Each ToT branch uses "let's think step by step" internally
```

**RISE + PanelGPT:**
```
RISE framework for task structure, PanelGPT for execution:

Role: Three expert content strategists
Input: Audience insights and industry data
Steps: Panel discusses step-by-step strategy (with debate)
Expectation: 40% visitor increase, thought leadership position
```

**RCR + AgentCoder:**
```
Integrate RCR into code agent workflows:
- Reflect: Agent reviews own code for bugs
- Critique: Reviews peer agents' code quality
- Refine: Updates with optimizations and fixes
```

---

## Implementation Guidelines

### 1. Start Simple, Scale Up
Begin with CoT, then progress to ToT/PanelGPT as needed. Reserve DTE for specialized applications requiring self-evolution.

### 2. Match Technique to Task

```python
def select_prompting_technique(task_type, complexity, resources):
    if complexity == "low":
        return "CoT"
    elif task_type == "puzzle" and resources == "high":
        return "ToT"
    elif task_type == "interdisciplinary":
        return "PanelGPT"
    elif task_type == "code" and resources == "high":
        return "MAD + RCR"
    elif requires_self_evolution:
        return "DTE"
```

### 3. Claude Agent SDK Integration

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// CoT Example
const cotResult = await query({
  prompt: "Solve this problem step by step: [problem]",
  options: {
    systemPrompt: { type: "preset", preset: "claude_code" }
  }
});

// PanelGPT Example
const panelPrompt = `
Three experts (Alice: optimist, Bob: skeptic, Charles: pragmatist)
are debating this question through panel discussion.
Each contributes one step at a time, critiques others, and refines.

Question: ${question}
`;

const panelResult = await query({
  prompt: panelPrompt,
  options: {
    systemPrompt: { type: "preset", preset: "claude_code" }
  }
});
```

### 4. Error Handling and Validation

```python
# For ToT/MAD implementations
def validate_thought_quality(thought, criteria):
    """Evaluate thought before adding to tree/debate"""
    return {
        "clarity": check_clarity(thought),
        "correctness": verify_logic(thought),
        "novelty": assess_uniqueness(thought)
    }

# Consensus threshold for debates
def check_consensus(agent_responses, threshold=0.75):
    """Require 75% agreement before terminating debate"""
    most_common = mode(agent_responses)
    agreement_rate = count(most_common) / len(agent_responses)
    return agreement_rate >= threshold
```

---

## Future Directions

### Emerging Trends (2025)
1. **Hybrid Systems**: Combining ToT search with MAD debate
2. **Tool Integration**: Connecting debates to code executors, databases
3. **Graph-of-Thoughts (GoT)**: Generalizing ToT to arbitrary graphs
4. **Multi-Modal Debates**: Incorporating images, code, data visualizations
5. **Efficient DTE**: Reducing computational costs through distillation

### Research Areas
- Optimal agent pool diversity in MAD
- Adaptive K-factors for different task types
- Cross-lingual debate effectiveness
- Integration with retrieval-augmented generation (RAG)

---

## Resources

### Academic Papers
- **CoT**: "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (2022)
- **ToT**: "Tree of Thoughts: Deliberate Problem Solving with Large Language Models" (2023)
- **DTE**: "Debate, Train, Evolve: Self-Evolution of Language Model Reasoning" (2025)
- **MAD**: Various papers on multi-agent systems and AutoGen framework

### Implementation Repositories
- **ToT**: [princeton-nlp/tree-of-thought-llm](https://github.com/princeton-nlp/tree-of-thought-llm)
- **AutoGen**: [microsoft/autogen](https://github.com/microsoft/autogen)
- **AgentCoder**: Search for official AgentCoder repository

### Related Documentation
- [MULTI_AGENT_SYSTEMS.md](MULTI_AGENT_SYSTEMS.md) - Implementation patterns
- [CODE_BENCHMARKS.md](CODE_BENCHMARKS.md) - Evaluation methods
- [COMPREHENSIVE_GUIDE.md](COMPREHENSIVE_GUIDE.md) - Integrated framework guide

---

## Version History

- **v1.0** (2025-11-08): Initial comprehensive documentation
  - Added CoT, ToT, PanelGPT, MAD, DTE, RCR
  - Included comparison matrices and implementation guidelines
  - Integrated with Claude Agent SDK examples

---

## Contributing

When updating this document:
1. Maintain academic rigor with proper citations
2. Include working code examples
3. Update performance metrics with latest research
4. Cross-reference related documentation
5. Test prompts before adding examples
