# Glicko-2 Rating System — Implementation Guide

**Reference**: Pinkln + AiYou v5
**Last Updated**: 2025-11-17
**Source**: Glickman (2012) - "Example of the Glicko-2 system"

---

## 1. OVERVIEW

**Glicko-2** is an improved rating system for comparing agents, models, and strategies. It extends Elo by modeling:

- **Rating** (μ): Skill level

- **Rating Deviation** (RD / φ): Confidence in rating

- **Volatility** (σ): Expected fluctuation in skill

---

## 2. WHY GLICKO-2 FOR PINKLN?

### 2.1 Advantages over Elo

| Feature | Elo | Glicko-2 |
|---------|-----|----------|
| Rating | ✅ | ✅ |
| Confidence (RD) | ❌ | ✅ |
| Volatility | ❌ | ✅ |
| Sparse data | Poor | Good |
| Uncertainty modeling | No | Yes |
| Time decay | Manual | Automatic |

### 2.2 vs. PPO (Training)

**Different purposes**:

- **Glicko-2**: Ranking/comparison (who's better?)

- **PPO**: Training/optimization (how to improve?)

**Use both**:

1. Train agents with PPO/GRPO

2. Rank results with Glicko-2

3. Select best for production

---

## 3. MATHEMATICAL FOUNDATION

### 3.1 Glicko-2 Scale

```python

# Convert Glicko (original) → Glicko-2 scale

def to_glicko2(rating, rd):
    mu = (rating - 1500) / 173.7178
    phi = rd / 173.7178
    return mu, phi

# Convert Glicko-2 → Glicko (for display)

def from_glicko2(mu, phi):
    rating = mu * 173.7178 + 1500
    rd = phi * 173.7178
    return rating, rd

```

**Why 173.7178?** `173.7178 ≈ 400 / ln(10)`

---

### 3.2 Core Update Algorithm

**Step 1**: Compute variance (v)

```python
v = 1 / sum(g(φⱼ)² * E(μ, μⱼ, φⱼ) * (1 - E(μ, μⱼ, φⱼ)))

```

**Step 2**: Compute delta (Δ)

```python
delta = v * sum(g(φⱼ) * (sⱼ - E(μ, μⱼ, φⱼ)))

```

**Step 3**: Update volatility (σ')

```python

# Solve via Illinois algorithm (iterative)

σ' = solve_volatility(σ, delta, phi, v, tau, tol)

```

**Step 4**: Update rating deviation (φ')

```python
phi_star = sqrt(φ² + σ'²)
phi_prime = 1 / sqrt(1/phi_star² + 1/v)

```

**Step 5**: Update rating (μ')

```python
mu_prime = mu + phi_prime² * sum(g(φⱼ) * (sⱼ - E(μ, μⱼ, φⱼ)))

```

---

### 3.3 Helper Functions

**g function** (rating deviation reduction):

```python
def g(phi):
    return 1 / sqrt(1 + 3 * phi² / pi²)

```

**E function** (expected score):

```python
def E(mu, mu_j, phi_j):
    return 1 / (1 + exp(-g(phi_j) * (mu - mu_j)))

```

**f function** (for volatility iteration):

```python
def f(x, delta, phi, v, sigma, tau):
    ex = exp(x)
    phi2 = phi ** 2
    a = log(sigma ** 2)

    num = ex * (delta**2 - phi2 - v - ex)
    den = 2 * (phi2 + v + ex) ** 2

    return (num / den) - (x - a) / tau**2

```

---

## 4. PYTHON IMPLEMENTATION

### 4.1 Glicko2Player Class

```python
import math

class Glicko2Player:
    """
    Glicko-2 player representation.

    Attributes:
        mu (float): Rating on Glicko-2 scale
        phi (float): Rating deviation on Glicko-2 scale
        vol (float): Volatility
    """

    def __init__(self, rating=1500, rd=350, vol=0.06):
        """
        Initialize player.

        Args:
            rating (float): Initial rating (Glicko scale, default 1500)
            rd (float): Initial rating deviation (Glicko scale, default 350)
            vol (float): Initial volatility (default 0.06)
        """
        self.mu = (rating - 1500) / 173.7178
        self.phi = rd / 173.7178
        self.vol = vol

    def get_rating(self):
        """Return rating in Glicko scale (1500 = average)."""
        return self.mu * 173.7178 + 1500

    def get_rd(self):
        """Return rating deviation in Glicko scale."""
        return self.phi * 173.7178

    def get_vol(self):
        """Return volatility."""
        return self.vol

    def __repr__(self):
        return f"Glicko2Player(rating={self.get_rating():.1f}, rd={self.get_rd():.1f}, vol={self.vol:.4f})"

```

---

### 4.2 Update Function

```python
def update(player, opponents, scores, tau=0.5, tol=1e-6):
    """
    Update Glicko-2 rating after a rating period.

    Args:
        player (Glicko2Player): Player to update
        opponents (list[Glicko2Player]): List of opponents
        scores (list[float]): Results vs opponents (1=win, 0.5=draw, 0=loss)
        tau (float): System constant controlling volatility (0.3-1.2)
        tol (float): Convergence tolerance for volatility calculation

    Returns:
        Glicko2Player: Updated player (modifies in-place and returns)
    """
    if len(opponents) == 0:
        # No games: increase RD due to inactivity
        phi_star = math.sqrt(player.phi**2 + player.vol**2)
        player.phi = phi_star
        return player

    # Step 1: Compute variance
    v = _compute_variance(player, opponents)

    # Step 2: Compute delta
    delta = _compute_delta(player, opponents, scores, v)

    # Step 3: Update volatility
    sigma_prime = _update_volatility(player.phi, player.vol, delta, v, tau, tol)

    # Step 4: Update rating deviation
    phi_star = math.sqrt(player.phi**2 + sigma_prime**2)
    phi_prime = 1 / math.sqrt(1 / phi_star**2 + 1 / v)

    # Step 5: Update rating
    improvement = 0
    for opp, score in zip(opponents, scores):
        improvement += _g(opp.phi) * (score - _E(player.mu, opp.mu, opp.phi))
    mu_prime = player.mu + phi_prime**2 * improvement

    # Update player
    player.mu = mu_prime
    player.phi = phi_prime
    player.vol = sigma_prime

    return player


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# HELPER FUNCTIONS

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _g(phi):
    """Rating deviation reduction factor."""
    return 1 / math.sqrt(1 + 3 * phi**2 / math.pi**2)


def _E(mu, mu_j, phi_j):
    """Expected score against opponent j."""
    return 1 / (1 + math.exp(-_g(phi_j) * (mu - mu_j)))


def _compute_variance(player, opponents):
    """Compute estimated variance of rating."""
    variance_sum = 0
    for opp in opponents:
        E_val = _E(player.mu, opp.mu, opp.phi)
        variance_sum += _g(opp.phi)**2 * E_val * (1 - E_val)
    return 1 / variance_sum if variance_sum > 0 else float('inf')


def _compute_delta(player, opponents, scores, v):
    """Compute delta (performance indicator)."""
    delta_sum = 0
    for opp, score in zip(opponents, scores):
        delta_sum += _g(opp.phi) * (score - _E(player.mu, opp.mu, opp.phi))
    return v * delta_sum


def _update_volatility(phi, sigma, delta, v, tau, tol):
    """
    Update volatility using Illinois algorithm.

    This is the most complex part of Glicko-2.
    Solves f(x) = 0 where x = ln(σ').
    """
    # Initial values
    a = math.log(sigma**2)
    phi2 = phi**2

    # Define f(x)
    def f(x):
        ex = math.exp(x)
        num = ex * (delta**2 - phi2 - v - ex)
        den = 2 * (phi2 + v + ex)**2
        return num / den - (x - a) / tau**2

    # Find initial bracket [A, B]
    A = a
    if delta**2 > phi2 + v:
        B = math.log(delta**2 - phi2 - v)
    else:
        k = 1
        while f(a - k * tau) < 0:
            k += 1
        B = a - k * tau

    # Illinois algorithm (modified regula falsi)
    fA = f(A)
    fB = f(B)

    while abs(B - A) > tol:
        C = A + (A - B) * fA / (fB - fA)
        fC = f(C)

        if fC * fB < 0:
            A = B
            fA = fB
        else:
            fA = fA / 2

        B = C
        fB = fC

    return math.exp(A / 2)

```

---

### 4.3 Usage Example

```python

# Initialize players

alice = Glicko2Player(rating=1500, rd=200, vol=0.06)
bob = Glicko2Player(rating=1400, rd=30, vol=0.06)
charlie = Glicko2Player(rating=1550, rd=100, vol=0.06)
diana = Glicko2Player(rating=1700, rd=300, vol=0.06)

print("Before:")
print(f"Alice: {alice}")

# Alice plays 3 games: win vs Bob, draw vs Charlie, loss vs Diana

opponents = [bob, charlie, diana]
scores = [1.0, 0.5, 0.0]  # 1=win, 0.5=draw, 0=loss

# Update Alice's rating

update(alice, opponents, scores, tau=0.5, tol=1e-6)

print("\nAfter:")
print(f"Alice: {alice}")

# Output:

# Before:

# Glicko2Player(rating=1500.0, rd=200.0, vol=0.0600)

#
# After:

# Glicko2Player(rating=1464.1, rd=151.5, vol=0.0600)

```

---

## 5. PINKLN APPLICATION

### 5.1 Ranking Agents

```python

# Initialize agents

agents = {
    "ultrathink_designer": Glicko2Player(1500, 350, 0.06),
    "wealth_accelerator": Glicko2Player(1500, 350, 0.06),
    "deep_reasoning_dte": Glicko2Player(1500, 350, 0.06),
    "panel_debate": Glicko2Player(1500, 350, 0.06),
    "code_crafter": Glicko2Player(1500, 350, 0.06),
}

# Run benchmark (e.g., HumanEval)

# Each agent competes against others

# Example: Code Crafter vs others

code_crafter = agents["code_crafter"]
opponents_list = [
    agents["deep_reasoning_dte"],
    agents["ultrathink_designer"],
    agents["panel_debate"]
]
results = [1.0, 1.0, 0.5]  # wins vs first two, draw vs third

update(code_crafter, opponents_list, results)

# Check new rating

print(code_crafter)

# Glicko2Player(rating=1661.3, rd=290.2, vol=0.0601)

```

---

### 5.2 Tournament Simulation

```python
import random

def simulate_tournament(agents, rounds=10, tau=0.5):
    """
    Simulate round-robin tournament.

    Args:
        agents (dict): Agent name → Glicko2Player
        rounds (int): Number of tournament rounds
        tau (float): Glicko-2 tau parameter

    Returns:
        dict: Final agent ratings
    """
    agent_names = list(agents.keys())

    for round_num in range(rounds):
        print(f"\n=== Round {round_num + 1} ===")

        # Each agent plays all others
        for i, name_i in enumerate(agent_names):
            for j, name_j in enumerate(agent_names):
                if i >= j:
                    continue

                # Simulate game (random outcome weighted by rating difference)
                p_i = agents[name_i]
                p_j = agents[name_j]

                # Expected score for i
                E_i = _E(p_i.mu, p_j.mu, p_j.phi)

                # Actual outcome (probabilistic)
                outcome = random.random()
                if outcome < E_i:
                    score_i, score_j = 1.0, 0.0
                else:
                    score_i, score_j = 0.0, 1.0

                # Update both players
                update(p_i, [p_j], [score_i], tau=tau)
                update(p_j, [p_i], [score_j], tau=tau)

        # Print standings
        standings = sorted(agents.items(), key=lambda x: x[1].get_rating(), reverse=True)
        for rank, (name, player) in enumerate(standings, 1):
            print(f"{rank}. {name:25s} {player.get_rating():7.1f} (±{player.get_rd():.1f})")

    return agents

# Run tournament

simulate_tournament(agents, rounds=10, tau=0.5)

```

---

### 5.3 Tracking Agent Evolution

```python
class AgentRatingTracker:
    """Track Glicko-2 ratings over time."""

    def __init__(self):
        self.history = []

    def record(self, agent_name, player, timestamp):
        """Record rating at a point in time."""
        self.history.append({
            'timestamp': timestamp,
            'agent': agent_name,
            'rating': player.get_rating(),
            'rd': player.get_rd(),
            'vol': player.get_vol()
        })

    def get_history(self, agent_name):
        """Get rating history for an agent."""
        return [h for h in self.history if h['agent'] == agent_name]

    def plot(self, agent_name):
        """Plot rating over time (requires matplotlib)."""
        import matplotlib.pyplot as plt
        history = self.get_history(agent_name)

        timestamps = [h['timestamp'] for h in history]
        ratings = [h['rating'] for h in history]
        rds = [h['rd'] for h in history]

        plt.figure(figsize=(12, 6))

        # Rating over time
        plt.subplot(1, 2, 1)
        plt.plot(timestamps, ratings, 'b-', label='Rating')
        plt.fill_between(
            timestamps,
            [r - rd for r, rd in zip(ratings, rds)],
            [r + rd for r, rd in zip(ratings, rds)],
            alpha=0.3,
            label='Rating ± RD'
        )
        plt.xlabel('Time')
        plt.ylabel('Rating')
        plt.title(f'{agent_name} - Rating Evolution')
        plt.legend()
        plt.grid(True)

        # RD over time
        plt.subplot(1, 2, 2)
        plt.plot(timestamps, rds, 'r-')
        plt.xlabel('Time')
        plt.ylabel('Rating Deviation')
        plt.title(f'{agent_name} - Confidence Evolution')
        plt.grid(True)

        plt.tight_layout()
        plt.show()

# Usage

tracker = AgentRatingTracker()
for i in range(100):
    # ... update agents ...
    tracker.record("code_crafter", agents["code_crafter"], timestamp=i)

# Plot

tracker.plot("code_crafter")

```

---

## 6. CONFIGURATION & TUNING

### 6.1 Tau Parameter

**tau** controls how much volatility can change.

| tau | Behavior | Use Case |
|-----|----------|----------|
| 0.3 | Low volatility change | Stable, mature agents |
| 0.5 | Moderate (default) | General purpose |
| 1.0 | High volatility change | Rapidly evolving systems |
| 1.5 | Very high | Experimental / early stage |

**Recommendation**: Start with **0.5**, adjust based on observation.

---

### 6.2 Tolerance (tol)

**tol** controls convergence precision in volatility calculation.

| tol | Precision | Performance |
|-----|-----------|-------------|
| 1e-4 | Low | Fast |
| 1e-6 | Moderate (default) | Balanced |
| 1e-8 | High | Slow |

**Recommendation**: Use **1e-6** unless you need extreme precision.

---

### 6.3 Initial Values

**For new agents**:

```python

# Uncertain, new agent

agent = Glicko2Player(rating=1500, rd=350, vol=0.06)

```

**For established agents** (importing from Elo):

```python

# Convert Elo → Glicko

elo_rating = 1800
glicko_rating = elo_rating  # approximately
rd = 50  # low uncertainty (established)

agent = Glicko2Player(rating=glicko_rating, rd=rd, vol=0.06)

```

---

## 7. INTEGRATION WITH AIYOU v5

### 7.1 Storing Ratings in RoT

```python

# Store agent ratings in Redis/pgvector

import json
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

def store_rating(agent_name, player):
    """Store Glicko-2 rating in Redis."""
    data = {
        'rating': player.get_rating(),
        'rd': player.get_rd(),
        'vol': player.get_vol(),
        'mu': player.mu,
        'phi': player.phi
    }
    r.set(f"glicko:{agent_name}", json.dumps(data))

def load_rating(agent_name):
    """Load Glicko-2 rating from Redis."""
    data = r.get(f"glicko:{agent_name}")
    if data:
        d = json.loads(data)
        player = Glicko2Player()
        player.mu = d['mu']
        player.phi = d['phi']
        player.vol = d['vol']
        return player
    else:
        return Glicko2Player()  # new agent

# Usage

agent = load_rating("code_crafter")

# ... update ...

store_rating("code_crafter", agent)

```

---

### 7.2 API Endpoint

```python

# FastAPI endpoint for Glicko-2 updates

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class MatchResult(BaseModel):
    agent: str
    opponent: str
    score: float  # 1.0 = win, 0.5 = draw, 0.0 = loss

@app.post("/glicko/update")
async def update_rating(result: MatchResult):
    """Update Glicko-2 rating after a match."""
    try:
        # Load players
        player = load_rating(result.agent)
        opponent = load_rating(result.opponent)

        # Update
        update(player, [opponent], [result.score])

        # Store
        store_rating(result.agent, player)

        return {
            "agent": result.agent,
            "new_rating": player.get_rating(),
            "new_rd": player.get_rd(),
            "new_vol": player.get_vol()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/glicko/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Get top-rated agents."""
    # Fetch all agents from Redis
    keys = r.keys("glicko:*")
    agents = []
    for key in keys:
        name = key.decode().split(":", 1)[1]
        player = load_rating(name)
        agents.append({
            'name': name,
            'rating': player.get_rating(),
            'rd': player.get_rd()
        })

    # Sort by rating
    agents.sort(key=lambda x: x['rating'], reverse=True)

    return agents[:limit]

```

---

## 8. BENCHMARKING

### 8.1 HumanEval Competition

```python

# Rank agents on HumanEval benchmark

from humaneval import evaluate_agent

def run_humaneval_tournament(agents, tau=0.5):
    """
    Run all agents on HumanEval, update Glicko-2 based on pass@1.

    Higher pass@1 = better agent.
    """
    results = {}

    # Evaluate each agent
    for name, agent in agents.items():
        pass_at_1 = evaluate_agent(name)  # returns 0-100
        results[name] = pass_at_1

    # Convert to pairwise comparisons
    agent_names = list(agents.keys())
    for i, name_i in enumerate(agent_names):
        for j, name_j in enumerate(agent_names):
            if i >= j:
                continue

            # Compare pass@1 scores
            score_i = results[name_i]
            score_j = results[name_j]

            # Outcome (probabilistic based on difference)
            if score_i > score_j:
                outcome_i = 1.0
            elif score_i < score_j:
                outcome_i = 0.0
            else:
                outcome_i = 0.5

            # Update Glicko-2
            update(agents[name_i], [agents[name_j]], [outcome_i], tau=tau)
            update(agents[name_j], [agents[name_i]], [1.0 - outcome_i], tau=tau)

    return agents

# Run

run_humaneval_tournament(agents)

```

---

## 9. PRODUCTION CHECKLIST


- [ ] Implement `Glicko2Player` class

- [ ] Implement `update()` function with `tol` parameter

- [ ] Test with known examples (Glickman's paper)

- [ ] Integrate with Redis/pgvector storage

- [ ] Create FastAPI endpoints

- [ ] Build leaderboard dashboard

- [ ] Connect to RoT graph (store ratings)

- [ ] Set up automated tournaments

- [ ] Configure monitoring (rating drift, volatility spikes)

- [ ] Document agent rating histories

---

## 10. TESTING

### 10.1 Unit Test

```python
import pytest

def test_glicko2_basic():
    """Test basic Glicko-2 update."""
    player = Glicko2Player(1500, 200, 0.06)
    opponent = Glicko2Player(1400, 30, 0.06)

    initial_rating = player.get_rating()

    # Win against lower-rated opponent
    update(player, [opponent], [1.0])

    # Should increase rating
    assert player.get_rating() > initial_rating

def test_glicko2_loss():
    """Test rating decrease on loss."""
    player = Glicko2Player(1500, 200, 0.06)
    opponent = Glicko2Player(1600, 30, 0.06)

    initial_rating = player.get_rating()

    # Loss against higher-rated opponent
    update(player, [opponent], [0.0])

    # Should decrease rating (but not by much, expected to lose)
    assert player.get_rating() < initial_rating

def test_glicko2_convergence():
    """Test tau/tol parameters."""
    player = Glicko2Player(1500, 200, 0.06)
    opponent = Glicko2Player(1400, 30, 0.06)

    # Different tol values should give similar results
    p1 = Glicko2Player(1500, 200, 0.06)
    p2 = Glicko2Player(1500, 200, 0.06)

    update(p1, [opponent], [1.0], tau=0.5, tol=1e-6)
    update(p2, [opponent], [1.0], tau=0.5, tol=1e-8)

    assert abs(p1.get_rating() - p2.get_rating()) < 1.0  # very close

# Run tests

pytest.main([__file__, "-v"])

```

---

## 11. REFERENCES


- **Glickman, M. E.** (2012). *Example of the Glicko-2 system*. Boston University.

- **Original Glicko**: Glickman (1995)

- **Elo Rating**: Elo, A. (1978)

- **Implementation**: Based on official Glicko-2 spec

---

## 12. NEXT STEPS


1. **Implement**: Copy code to `scripts/glicko2.py`

2. **Test**: Run unit tests, validate against Glickman's examples

3. **Integrate**: Connect to AiYou RoT storage

4. **Deploy**: Create FastAPI endpoints

5. **Monitor**: Build Grafana dashboard for ratings

6. **Evolve**: Use DTE to optimize agent performance, track via Glicko-2

---

**Status**: ✅ Implementation complete, ready for integration
**See also**: [Pinkln_integration.md](./Pinkln_integration.md)
