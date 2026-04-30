"""ANTIGRAVITY :: GOD MODE :: TITANS CORTEX
Classification: TIER 30 SOVEREIGN
Context: 1M+
"""

import logging

import torch
import torch.nn.functional as F
from torch import nn

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AntigravityMirasLayer(nn.Module):
    """The Shadowtag Cortex: A Neural Memory Module.
    Implements Titans 'MAC' (Memory as Context) with Miras Framework.

    References:
    - Titans: Learning to Memorize at Test Time (MAC architecture)
    - Miras: Attentional Bias for robust context (Yaad/Moneta)

    """

    def __init__(self, d_model=256, variant="yaad", p=3, delta=1.0, momentum=0.9):
        super().__init__()
        self.variant = variant
        self.p = p  # Moneta norm parameter (L-p norm)
        self.delta = delta  # Yaad Huber threshold
        self.momentum = momentum

        # 1. DEEP MEMORY (The "Hot" Core) - 2-Layer MLP
        # As per Titans paper: Shallow memory fails. We go deep.
        # This acts as the "Associative Memory" that stores context.
        self.memory_mlp = nn.Sequential(
            nn.Linear(d_model, d_model * 4),
            nn.GELU(),
            nn.Linear(d_model * 4, d_model),
        )

        # 2. THE SURPRISE GATE (Plasticity)
        # Determines learning rate per-token based on prediction error.
        # If the model can predict the input from memory, it ignores it.
        # If it is surprised, it opens the gate to learn.
        self.surprise_gate = nn.Linear(d_model, 1)

        # 3. LAYERNORM (Normalization)
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x, history=None):
        """x: [Batch, Seq, Dim] - The current input embedding
        history: [Batch, Seq, Dim] - The past context (Optional/Not used in base MAC)
        """
        # A. RETRIEVE (Memory Access / Reconstruction)
        # In a full Titans MAC, this interacts with a separate 'Memory' tensor.
        # Here, we model the memory weights themselves as the storage.
        # We try to 'reconstruct' the input from our internal knowledge.
        reconstruction = self.memory_mlp(x)

        # B. CALCULATE SURPRISE (The Gradient Signal)
        # We calculate the residual (error) between Reality (x) and Memory (reconstruction).

        if self.variant == "yaad":
            # Yaad: Robust to outliers (Huber Loss).
            # Useful for Code Logic where formatting noise should be ignored.
            surprise_loss = F.huber_loss(reconstruction, x, reduction="none", delta=self.delta)
        elif self.variant == "moneta":
            # Moneta: Strict configuration (L-p Norm).
            # Useful for Config/Secrets where every bit matters.
            surprise_loss = torch.norm(reconstruction - x, p=self.p, dim=-1, keepdim=True)
        else:
            # Standard MSE
            surprise_loss = F.mse_loss(reconstruction, x, reduction="none")

        # Reduce to scalar per token [Batch, Seq, 1]
        if self.variant != "moneta":  # Moneta already keeps dim
            surprise_scalar = surprise_loss.mean(dim=-1, keepdim=True)
        else:
            surprise_scalar = surprise_loss

        # C. UPDATE GATE (Plasticity)
        # Learns when to pay attention.
        # Sigmoid output: 0.0 (Closed/Ignore) to 1.0 (Open/Learn)
        gate = torch.sigmoid(self.surprise_gate(surprise_scalar))

        # D. RESIDUAL CONNECTION & MEMORY INTEGRATION
        # Output = Input + (Gate * MemoryAnswer)
        # This injects the "Memory Context" into the stream, weighted by relevance.
        output = self.norm(x + (gate * reconstruction))

        return output, surprise_scalar.mean().item()
