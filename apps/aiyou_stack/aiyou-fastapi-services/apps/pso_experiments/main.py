"""
Minimal entry‑point to verify that the PSO backend works.
Run:
    $ python -m pso_experiments.main
"""

import os
import sys

# Ensure we can import the sibling module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pso_experiments.pso_backend import PsoModel

if __name__ == "__main__":
    print("🚀 Starting PSO Training on XOR dataset...")

    # Train on the XOR toy‑problem and print predictions
    X, preds = PsoModel.demo_xor()

    print("\n--- Training Complete ---")
    print(f"XOR Inputs : {X}")
    print("Predictions:")
    for x_val, p_val in zip(X, preds, strict=False):
        print(f"  {x_val} -> {p_val[0]:.4f}")
