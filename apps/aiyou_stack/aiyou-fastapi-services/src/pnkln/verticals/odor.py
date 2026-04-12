"""
Pnkln Odor Vertical
Model airflow/odor/CBRN scrubbing with constraints.
"""

from __future__ import annotations

import numpy as np


def odor_sim(
    n: int = 128, src: list[tuple[int, int, float]] = None, k: float = 0.92, fx: float = 0.02
) -> np.ndarray:
    """
    Simulate odor diffusion using a simple automata or PDE approximation.
    n: Grid size (n x n)
    src: List of sources (x, y, strength)
    k: Decay/Diffusion factor
    fx: Flow/Spread factor
    """
    if src is None:
        src = [(64, 64, 1.0)]

    f = np.zeros((n, n), dtype=float)

    # Run simulation for fixed steps (256 from rollup)
    for _ in range(256):
        nf = np.copy(f)
        # Simple diffusion kernel (center * k + neighbors * fx)
        # Slicing: [1:-1, 1:-1] exclude borders
        # Neighbors: up, down, left, right
        nf[1:-1, 1:-1] = f[1:-1, 1:-1] * k + fx * (
            f[:-2, 1:-1] + f[2:, 1:-1] + f[1:-1, :-2] + f[1:-1, 2:]
        )

        # Add sources
        for x, y, s in src:
            nf[x % n, y % n] += s

        f = nf

    return f


def odor_score(f: np.ndarray, mask: np.ndarray = None) -> float:
    """Calculate mean odor score, optionally masked."""
    if mask is None:
        return float(f.mean())
    return float((f * mask).mean())
