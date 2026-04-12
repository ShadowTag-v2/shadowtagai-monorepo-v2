#!/usr/bin/env python3
"""
PNKLN // PORTFOLIO MONTE CARLO SIMULATION
Calculates expected value, standard deviation, and 5% VaR
"""

import random
import statistics as st
from math import exp


def sim(n: int, y: int, base: float, alloc: dict, mu: dict, sigma: dict):
    """
    Run Monte Carlo simulation for portfolio.

    Args:
        n: Number of simulations
        y: Years to project
        base: Starting capital
        alloc: Asset allocation dict (asset -> weight)
        mu: Expected returns dict (asset -> annual return)
        sigma: Volatility dict (asset -> std dev)

    Returns:
        tuple: (mean, std_dev, var_5_percent)
    """
    results = []
    for _ in range(n):
        value = 0
        for asset, pct in alloc.items():
            x = base * pct
            for _ in range(y):
                z = random.gauss(mu[asset], sigma[asset])
                x *= exp(z)
            value += x
        results.append(value)

    return st.mean(results), st.pstdev(results), sorted(results)[int(0.05 * n)]


if __name__ == "__main__":
    # Default portfolio allocation
    alloc = {"crypto": 0.5, "equity": 0.4, "metals": 0.1}
    mu = {"crypto": 0.10, "equity": 0.07, "metals": 0.04}
    sigma = {"crypto": 0.6, "equity": 0.2, "metals": 0.15}

    mean, std, var5 = sim(2000, 3, 400000, alloc, mu, sigma)

    print("PNKLN Portfolio Monte Carlo (3yr projection, $400k base)")
    print("=" * 50)
    print(f"Expected Value:  ${round(mean, 2):,.2f}")
    print(f"Std Deviation:   ${round(std, 2):,.2f}")
    print(f"5% VaR (worst):  ${round(var5, 2):,.2f}")
