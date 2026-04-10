# Evaluation Metrics for AI Systems

## Overview

This document covers the mathematical foundations and practical applications of evaluation metrics used to assess AI model performance, particularly for code generation and reasoning tasks. Understanding these metrics is essential for fair model comparison and benchmark interpretation.

**Related Documents:**

- [CODE_BENCHMARKS.md](CODE_BENCHMARKS.md) - Benchmark datasets
- [ADVANCED_PROMPTING.md](ADVANCED_PROMPTING.md) - Techniques that improve these metrics
- [MULTI_AGENT_SYSTEMS.md](MULTI_AGENT_SYSTEMS.md) - Systems evaluated using these metrics

---

## Table of Contents

1. [Pass@k Metrics](#passk-metrics)
2. [Elo Rating System](#elo-rating-system)
3. [Glicko Rating System](#glicko-rating-system)
4. [Metric Comparison](#metric-comparison)
5. [Implementation Guide](#implementation-guide)

---

## Pass@k Metrics

### Overview

**Pass@k** measures the probability that at least one correct solution appears in k generated samples. It's the primary metric for code generation benchmarks like HumanEval and BigCodeBench.

### Mathematical Definition

**Formula:**

```
Pass@k = E_Problems[1 - (C(n-c, k) / C(n, k))]

Where:
- n = total number of samples generated
- c = number of correct samples
- k = number of samples to consider
- C(n,k) = binomial coefficient = n! / (k!(n-k)!)
- E_Problems = expected value across all problems
```

**Intuition:**

- If you generate n=100 solutions and c=20 are correct
- Pass@10 = probability that at least 1 of 10 random picks is correct
- Higher k gives the model more chances, increasing Pass@k

### Common Variants

#### Pass@1 (Calibrated)

```
Special case: k=1, measured with greedy decoding
Pass@1 = (correct solutions / total problems) × 100%

Example:
- 164 HumanEval problems
- 140 solved correctly
- Pass@1 = 140/164 = 85.4%
```

#### Pass@10

```
Generate 10 solutions per problem (often with temperature > 0)
Pass@10 = probability at least 1 of 10 is correct

If c=2 correct out of n=10 samples:
Pass@10 = 1 - C(8,10) / C(10,10)
        = 1 - C(8,10) / 1
        = 1 - 45/1
```

#### Pass@100

```
Generate 100 diverse solutions
Pass@100 measures "potential" if we could cherry-pick
Higher than Pass@1 or Pass@10
Used to assess model's capability ceiling
```

### Practical Calculation

**Python Implementation:**

```python
import numpy as np
from scipy.special import comb

def calculate_pass_at_k(n, c, k):
    """
    Calculate Pass@k metric

    Args:
        n: Total samples generated
        c: Number of correct samples
        k: Samples to consider

    Returns:
        Pass@k probability
    """
    if n - c < k:
        return 1.0
    return 1.0 - (comb(n - c, k) / comb(n, k))

# Example: 20 correct out of 100 samples
pass_at_1 = calculate_pass_at_k(100, 20, 1)    # ~0.20
pass_at_10 = calculate_pass_at_k(100, 20, 10)  # ~0.89
pass_at_100 = calculate_pass_at_k(100, 20, 100) # 1.00

print(f"Pass@1:   {pass_at_1:.2%}")
print(f"Pass@10:  {pass_at_10:.2%}")
print(f"Pass@100: {pass_at_100:.2%}")
```

### Evaluation Configurations

#### Greedy Decoding (Pass@1)

```json
{
  "temperature": 0.0,
  "top_p": 1.0,
  "samples": 1,
  "use_case": "Calibrated, deterministic evaluation"
}
```

#### Sampling (Pass@10, Pass@100)

```json
{
  "temperature": 0.8,
  "top_p": 0.95,
  "samples": 10, // or 100
  "use_case": "Diversity-driven evaluation"
}
```

### Interpretation Guidelines

| Pass@k       | Interpretation                | Use Case                              |
| ------------ | ----------------------------- | ------------------------------------- |
| **Pass@1**   | Single-shot success rate      | Production readiness, cost estimation |
| **Pass@10**  | Success with moderate retries | Interactive coding assistants         |
| **Pass@100** | Theoretical ceiling           | Research, capability assessment       |

**Example Analysis:**

```
Model A: Pass@1=60%, Pass@10=85%, Pass@100=95%
→ Good baseline, benefits from sampling
→ Suitable for tools with retry mechanisms

Model B: Pass@1=80%, Pass@10=82%, Pass@100=85%
→ Consistent, less diversity
→ Better for single-generation scenarios
```

### Limitations

1. **Cost**: Pass@100 requires 100× more compute than Pass@1
2. **Practicality**: Real users typically see Pass@1 or Pass@3
3. **Diversity Assumption**: Assumes independent samples (not always true)
4. **Ranking Sensitivity**: Small differences may not be significant

---

## Elo Rating System

### Overview

The **Elo rating system**, developed by Arpad Elo in the 1950s-1960s for chess, provides relative rankings based on pairwise competition outcomes. Adapted for AI evaluation, it offers finer-grained model comparison than absolute metrics.

### Mathematical Foundation

#### Expected Score (Win Probability)

**Formula:**

```
E_A = 1 / (1 + 10^((R_B - R_A) / 400))

Where:
- E_A = expected score for player A (probability of winning)
- R_A = rating of player A
- R_B = rating of player B
- 400 = scaling constant (empirically derived)
```

**Rating Difference → Win Probability:**

```
Δ Rating  |  Higher's Win%  |  Odds Ratio
----------|-----------------|-------------
    0     |      50%        |    1:1
  100     |      64%        |    1.8:1
  200     |      76%        |    3.2:1
  400     |      91%        |   10:1
  600     |      97%        |   32:1
  800     |      99%        |  100:1
```

#### Rating Update Rule

**Formula:**

```
R'_A = R_A + K × (S_A - E_A)

Where:
- R'_A = new rating for player A
- R_A = current rating
- K = K-factor (adjustment magnitude, typically 16-32)
- S_A = actual score (1=win, 0.5=draw, 0=loss)
- E_A = expected score (calculated above)
```

**Example Calculation:**

```
Player A: R_A = 1500
Player B: R_B = 1700
K = 32

1. Calculate expected score for A:
   E_A = 1 / (1 + 10^((1700-1500)/400))
       = 1 / (1 + 10^0.5)
       = 1 / (1 + 3.162)
       = 0.24 (24% chance to win)

2. A wins (surprise!), so S_A = 1:
   R'_A = 1500 + 32 × (1 - 0.24)
        = 1500 + 32 × 0.76
        = 1500 + 24.3
        = 1524

3. B's rating decreases by same amount:
   R'_B = 1700 - 24.3 = 1676
```

### Derivation from First Principles

#### Step 1: Bradley-Terry Model

Assumes win probability proportional to strength ratio:

```
P(A beats B) = s_A / (s_A + s_B)

Where s is strength parameter
```

#### Step 2: Logistic Transformation

Convert to ratings using logarithms:

```
s_A = 10^(R_A / 400)
s_B = 10^(R_B / 400)

Therefore:
P(A > B) = 10^(R_A/400) / (10^(R_A/400) + 10^(R_B/400))
         = 1 / (1 + 10^((R_B - R_A)/400))
```

#### Step 3: Why 400?

Chosen so 400-point difference = 10× strength = ~91% win rate

#### Step 4: Update Rule Derivation

Approximates maximum likelihood estimation:

- Minimize prediction error
- Weight by K-factor for convergence speed
- Zero-sum (ratings conserved in pairwise matches)

### K-Factor Selection

| Player Type      | K Value | Purpose                       |
| ---------------- | ------- | ----------------------------- |
| **Beginners**    | 40-50   | Fast adaptation to true skill |
| **Intermediate** | 32      | Standard adjustment           |
| **Experts**      | 16-20   | Stability, resist volatility  |
| **Established**  | 10      | Minimal change                |

**AI Evaluation:** Typically use K=32 for model rankings

### Elo in Code Benchmarks

#### BigCodeBench Application

**Process:**

1. Treat each task as a "game"
2. Models "compete" on each task:
   - Both pass → draw
   - One passes → that model "wins"
   - Both fail → draw (or exclude)
3. Update ratings after all tasks
4. Repeat with random sampling for robustness

**Pseudocode:**

```python
def compute_elo_ratings(models, tasks, K=32, init_rating=1000):
    ratings = {model: init_rating for model in models}

    for iteration in range(500):  # Multiple iterations
        shuffled_tasks = random.sample(tasks, len(tasks))

        for task in shuffled_tasks:
            for model_a in models:
                for model_b in models:
                    if model_a == model_b:
                        continue

                    # Determine outcome
                    pass_a = model_a.solve(task)
                    pass_b = model_b.solve(task)

                    if pass_a and not pass_b:
                        score_a = 1.0
                    elif not pass_a and pass_b:
                        score_a = 0.0
                    else:
                        continue  # Skip draws

                    # Calculate expected
                    E_a = 1 / (1 + 10**((ratings[model_b] - ratings[model_a])/400))

                    # Update ratings
                    ratings[model_a] += K * (score_a - E_a)
                    ratings[model_b] += K * ((1-score_a) - (1-E_a))

    return ratings
```

**Advantages over Pass@1:**

- Accounts for task difficulty
- Differentiates models with similar Pass@1
- Relative ranking robust to benchmark selection

---

## Glicko Rating System

### Overview

**Glicko**, developed by Mark Glickman in 1995, improves upon Elo by adding a **rating deviation (RD)** parameter that quantifies uncertainty. **Glicko-2** (2001) further adds a **volatility** parameter for inconsistent performance.

### Key Innovations Over Elo

| Feature                      | Elo           | Glicko/Glicko-2           |
| ---------------------------- | ------------- | ------------------------- |
| **Uncertainty Modeling**     | No            | Yes (RD parameter)        |
| **Inactivity Handling**      | Static rating | RD increases over time    |
| **Volatility**               | No            | Glicko-2 adds σ parameter |
| **Computational Complexity** | Low           | Medium-High               |
| **Accuracy**                 | Good          | Superior                  |

### Rating Deviation (RD)

**Concept:**

- Low RD (e.g., 30): High confidence, many recent games
- High RD (e.g., 350): High uncertainty, new or inactive player
- RD affects update magnitude: high RD → bigger changes

**Formula (simplified):**

```
RD_new = sqrt(RD² + c²t)

Where:
- RD = current rating deviation
- c = constant for RD growth rate
- t = time periods since last game
```

### Glicko-2 Components

| Parameter      | Symbol | Meaning        | Typical Range                      |
| -------------- | ------ | -------------- | ---------------------------------- |
| **Rating**     | μ      | Skill estimate | 0-3000 (converted from 1500 scale) |
| **Deviation**  | φ      | Uncertainty    | 30-350                             |
| **Volatility** | σ      | Consistency    | 0.3-1.2                            |

### Expected Outcome with RD

**Modified Formula:**

```
E = 1 / (1 + 10^(-g(φ) × (μ_A - μ_B) / 400))

Where:
g(φ) = 1 / sqrt(1 + 3φ² / π²)

φ = combined RD of both players
```

**Effect:**

- Higher combined RD → predictions less confident
- Outcomes against uncertain players less informative

### Glicko-2 Update Process

**Simplified Steps:**

1. **Convert** ratings to Glicko-2 scale
2. **Compute** expected outcomes using g(φ)
3. **Calculate** variance of performance
4. **Update** volatility σ based on surprise
5. **Update** deviation φ (decreases after games)
6. **Update** rating μ using outcomes and variance
7. **Convert** back to standard scale

### Comparison: Elo vs Glicko

**Scenario: Player Returns After 1 Year**

| System     | Rating Change                  | Rationale                    |
| ---------- | ------------------------------ | ---------------------------- |
| **Elo**    | 1500 → 1500                    | No change (static)           |
| **Glicko** | (1500, RD 50) → (1500, RD 200) | RD increases, less confident |

**After First Game Back (Win vs 1600 opponent):**

| System     | New Rating | Explanation                  |
| ---------- | ---------- | ---------------------------- |
| **Elo**    | 1524       | Fixed K=32, standard update  |
| **Glicko** | 1565       | Larger change due to high RD |

### When to Use Glicko

**Advantages:**
✓ Variable player activity (online games)
✓ Need confidence intervals
✓ Modeling skill volatility (inconsistent players)
✓ Research requiring statistical rigor

**Disadvantages:**
✗ Complex implementation
✗ Requires computational resources
✗ Less intuitive than Elo
✗ Harder to explain to users

---

## Metric Comparison

### Absolute vs Relative Metrics

| Metric Type  | Examples         | Strengths                  | Weaknesses                     |
| ------------ | ---------------- | -------------------------- | ------------------------------ |
| **Absolute** | Pass@k, Accuracy | Direct performance measure | Doesn't account for difficulty |
| **Relative** | Elo, Glicko      | Task-difficulty-aware      | No absolute performance info   |

### Pass@1 vs Elo Detailed Comparison

#### Example Scenario

**Two Models on BigCodeBench:**

```
Model X:
- Pass@1: 61.0%
- Solves: Easy tasks (600/1140) + Medium tasks (95/1140)

Model Y:
- Pass@1: 61.0%
- Solves: Medium tasks (300/1140) + Hard tasks (395/1140)

Pass@1: SAME (61.0%)
Elo: Model Y likely higher (solved harder tasks)
```

**Why Elo Differs:**

- Model Y wins matchups on hard tasks
- Model X wins matchups on easy tasks
- Hard task wins weighted more by Elo mechanics
- Result: Model Y gets higher Elo despite same Pass@1

### Complementary Usage

**Best Practice: Report Both**

```markdown
## Model Evaluation Results

### BigCodeBench-Complete

- **Pass@1**: 61.1% (Primary metric)
- **Elo Rating**: 1456 (Relative ranking)
- **Interpretation**: Strong baseline, excels on API-heavy tasks

### Comparison to Baseline

- Pass@1: +5.3% vs GPT-4-base
- Elo: +47 points vs GPT-4-base
```

---

## Implementation Guide

### Pass@k Implementation

**Full Python Script:**

```python
import json
import numpy as np
from scipy.special import comb
from typing import List, Dict

def evaluate_pass_at_k(
    results: List[Dict[str, any]],
    k_values: List[int] = [1, 10, 100]
) -> Dict[str, float]:
    """
    Calculate Pass@k metrics for code generation results

    Args:
        results: List of {"task_id": str, "passed": List[bool]}
        k_values: List of k values to calculate

    Returns:
        Dictionary of {f"pass@{k}": score}
    """
    total_tasks = len(results)
    pass_at_k_scores = {}

    for k in k_values:
        total_score = 0.0

        for result in results:
            n = len(result["passed"])
            c = sum(result["passed"])

            if n < k:
                # Not enough samples
                score = float(c > 0)
            else:
                score = 1.0 - (comb(n - c, k) / comb(n, k))

            total_score += score

        pass_at_k_scores[f"pass@{k}"] = total_score / total_tasks

    return pass_at_k_scores

# Example usage
results = [
    {"task_id": "task_1", "passed": [True, True, False] * 33 + [True]},  # 67% correct, n=100
    {"task_id": "task_2", "passed": [True] * 50 + [False] * 50},  # 50% correct, n=100
]

scores = evaluate_pass_at_k(results, k_values=[1, 10])
print(json.dumps(scores, indent=2))
# {
#   "pass@1": 0.585,
#   "pass@10": 0.98
# }
```

### Elo Implementation

**Python Class:**

```python
class EloRatingSystem:
    def __init__(self, k_factor=32, initial_rating=1000):
        self.k_factor = k_factor
        self.initial_rating = initial_rating
        self.ratings = {}

    def get_rating(self, player):
        return self.ratings.get(player, self.initial_rating)

    def expected_score(self, rating_a, rating_b):
        return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))

    def update_ratings(self, player_a, player_b, score_a):
        """
        Update ratings after a game

        Args:
            player_a: First player ID
            player_b: Second player ID
            score_a: Result for player_a (1.0=win, 0.5=draw, 0.0=loss)
        """
        rating_a = self.get_rating(player_a)
        rating_b = self.get_rating(player_b)

        expected_a = self.expected_score(rating_a, rating_b)
        expected_b = 1 - expected_a

        new_rating_a = rating_a + self.k_factor * (score_a - expected_a)
        new_rating_b = rating_b + self.k_factor * ((1 - score_a) - expected_b)

        self.ratings[player_a] = new_rating_a
        self.ratings[player_b] = new_rating_b

    def get_leaderboard(self):
        return sorted(self.ratings.items(), key=lambda x: x[1], reverse=True)

# Example: Model competition on code tasks
elo = EloRatingSystem(k_factor=32)

task_results = {
    ("gpt-4", "claude-3"): 1.0,  # gpt-4 wins
    ("gpt-4", "llama-2"): 1.0,   # gpt-4 wins
    ("claude-3", "llama-2"): 0.5,  # draw
}

for (model_a, model_b), score in task_results.items():
    elo.update_ratings(model_a, model_b, score)

print("Leaderboard:")
for rank, (model, rating) in enumerate(elo.get_leaderboard(), 1):
    print(f"{rank}. {model}: {rating:.1f}")
```

### Glicko-2 Implementation

**Simplified Python (Full version is complex):**

```python
import math

class GlickoRating:
    def __init__(self, mu=1500, phi=350, sigma=0.06):
        self.mu = mu      # Rating
        self.phi = phi    # Rating deviation
        self.sigma = sigma  # Volatility

    def __repr__(self):
        return f"Rating({self.mu:.1f} ± {self.phi:.1f}, σ={self.sigma:.3f})"

def g(phi):
    """RD impact on prediction"""
    return 1 / math.sqrt(1 + 3 * phi**2 / math.pi**2)

def expected_score(mu_a, mu_b, phi_b):
    """Expected outcome with RD consideration"""
    return 1 / (1 + 10 ** (-g(phi_b) * (mu_a - mu_b) / 400))

# Usage (simplified, full Glicko-2 requires iterative sigma update)
player_a = GlickoRating(mu=1500, phi=200, sigma=0.06)
player_b = GlickoRating(mu=1700, phi=50, sigma=0.06)

E_a = expected_score(player_a.mu, player_b.mu, player_b.phi)
print(f"Player A expected score: {E_a:.2%}")
# Output: Player A expected score: ~22% (lower than Elo's 24% due to RD)
```

**Note**: Full Glicko-2 implementation requires iterative numerical methods for volatility updates. Consider using existing libraries like `glicko2` in Python.

---

## Best Practices

### 1. Always Report Context

```markdown
**Bad**: "Our model achieves 85%"

**Good**: "Our model achieves:

- Pass@1: 85% on HumanEval (greedy, temp=0.0)
- Elo: 1523 on BigCodeBench-Complete vs 10 baselines
- Measured on: 2025-11-08"
```

### 2. Use Confidence Intervals

```python
from scipy import stats

def pass_at_k_with_confidence(results, k, confidence=0.95):
    """Calculate Pass@k with confidence interval"""
    scores = [calculate_pass_at_k(r, k) for r in results]
    mean = np.mean(scores)
    sem = stats.sem(scores)
    ci = stats.t.interval(confidence, len(scores)-1, mean, sem)
    return mean, ci

# Report: Pass@1 = 85.3% ± 2.1% (95% CI)
```

### 3. Choose Metrics by Use Case

| Use Case                  | Recommended Metrics              |
| ------------------------- | -------------------------------- |
| **Production deployment** | Pass@1 (cost-effective baseline) |
| **Research**              | Pass@1, Pass@10, Elo             |
| **User-facing tools**     | Pass@1, Pass@3 (limited retries) |
| **Model comparison**      | Elo + Pass@1 (complementary)     |
| **Active learning**       | Glicko (handles uncertainty)     |

### 4. Avoid Common Pitfalls

**Pitfall 1: Comparing Pass@1 vs Pass@10**

```
Wrong: "Model A (Pass@10=90%) beats Model B (Pass@1=85%)"
Right: Compare like-for-like: Pass@1 vs Pass@1
```

**Pitfall 2: Ignoring Variance**

```
Wrong: "85.2% > 84.8%, so A is better"
Right: Check if difference is statistically significant
```

**Pitfall 3: Elo Without Stabilization**

```
Wrong: Report Elo after 10 games
Right: Run 500+ iterations for convergence
```

---

## Future Directions

### Emerging Metrics (2025+)

1. **Partial Credit Scores**: Reward nearly-correct solutions
2. **Execution-Based Metrics**: Beyond pass/fail (performance, style)
3. **Multi-Dimensional Ratings**: Separate Elo for different task types
4. **Human-Preference Alignment**: Elo from human judgments
5. **Adaptive K-Factors**: Dynamic adjustment based on task difficulty

### Research Questions

- Optimal k-values for practical deployment?
- Elo stability with limited task sets?
- Glicko-2 for multi-modal code tasks?
- Cross-benchmark Elo normalization?

---

## Resources

### Academic Papers

- "The Rating of Chess Players, Past and Present" (Elo, 1978)
- "A Comprehensive Guide to Glicko and Glicko-2" (Glickman, 2012)
- "Evaluating Large Language Models Trained on Code" (Chen et al., 2021 - HumanEval)

### Implementations

- **Elo**: Simple Python examples above
- **Glicko-2**: `glicko2` package (Python), JavaScript implementations available
- **Pass@k**: Included in `human-eval` package

### Tools

- **BigCode Leaderboard**: Uses calibrated Pass@1 + Elo
- **Chatbot Arena**: Elo for LLM comparison (Bradley-Terry model)

---

## Version History

- **v1.0** (2025-11-08): Comprehensive metrics documentation
  - Pass@k with mathematical derivations
  - Elo system with first-principles explanation
  - Glicko comparison and use cases
  - Implementation examples for all metrics

---

## See Also

- [CODE_BENCHMARKS.md](CODE_BENCHMARKS.md) - Where these metrics are applied
- [ADVANCED_PROMPTING.md](ADVANCED_PROMPTING.md) - Techniques to improve scores
- [COMPREHENSIVE_GUIDE.md](COMPREHENSIVE_GUIDE.md) - Integrated usage guide
