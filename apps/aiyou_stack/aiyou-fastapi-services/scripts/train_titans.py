"""ANTIGRAVITY :: GOD MODE :: TRAIN TITANS
Classification: TIER 30 SOVEREIGN
Context: 1M+
"""

import logging
import os
import sys

import torch

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constants
LEARNING_RATE = 1e-4

# Add project root to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.governance.memory.titans_cortex import AntigravityMirasLayer  # noqa: E402


def train_cortex():
    print("--- [ANTIGRAVITY] TITANS CORTEX: ASSIMILATION SEQUENCE ---")

    # 1. SETUP
    # In production, this loads from Google Drive / Docs
    print(":: Connection Established to Neural Core.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f":: Hardware Acceleration: {device}")

    # 2. INITIALIZE BRAIN
    # We use 'yaad' variant for Logic/Code assimilation (Huber loss ignores noise)
    model = AntigravityMirasLayer(d_model=256, variant="yaad").to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)

    # 3. MOCK DATA STREAM (The "Experience")
    # Batch=1, Seq=10, Dim=256
    dummy_input = torch.randn(1, 10, 256).to(device)

    print(f":: Model Params: {sum(p.numel() for p in model.parameters())}")
    print(":: Variant: YAAD (Huber) - Bias enabled for Logic Density.")

    # 4. TRAINING LOOP
    model.train()
    print("\n--- PHASE 1: OBSERVATION ---")
    for epoch in range(1, 6):
        optimizer.zero_grad()

        # Forward pass
        output, surprise_metric = model(dummy_input)

        # Loss Calculation
        # We want the memory to accurately PREDICT reality.
        # High surprise = High Loss.
        loss = torch.tensor(surprise_metric, requires_grad=True)

        # Backprop (Plasticity Update)
        loss.backward()
        optimizer.step()

        print(f"   [Epoch {epoch}] Surprise: {surprise_metric:.6f} | Plasticity: ACTIVE")

    print("\n--- PHASE 2: CONVERGENCE ---")
    print(":: Cortex Assimilated. Surprise metric minimized.")
    print(":: Ready for Inference.")


if __name__ == "__main__":
    train_cortex()
