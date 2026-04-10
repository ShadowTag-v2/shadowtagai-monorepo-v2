# Code Generation Benchmarks

## Overview

This document provides comprehensive coverage of the major benchmarks used to evaluate large language models (LLMs) on code generation, debugging, and software engineering tasks. These benchmarks are critical for assessing AI capabilities in practical programming scenarios.

**Related Documents:**

- [EVALUATION_METRICS.md](EVALUATION_METRICS.md) - Scoring systems (Elo, Pass@k)
- [ADVANCED_PROMPTING.md](ADVANCED_PROMPTING.md) - Prompting techniques
- [MULTI_AGENT_SYSTEMS.md](MULTI_AGENT_SYSTEMS.md) - Agent-based code generation

---

## Table of Contents

1. [HumanEval](#humaneval)
2. [BigCodeBench](#bigcodebench)
3. [SWE-bench](#swe-bench)
4. [Benchmark Comparison](#benchmark-comparison)
5. [Best Practices](#best-practices)

---

## HumanEval

### Overview

**HumanEval** is a foundational benchmark for evaluating code generation capabilities, introduced by OpenAI in 2021. It consists of 164 hand-crafted Python programming problems designed to test functional correctness without relying on simple pattern matching.

### Key Characteristics

| Property          | Details                                   |
| ----------------- | ----------------------------------------- |
| **Release Date**  | 2021 (OpenAI)                             |
| **Tasks**         | 164 hand-crafted problems                 |
| **Language**      | Python exclusively                        |
| **Test Coverage** | Average of 7.7 unit tests per problem     |
| **Focus**         | Algorithms, data structures, computations |
| **Evaluation**    | Functional correctness via unit tests     |

### How It Works

1. **Input Format**: Function signature + docstring

   ```python
   from typing import List
   def has_close_elements(numbers: List[float], threshold: float) -> bool:
       """
       Check if in given list of numbers, are any two numbers closer
       to each other than given threshold.
       >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
       False
       >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
       True
       """
   ```

2. **Model Task**: Generate complete function body

3. **Evaluation**: Pass@k metric
   - Generate k solutions
   - Success if ≥1 solution passes all tests
   - Common values: k=1, 10, 100

### Evaluation Metrics

**Pass@k Formula:**

```
Pass@k = E_Problems[1 - (C(n-c, k) / C(n, k))]

Where:
- n = total samples generated
- c = correct samples
- k = samples considered
- C(n,k) = binomial coefficient
```

**Typical Results (2025):**

- GPT-4 variants: ~85-90% Pass@1
- Claude 3.7 Sonnet: ~85% Pass@1
- Smaller open-source models: 40-70% Pass@1

### Variants and Extensions

#### HumanEval-X

- **Languages**: Python, JavaScript, Go, Java, C++
- **Tasks**: Code generation + translation
- **Size**: Smaller multilingual variant

#### HumanEval-XL

- **Scale**: 22,080 prompts
- **Languages**: 23 natural languages × 12 programming languages
- **Use Case**: Comprehensive multilingual evaluation

### Limitations

1. **Small Size**: Only 164 problems; risk of saturation
2. **Python-Only**: Original doesn't test cross-language abilities
3. **Simplicity**: Problems considered easier than real-world tasks
4. **Data Contamination**: Risk of test set leakage in training

### Implementation

```bash
# Install evaluation harness
pip install human-eval

# Run evaluation
evaluate_functional_correctness sample_solutions.jsonl

# Output format
{
  "task_id": "HumanEval/0",
  "completion": "    for i in range(len(numbers)):\n...",
  "pass": true
}
```

### Resources

- **GitHub**: [openai/human-eval](https://github.com/openai/human-eval)
- **Hugging Face**: Dataset available for easy integration
- **Leaderboards**: Various AI research sites track HumanEval scores

---

## BigCodeBench

### Overview

**BigCodeBench** (June 2024) is designed as the "next generation of HumanEval," addressing saturation issues with more challenging, practical programming tasks. Developed by the BigCode project, it emphasizes diverse real-world library usage.

### Key Characteristics

| Property         | Details                                        |
| ---------------- | ---------------------------------------------- |
| **Release Date** | June 2024 (BigCode project)                    |
| **Tasks**        | 1,140 programming problems                     |
| **Libraries**    | 139 libraries across 7 domains                 |
| **Languages**    | Primarily Python (with library focus)          |
| **Variants**     | Complete (code completion), Instruct (NL→code) |
| **Focus**        | Practical API usage, complex instructions      |

### Task Diversity

**Seven Domains:**

1. Data Processing
2. Machine Learning
3. Web Development
4. Scientific Computing
5. Visualization
6. Database Operations
7. System Administration

**Library Examples:**

- pandas, numpy, scikit-learn
- requests, flask, django
- matplotlib, plotly
- sqlalchemy, pymongo

### Evaluation Variants

#### BigCodeBench-Complete

**Format**: Code completion from partial implementations

```python
# Given:
import pandas as pd
import numpy as np

def analyze_sales_data(df: pd.DataFrame) -> dict:
    """
    Analyze sales data and return summary statistics.
    Include: total revenue, average order value, top products.
    """
    # Model must complete implementation

# Expected: Full function using pandas operations
```

#### BigCodeBench-Instruct

**Format**: Natural language instructions → full code

```
Instruction:
Create a function that loads a CSV file of sales data,
filters for orders above $100, groups by product category,
and generates a bar chart of revenue by category.

# Model generates complete solution from scratch
```

### Evaluation Metrics

**Calibrated Pass@1:**

- Uses greedy decoding for fairness
- Binary: passes all tests or fails
- More challenging than HumanEval (lower scores)

**Typical Results (2025):**

| Model            | Complete | Instruct |
| ---------------- | -------- | -------- |
| GPT-4o           | 61.1%    | 51.1%    |
| Claude 3.7       | ~58%     | ~48%     |
| Gemini 2.0 Flash | ~55%     | ~45%     |
| Open-source (7B) | ~30-40%  | ~25-35%  |

### BigCodeBench-Hard

- **Subset**: ~150 most challenging tasks
- **Purpose**: User-facing, difficult problems
- **Scores**: Typically 10-20% lower than full set

### Elo Ratings

BigCodeBench also uses Elo ratings for finer-grained model comparison:

- Computed only for Complete variant
- Treats task success/failure as "wins/losses"
- Provides relative ranking beyond absolute Pass@1
- See [EVALUATION_METRICS.md](EVALUATION_METRICS.md) for details

### Common Issues Observed

**GPT-4o "Laziness":**

```python
# Issue: Missing imports in long prompts
def process_data(file_path):
    df = pd.read_csv(file_path)  # pd not imported!
    # Model skipped: import pandas as pd
```

**Solution**: Explicit instruction to include all imports

### Implementation

```bash
# Install BigCodeBench
pip install bigcodebench

# Run evaluation
bigcodebench.evaluate \
    --model gpt-4 \
    --split complete \
    --output results.json

# View leaderboard
# Visit: https://bigcode-bench.github.io/
```

### Resources

- **Website**: [bigcode-bench.github.io](https://bigcode-bench.github.io/)
- **GitHub**: BigCode project repository
- **Leaderboard**: Real-time rankings with 163+ models
- **Hugging Face Space**: Interactive leaderboard

---

## SWE-bench

### Overview

**SWE-bench** (October 2023) evaluates AI on real-world software engineering tasks derived from actual GitHub issues and pull requests. It's the gold standard for assessing AI agents in production-like development environments.

### Key Characteristics

| Property         | Details                                     |
| ---------------- | ------------------------------------------- |
| **Release Date** | October 2023 (arXiv paper)                  |
| **Source**       | Real GitHub issues/PRs                      |
| **Task Type**    | Bug fixes, features, maintenance            |
| **Languages**    | Python-focused (with multilingual variants) |
| **Evaluation**   | Patch must pass repository tests            |
| **Environment**  | Dockerized, sandboxed execution             |

### How It Works

**Workflow:**

1. **Input**: GitHub issue description + repository state (pre-issue commit)
2. **AI Task**: Generate code patch to resolve issue
3. **Validation**: Apply patch and run test suite in Docker
4. **Success Metric**: % Resolved (tests pass)

**Example Task:**

```
Repository: django/django
Issue #12345: "QuerySet.filter() fails with Q objects on M2M relations"

Given:
- Issue description
- Repository at specific commit
- Failing test cases

Required Output:
- Code patch that fixes the issue
- All tests pass after applying patch
```

### Dataset Variants

#### Comprehensive Comparison

| Variant          | Tasks  | Description                      | Focus                    | Release  |
| ---------------- | ------ | -------------------------------- | ------------------------ | -------- |
| **Full**         | 2,294  | Original dataset, diverse repos  | Comprehensive evaluation | Oct 2023 |
| **Lite**         | 300    | Curated subset                   | Cost-effective testing   | 2024     |
| **Verified**     | 500    | Human-validated (+ OpenAI)       | Quality, reliability     | Aug 2024 |
| **Bash Only**    | 500    | Verified + mini-SWE-agent        | CLI interactions         | 2024     |
| **Multimodal**   | 517    | Includes visual bug reports      | Multimodal AI            | Oct 2024 |
| **Multilingual** | 300    | 42 repos, 9 languages            | Non-Python code          | 2024     |
| **Pro**          | 1,865  | Long-horizon, professional repos | Complex, multi-step      | Sep 2025 |
| **PolyBench**    | Varies | Amazon's multilingual extension  | Global scenarios         | Apr 2025 |

#### SWE-bench Pro

**Breakdown:**

- **Public**: 1,865 tasks from 41 professional repositories
- **Verified**: 500 high-quality tasks
- **Private**: 300 proprietary code tasks
- **Difficulty**: Significantly harder (top models drop 20-30%)

### Performance Leaderboards (2025)

#### SWE-bench Verified

| Rank | Model             | % Resolved       |
| ---- | ----------------- | ---------------- |
| 1    | Gemini 2.5 Pro    | 53.60%           |
| 2    | Claude 3.7 Sonnet | 52.80%           |
| 3    | mini-SWE-agent    | ~50-65% (varies) |
| 4    | o4-mini           | 45.00%           |
| 5    | GPT-4 variants    | ~40-45%          |

#### SWE-bench Pro

- **GPT-5**: ~30-35% (significant drop)
- **Claude 4.1**: ~28-32%
- **Challenges**: Long-horizon, multi-file changes, complex dependencies

### Evaluation Environment

**Docker Setup:**

```dockerfile
# Each task runs in isolated container
FROM python:3.9
COPY repo /workspace
RUN pip install -r requirements.txt
COPY patch.diff /workspace
RUN cd /workspace && git apply patch.diff
RUN pytest tests/
```

**Success Criteria:**

- All existing tests still pass
- New tests (if any) pass
- No syntax or runtime errors
- Proper git patch format

### Common Challenges

1. **Multi-File Changes**: Requires understanding codebase structure
2. **Test Reproduction**: Must reproduce issue before fixing
3. **Edge Cases**: Real bugs often have subtle conditions
4. **Documentation**: Need to understand API contracts
5. **Version Compatibility**: Dependencies and Python versions

### SWE-agent

**Open-source tool** (2025) for tackling SWE-bench:

- State-of-the-art on Lite variant
- Uses agent-based approach with tools
- Bash-compatible environment
- Version 1.0 released March 2025

```bash
# SWE-agent usage
python run.py \
    --model_name gpt4 \
    --data_path swebench/test.json \
    --repo_path /path/to/repo \
    --output_dir results/
```

### Recent Developments

- **Sep 2025**: SWE-bench Pro (Scale AI)
- **Jul 2025**: mini-SWE-agent achieves 65% on Verified
- **May 2025**: SWE-smith paper (training agents)
- **Apr 2025**: SWE-PolyBench (multilingual)
- **Mar 2025**: SWE-agent 1.0 release
- **Oct 2024**: Multimodal variant
- **Aug 2024**: Verified subset with OpenAI

### Resources

- **Website**: [swebench.com](https://www.swebench.com/)
- **GitHub**: [princeton-nlp/SWE-bench](https://github.com/princeton-nlp/SWE-bench)
- **Leaderboard**: Multiple tracked at swebench.com
- **Docker Images**: Pre-configured test environments

---

## Benchmark Comparison

### Difficulty Progression

```
HumanEval        →  BigCodeBench       →  SWE-bench
(Algorithmic)       (Library Usage)       (Real Codebases)
    ↓                    ↓                      ↓
Single Function    Multi-library        Multi-file Patches
7 tests avg        Complex APIs         Full test suites
164 tasks          1,140 tasks          2,294+ tasks
~85% top score     ~60% top score       ~50% top score
```

### Use Case Matrix

| Benchmark        | Best For                   | Skill Level  | Time/Task | Cost   |
| ---------------- | -------------------------- | ------------ | --------- | ------ |
| **HumanEval**    | Algorithm fundamentals     | Intermediate | Low       | Low    |
| **BigCodeBench** | API usage, real-world libs | Advanced     | Medium    | Medium |
| **SWE-bench**    | Production code, debugging | Expert       | High      | High   |

### Metric Comparison

| Benchmark        | Primary Metric      | Secondary Metrics              |
| ---------------- | ------------------- | ------------------------------ |
| **HumanEval**    | Pass@k (k=1,10,100) | Syntax correctness             |
| **BigCodeBench** | Calibrated Pass@1   | Elo ratings (Complete)         |
| **SWE-bench**    | % Resolved          | Partial credit (some variants) |

### Coverage Comparison

```
┌─────────────────────────────────────────────────────┐
│                  Code Generation Skills             │
├─────────────┬─────────────┬──────────────┬──────────┤
│             │ HumanEval   │ BigCodeBench │ SWE-bench│
├─────────────┼─────────────┼──────────────┼──────────┤
│ Algorithms  │     ✓✓✓     │      ✓✓      │    ✓     │
│ Data Struct │     ✓✓✓     │      ✓✓      │    ✓     │
│ API Usage   │      ✓      │     ✓✓✓      │   ✓✓     │
│ Libraries   │      -      │     ✓✓✓      │   ✓✓✓    │
│ Multi-file  │      -      │      -       │   ✓✓✓    │
│ Debugging   │      ✓      │      ✓       │   ✓✓✓    │
│ Tests       │      ✓      │      ✓✓      │   ✓✓✓    │
│ Real Issues │      -      │      ✓       │   ✓✓✓    │
└─────────────┴─────────────┴──────────────┴──────────┘
```

---

## Best Practices

### 1. Choosing the Right Benchmark

```python
def select_benchmark(evaluation_goal, resources, skill_focus):
    if skill_focus == "fundamentals":
        return "HumanEval"
    elif skill_focus == "libraries" and resources == "medium":
        return "BigCodeBench"
    elif skill_focus == "production" and resources == "high":
        return "SWE-bench"
    elif skill_focus == "comprehensive":
        return ["HumanEval", "BigCodeBench", "SWE-bench"]
```

### 2. Avoiding Data Contamination

**Critical**: Ensure training data doesn't include test sets

```python
# Check for contamination
def check_contamination(model_training_data, benchmark_name):
    """
    Verify no test examples in training set
    Use temporal splits (pre-benchmark release)
    Hash-based detection for leaked examples
    """
    pass
```

**Guidelines:**

- Use temporal cutoffs (train before benchmark release)
- Implement n-gram overlap detection
- Monitor for suspiciously perfect scores
- Audit data sources regularly

### 3. Fair Evaluation Setup

**Standardize:**

- Temperature: 0.0 (greedy) for Pass@1
- Max tokens: Sufficient for complete solutions
- Timeout: Reasonable execution limits
- Environment: Docker for reproducibility

**Example Configuration:**

```json
{
  "model": "gpt-4",
  "temperature": 0.0,
  "max_tokens": 2048,
  "timeout_seconds": 300,
  "sandbox": "docker",
  "attempts": 1
}
```

### 4. Interpreting Results

**Single Benchmark:**

```
Pass@1: 85% on HumanEval
→ Strong at algorithmic tasks
→ May struggle with complex libraries
→ Test on BigCodeBench for full picture
```

**Comprehensive Evaluation:**

```
Model A: HumanEval 90%, BigCodeBench 45%, SWE-bench 25%
→ Great fundamentals, needs real-world experience

Model B: HumanEval 85%, BigCodeBench 60%, SWE-bench 50%
→ Better practical performance, production-ready
```

### 5. Prompting Strategies per Benchmark

#### HumanEval

```
Strategy: Clear, algorithmic thinking
Prompt: "Implement the function following these steps:
1. Understand the input/output specification
2. Consider edge cases
3. Write efficient, readable code
4. Test with provided examples"
```

#### BigCodeBench

```
Strategy: Library-aware, practical
Prompt: "Create a solution using appropriate libraries:
- Import necessary modules explicitly
- Use idiomatic API patterns
- Handle errors gracefully
- Follow Python best practices"
```

#### SWE-bench

```
Strategy: Codebase understanding, systematic debugging
Prompt: "Solve this GitHub issue:
1. Read the issue description carefully
2. Locate relevant files in the repository
3. Reproduce the bug with existing tests
4. Implement minimal fix
5. Verify all tests pass"
```

### 6. Continuous Monitoring

**Track over time:**

```python
benchmark_scores = {
    "2024-01": {"humaneval": 0.82, "bigcode": 0.51, "swe": 0.38},
    "2024-06": {"humaneval": 0.85, "bigcode": 0.58, "swe": 0.45},
    "2025-01": {"humaneval": 0.87, "bigcode": 0.61, "swe": 0.52}
}

# Identify improvement trends and saturation points
```

---

## Integration with Multi-Agent Systems

### AgentCoder + Benchmarks

```python
from agentcoder import ProgrammerAgent, TesterAgent, OptimizerAgent

# Evaluate on HumanEval
for task in humaneval_tasks:
    programmer = ProgrammerAgent()
    code = programmer.generate(task.prompt)

    tester = TesterAgent()
    tests = tester.create_tests(task)
    results = tester.execute(code, tests)

    if results.failed:
        optimizer = OptimizerAgent()
        code = optimizer.refine(code, results.errors)
```

### DTE Self-Evolution on Benchmarks

```python
# Train on BigCodeBench using DTE
dte_framework = DTE(
    base_model="qwen-7b",
    benchmark="bigcodebench",
    debate_rounds=3,
    evolution_rounds=2
)

evolved_model = dte_framework.evolve()
# Achieves +5-10% on BigCodeBench after evolution
```

---

## Future Directions

### Emerging Benchmarks (2025+)

1. **MultiLingual SWE-bench**: Beyond Python
2. **Interactive Debugging Benchmarks**: Conversational fixing
3. **Security-Focused Evaluations**: Vulnerability detection
4. **Performance Optimization Benchmarks**: Speed/memory tests
5. **Documentation Generation**: Code→docs quality

### Research Opportunities

- Cross-benchmark generalization studies
- Contamination detection methods
- Adaptive difficulty benchmarks
- Human-AI collaborative evaluation
- Domain-specific code generation (embedded, distributed systems)

---

## Resources

### Official Sites

- **HumanEval**: [github.com/openai/human-eval](https://github.com/openai/human-eval)
- **BigCodeBench**: [bigcode-bench.github.io](https://bigcode-bench.github.io/)
- **SWE-bench**: [swebench.com](https://www.swebench.com/)

### Leaderboards

- BigCode Leaderboard (Hugging Face)
- SWE-bench Official Rankings
- Papers with Code (aggregated results)

### Related Tools

- **Code Execution**: Judge0, Piston
- **Evaluation Frameworks**: EleutherAI lm-evaluation-harness
- **Agent Frameworks**: AutoGen, LangGraph

---

## Version History

- **v1.0** (2025-11-08): Initial comprehensive documentation
  - Covered HumanEval, BigCodeBench, SWE-bench
  - Added comparison matrices and best practices
  - Integrated with multi-agent systems

---

## See Also

- [EVALUATION_METRICS.md](EVALUATION_METRICS.md) - Pass@k, Elo, Glicko systems
- [MULTI_AGENT_SYSTEMS.md](MULTI_AGENT_SYSTEMS.md) - AgentCoder, collaborative coding
- [ADVANCED_PROMPTING.md](ADVANCED_PROMPTING.md) - Techniques for better performance
- [COMPREHENSIVE_GUIDE.md](COMPREHENSIVE_GUIDE.md) - Integrated framework guide
