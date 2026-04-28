# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from pso_experiments.pso_backend import PsoModel


def test_xor_learning():
    """Sanity‑check: after a few generations the model should separate the XOR classes."""
    X, y = PsoModel.demo_xor()
    # Convert predictions to binary decisions
    decisions = [(pred[0] > 0.5) for pred in y]

    # Expected pattern for XOR:
    # [0,0]->0 (False), [0,1]->1 (True), [1,0]->1 (True), [1,1]->0 (False)
    # Note: PSO is stochastic, so we check if it got at least the clear logic right
    # but strict equality assert implies it converged.
    assert decisions == [False, True, True, False], f"Model failed XOR: {y}"


def test_predict_shape():
    model = PsoModel()
    # Train quickly on the toy data to initialise internal weights
    X_train, y_train = [[0, 0], [0, 1]], [[0], [1]]
    model.fit(X_train, y_train, epochs=2)
    preds = model.predict([[0, 1]])

    assert isinstance(preds, list)
    assert len(preds) == 1
    assert isinstance(preds[0], list)
