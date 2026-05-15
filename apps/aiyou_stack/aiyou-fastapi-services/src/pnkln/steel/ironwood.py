import os
import sys
from pathlib import Path

# --- Antigravity Ironwood Bridge ---
# Allows importing JAX/Flax/Gemma from flattened forks without pip install.

ANTIGRAVITY_ROOT = Path(os.path.expanduser("~/antigravity-flattened"))


def bootstrap_ironwood():
    """Injects forked repositories into sys.path to enable Ironwood stack."""
    # Priority paths for Ironwood Stack
    ironwood_paths = [
        ANTIGRAVITY_ROOT / "jax",
        ANTIGRAVITY_ROOT / "flax",
        ANTIGRAVITY_ROOT / "gemma",
        ANTIGRAVITY_ROOT / "genkit",  # Bonus
    ]

    injected = []
    for p in ironwood_paths:
        if p.exists() and str(p) not in sys.path:
            sys.path.insert(0, str(p))  # Insert at front to override installed versions
            injected.append(p.name)

    return injected


def verify_ironwood():
    """Attempts to import key modules and print their location."""
    injected = bootstrap_ironwood()
    print(f"Ironwood: Injected paths for {injected}")

    try:
        import jax

        print(f"✅ JAX: {jax.__version__} @ {os.path.dirname(jax.__file__)}")
    except ImportError as e:
        print(f"❌ JAX: Import Failed ({e})")

    try:
        import flax

        print(f"✅ Flax: {flax.__version__} @ {os.path.dirname(flax.__file__)}")
    except ImportError as e:
        print(f"❌ Flax: Import Failed ({e})")

    try:
        import gemma

        print(
            f"✅ Gemma: (Source) @ {os.path.dirname(gemma.__file__) if hasattr(gemma, '__file__') else 'Namespace/Unknown'}",
        )
    except ImportError as e:
        # Gemma repo structure might use 'gemma' folder inside, checking...
        print(f"⚠️ Gemma: Import Failed (might need internal path adjustment) ({e})")


if __name__ == "__main__":
    verify_ironwood()
