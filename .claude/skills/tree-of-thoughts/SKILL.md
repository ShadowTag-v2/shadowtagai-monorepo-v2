# Tree of Thoughts (ToT) Skill

## Model
opus

## Purpose
Structure reasoning as tree-like exploration with branching, evaluation, and backtracking. Enables deliberate "System 2" thinking for complex tasks requiring planning, lookahead, or handling ambiguity.

## Enforcement
- Level: suggest
- Priority: critical

---

## Core Mechanism

### Thought Decomposition
Break problem into smaller steps where each step = a node in the tree.

### Thought Generation
For each step, generate multiple potential "thoughts" or ideas:
- **Independent sampling**: Diverse options
- **Sequential proposal**: Next logical step

### State Evaluation
Assess viability of each thought:
- **Value-based**: Rate as "sure," "likely," or "impossible"
- **Vote-based**: Compare thoughts and vote on best

### Search and Navigation
- **BFS**: Level-by-level exploration
- **DFS**: Deep dive with backtracking
- **Beam Search**: Keep top-k candidates

---

## Implementation Templates

### Propose Prompt (Generation)
```
Input: [CURRENT STATE]
Possible next steps:
1. [Option A] → [Result]
2. [Option B] → [Result]
3. [Option C] → [Result]
```

### Value Prompt (Evaluation)
```
Evaluate if this state can reach the goal (sure/likely/impossible):

State: [CURRENT STATE]
Analysis: [REASONING]
Rating: [sure/likely/impossible]
```

### Synthesis Prompt
```
Problem: [PROBLEM]
Exploration Path: [STEPS TAKEN]
Final Answer: [SOLUTION]
```

---

## Expert Debate Pattern (Simplified ToT)

```
Imagine three different experts are answering this question.
All experts will write down 1 step of their thinking, then share with the group.
Then all experts go to the next step, etc.
If any expert realizes they're wrong at any point, they leave.

Question: [PROBLEM]

Expert 1 (Step 1): [THOUGHT]
Expert 2 (Step 1): [THOUGHT]
Expert 3 (Step 1): [THOUGHT]

[Continue until consensus or elimination]

Final Answer: [SOLUTION]
```

---

## Use Cases

### Game of 24 (Arithmetic Puzzle)
```
Input: 4 9 10 13
Goal: Use operations to reach 24

Branch 1: 13 - 10 = 3 (left: 3 4 9)
  → 9 - 3 = 6 (left: 4 6)
    → 4 * 6 = 24 ✓

Answer: 4 * (9 - (13 - 10)) = 24
```

### Architecture Decision
```
Problem: Choose database for high-write workload

Branch 1: PostgreSQL
  Evaluation: Mature, ACID, but write-heavy may bottleneck
  Rating: likely

Branch 2: Cassandra
  Evaluation: Distributed writes, eventual consistency acceptable
  Rating: sure

Branch 3: MongoDB
  Evaluation: Flexible schema, but consistency concerns
  Rating: likely

Selected: Cassandra (highest confidence for use case)
```

### Creative Writing
```
Task: Generate coherent passage from random sentences

Branch exploration for each sentence placement
Vote on best arrangement
Refine for coherence

Result: Coherence score 7.56/10 (vs 6.93 for linear CoT)
```

---

## Auto-Activation Triggers

### Keywords
- "explore options"
- "consider alternatives"
- "branch"
- "evaluate paths"
- "tree of thoughts"
- "multiple approaches"

### Intent Patterns
- Complex planning with uncertainty
- Puzzles requiring exploration
- Architecture decisions with tradeoffs
- Creative tasks with multiple valid outcomes

### Problem Types
- Optimization problems
- Game-like scenarios
- Multi-step planning
- Design decisions

---

## Quality Gates

- Minimum 3 branches explored per decision point
- Each branch evaluated with explicit rating
- Pruning justified with reasoning
- Final selection explained

---

## Metrics

- **Game of 24**: ~74% success with GPT-4 (vs ~4% baseline)
- **Crosswords**: ~20% solve rate (far exceeds CoT)
- **Creative Writing**: 7.56/10 coherence (vs 6.93 CoT)

---

## Advantages

- Excels in complex, non-linear tasks
- Enables exploration and self-correction
- No model fine-tuning needed
- Outperforms CoT on benchmarks by 60%+

## Limitations

- Computationally intensive (multiple LLM calls)
- Best for tasks with clear evaluation criteria
- May not adapt well without customization

---

## Integration Notes

- **With CoT**: Use CoT within each tree branch
- **With RCR**: Apply RCR to refine selected branches
- **With MAD**: Use ToT for individual agent exploration
- **Extends to GoT**: Generalize to arbitrary graphs with loops
