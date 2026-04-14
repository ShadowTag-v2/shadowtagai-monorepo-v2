"""Backend abstraction layer for TinyTorch.
Allows switching between numpy (CPU) and jax.numpy (TPU/GPU) via environment variable.
"""

import os
import sys

# Default to numpy
_BACKEND = "numpy"

# Check environment variable
if os.environ.get("TINYTORCH_BACKEND", "").lower() == "jax":
    try:
        import jax
        import jax.numpy as np

        _BACKEND = "jax"
        # Pre-allocate to check device availability if needed, but keeping it lazy for now
    except ImportError:
        print(
            "Warning: TINYTORCH_BACKEND=jax requested but jax not found. Falling back to numpy.",
            file=sys.stderr,
        )
else:
    pass


def get_backend_name():
    """Return the name of the current backend ('numpy' or 'jax')."""
    return _BACKEND


def is_jax():
    """Return True if using JAX backend."""
    return _BACKEND == "jax"
