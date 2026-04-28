# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import sys
from typing import Any

# Ensure the vendored code can find its own sibling modules if they use absolute imports
# (This adds pso_experiments/pso_nn to the path temporarily)
sys.path.append(os.path.join(os.path.dirname(__file__), "pso_nn"))

# Import from the vendored package
# We use try/except to handle both running as a script and as a module
try:
    from pso_experiments.pso_nn.nn.layers import Layer
    from pso_experiments.pso_nn.nn.losses import BinaryCrossEntropyLoss
    from pso_experiments.pso_nn.nn.model import Model
    from pso_experiments.pso_nn.nn.pipeline import DataLoader
except ImportError:
    # Fallback for when running directly inside the folder without package context
    from pso_nn.nn.layers import Layer
    from pso_nn.nn.losses import BinaryCrossEntropyLoss
    from pso_nn.nn.model import Model
    from pso_nn.nn.pipeline import DataLoader


# ----------------------------------------------------------------------
# Helper – tiny synthetic dataset for quick sanity checks
# ----------------------------------------------------------------------
def _xor_dataset() -> tuple[list[list[float]], list[list[float]]]:
    """Return a classic XOR toy‑dataset (inputs, targets)."""
    X = [[0, 0], [0, 1], [1, 0], [1, 1]]
    y = [[0], [1], [1], [0]]
    return X, y


# ----------------------------------------------------------------------
# Public wrapper class
# ----------------------------------------------------------------------
class PsoModel:
    """A convenience wrapper around the experimental ``Model`` class."""

    def __init__(self) -> None:
        # Build a *very* small network – feel free to customise.
        self.model = Model()
        self.model.add_layer(Layer(2, 8, activation="tanh"))
        self.model.add_layer(Layer(8, 8, activation="tanh"))
        self.model.add_layer(Layer(8, 1, activation="sigmoid"))

        # Compile with the PSO‑backed optimizer
        self.model.compile(
            loss=BinaryCrossEntropyLoss,
            data_loader=DataLoader,
            metric=self._accuracy,
            batches_per_epoch=20,
            n_workers=4,
        )

    @staticmethod
    def _accuracy(y_true: Any, y_pred: Any) -> float:
        """Threshold‑based accuracy for binary outputs."""
        try:
            # Handle standard list or numpy input
            import numpy as np

            y_pred = np.array(y_pred)
            y_true = np.array(y_true)
            preds = (y_pred > 0.5).astype(int)
            return float((preds == y_true).mean())
        except ImportError:
            # Pure python fallback if numpy fails (though numpy is req by upstream)
            return 0.0

    def fit(
        self,
        X_train: list[list[float]],
        y_train: list[list[float]],
        epochs: int = 50,
        X_val: list[list[float]] | None = None,
        y_val: list[list[float]] | None = None,
    ) -> dict[str, Any]:
        """Train the model with PSO."""
        return self.model.fit(
            X_train,
            y_train,
            epochs=epochs,
            X_val=X_val,
            y_val=y_val,
        )

    def predict(self, X: list[list[float]]) -> list[list[float]]:
        """Run a forward pass on *X*."""
        return self.model.predict(X)

    @classmethod
    def demo_xor(cls) -> tuple[list[list[float]], list[list[float]]]:
        """Quick end‑to‑end demo that trains on XOR."""
        X, y = _xor_dataset()
        model = cls()
        model.fit(X, y, epochs=30)
        preds = model.predict(X)
        return X, preds
