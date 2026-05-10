# Glicko Doctrine

> **STATUS**: ACTIVE
> **REPLACES**: Elo Rating System

## Philosophy

Ratings aren't static; they're alive. We use Glicko-2 because it accounts for **uncertainty** (Ratings Deviation - RD) and **volatility**.

- **Elo**: Assumes constant performance.
- **Glicko**: Knows when we don't know. A high RD means "test fast".

## Implementation

```python
def glicko_update(rating, rd, volatility, opponent_rating, opponent_rd, outcome):
    """
    Update Glicko-2 rating based on match outcome.
    outcome: 1 (win), 0 (loss), 0.5 (draw)
    """
    # ... implementation of Glicko-2 math ...
    pass
```

## Application

1.  **Benchmarks**: Rate models (Pass@1 = Win). High RD = Needs more tests.
2.  **Debates**: Rate arguments.
3.  **Wealth**: Rate opportunities (Expected ROI = Rating, Risk = Volatility).

## System Prompt Addition

"<role>Rater</role> <task>Integrate Glicko for evaluations</task> <constraints>Handle RD/volatility</constraints> <examples>Rank benchmark models</examples>"
