"""Null-Model Validator — Permutation testing for hallucinated alpha.

Prevents the system from reporting 'discoveries' that are statistical noise.
Runs a permuted baseline (shuffled labels) through the same pipeline and
compares scores. If the real result doesn't significantly beat the null,
it's noise, not signal.

This is the epistemological rigor layer of the Cor.Uphillsnowball doctrine.
"""

import random
import statistics
from dataclasses import dataclass
from collections.abc import Callable


@dataclass(frozen=True)
class NullTestResult:
    """Immutable record of a null-model validation run."""

    real_mean: float
    null_mean: float
    null_std: float
    p_value: float
    significant: bool
    verdict: str  # "SIGNAL" or "NOISE"
    n_permutations: int


def null_model_test(
    real_scores: list[float],
    data: list,
    score_fn: Callable[[list], list[float]],
    n_permutations: int = 1000,
    alpha: float = 0.05,
    seed: int | None = None,
) -> NullTestResult:
    """Run permutation test against null hypothesis of no effect.

    Args:
        real_scores: Actual scores from the pipeline.
        data: Input data to permute.
        score_fn: Function that scores a dataset (returns list[float]).
        n_permutations: Number of random shuffles.
        alpha: Significance threshold (default 5%).
        seed: Optional RNG seed for reproducibility.

    Returns:
        NullTestResult with verdict "SIGNAL" (real) or "NOISE" (spurious).
    """
    if seed is not None:
        random.seed(seed)

    real_mean = statistics.mean(real_scores)
    null_means: list[float] = []

    for _ in range(n_permutations):
        shuffled = data.copy()
        random.shuffle(shuffled)
        null_scores = score_fn(shuffled)
        null_means.append(statistics.mean(null_scores))

    # p-value: fraction of null results >= real result
    p_value = sum(1 for n in null_means if n >= real_mean) / n_permutations
    null_std = statistics.stdev(null_means) if len(null_means) > 1 else 0.0

    return NullTestResult(
        real_mean=real_mean,
        null_mean=statistics.mean(null_means),
        null_std=null_std,
        p_value=p_value,
        significant=p_value < alpha,
        verdict="SIGNAL" if p_value < alpha else "NOISE",
        n_permutations=n_permutations,
    )
