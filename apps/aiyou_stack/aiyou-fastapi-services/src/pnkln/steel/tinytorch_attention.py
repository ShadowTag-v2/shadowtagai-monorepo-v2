# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import math

from src.pnkln.steel.tinytorch_activations import Softmax
from src.pnkln.steel.tinytorch_layers import Linear
from src.pnkln.steel.tinytorch_tensor import Tensor

# Constants for attention computation
MASK_VALUE = -1e9  # Large negative value used for attention masking (becomes ~0 after softmax)


def scaled_dot_product_attention(
    Q: Tensor,
    K: Tensor,
    V: Tensor,
    mask: Tensor | None = None,
) -> tuple[Tensor, Tensor]:
    """Compute scaled dot-product attention.

    This is the fundamental attention operation that powers all transformer models.
    We'll implement it with explicit loops first to show the O(n²) complexity.

    Args:
        Q: Query tensor of shape (batch_size, seq_len, d_model)
        K: Key tensor of shape (batch_size, seq_len, d_model)
        V: Value tensor of shape (batch_size, seq_len, d_model)
        mask: Optional causal mask, True=allow, False=mask (batch_size, seq_len, seq_len)

    Returns:
        output: Attended values (batch_size, seq_len, d_model)
        attention_weights: Attention matrix (batch_size, seq_len, seq_len)

    """
    # Step 1: Extract dimensions and validate
    # Note: Q, K, V can be 3D (batch, seq, dim) or 4D (batch, heads, seq, dim)
    # We use shape[-1] for d_model to handle both cases
    d_model = Q.shape[-1]

    # Step 2: Compute attention scores using matrix multiplication
    # Q: (..., seq_len, d_model)
    # K: (..., seq_len, d_model) -> K.T: (..., d_model, seq_len)
    # scores = Q @ K.T -> (..., seq_len, seq_len)

    # Transpose K for matrix multiplication
    # For 3D/4D tensors, transpose swaps the last two dimensions
    K_t = K.transpose(-2, -1)

    scores = Q.matmul(K_t)

    # Step 3: Scale by 1/√d_k for numerical stability
    scale_factor = 1.0 / math.sqrt(d_model)
    scores = scores * scale_factor

    # Step 4: Apply causal mask if provided
    if mask is not None:
        # Mask values of 0 indicate positions to mask out (set to -inf)
        # We use (1 - mask) * MASK_VALUE to add large negative values to masked positions
        # mask is expected to be 0 for masked, 1 for unmasked

        # Ensure mask is broadcastable
        mask_data = mask.data
        adder_mask = (1.0 - mask_data) * MASK_VALUE
        adder_mask_tensor = Tensor(adder_mask, requires_grad=False)
        scores = scores + adder_mask_tensor

    # Step 5: Apply softmax to get attention weights
    softmax = Softmax()
    attention_weights = softmax(scores, dim=-1)

    # Step 6: Apply values with attention weights
    # weights: (..., seq_len, seq_len)
    # V: (..., seq_len, d_model)
    # output = weights @ V -> (..., seq_len, d_model)
    output = attention_weights.matmul(V)

    return output, attention_weights


class MultiHeadAttention:
    """Multi-head attention mechanism.

    Runs multiple attention heads in parallel, each learning different relationships.
    This is the core component of transformer architectures.
    """

    def __init__(self, embed_dim: int, num_heads: int):
        """Initialize multi-head attention.

        Args:
            embed_dim: Embedding dimension (d_model)
            num_heads: Number of parallel attention heads

        """
        if embed_dim % num_heads != 0:
            raise ValueError(
                f"embed_dim ({embed_dim}) must be divisible by num_heads ({num_heads}).\n"
                f"  Issue: Multi-head attention splits embed_dim into num_heads heads.\n"
                f"  Fix: Choose embed_dim and num_heads such that embed_dim % num_heads == 0.\n"
                f"  Example: embed_dim=512, num_heads=8 works (512/8=64 per head).",
            )

        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads

        # Linear projections for queries, keys, values
        self.q_proj = Linear(embed_dim, embed_dim)
        self.k_proj = Linear(embed_dim, embed_dim)
        self.v_proj = Linear(embed_dim, embed_dim)

        # Output projection to mix information across heads
        self.out_proj = Linear(embed_dim, embed_dim)

    def forward(self, x: Tensor, mask: Tensor | None = None) -> Tensor:
        """Forward pass through multi-head attention.

        Args:
            x: Input tensor (batch_size, seq_len, embed_dim)
            mask: Optional attention mask (batch_size, seq_len, seq_len)

        Returns:
            output: Attended representation (batch_size, seq_len, embed_dim)

        """
        # Step 1: Extract dimensions
        batch_size, seq_len, embed_dim = x.shape
        if embed_dim != self.embed_dim:
            raise ValueError(
                f"Input dimension mismatch in MultiHeadAttention.forward().\n"
                f"  Expected: embed_dim={self.embed_dim} (set during initialization)\n"
                f"  Got: embed_dim={embed_dim} from input shape {x.shape}\n"
                f"  Fix: Ensure input tensor's last dimension matches the embed_dim used when creating MultiHeadAttention.",
            )

        # Step 2: Project to Q, K, V
        Q = self.q_proj.forward(x)  # (batch, seq, embed_dim)
        K = self.k_proj.forward(x)
        V = self.v_proj.forward(x)

        # Step 3: Reshape to separate heads
        # From (batch, seq, embed_dim) to (batch, seq, num_heads, head_dim)
        Q = Q.reshape(batch_size, seq_len, self.num_heads, self.head_dim)
        K = K.reshape(batch_size, seq_len, self.num_heads, self.head_dim)
        V = V.reshape(batch_size, seq_len, self.num_heads, self.head_dim)

        # Step 4: Transpose to (batch, num_heads, seq, head_dim) for parallel processing
        Q = Q.transpose(1, 2)
        K = K.transpose(1, 2)
        V = V.transpose(1, 2)

        # Step 5: Apply attention
        # We can apply attention to all heads at once because scaled_dot_product_attention
        # supports broadcasting or 4D tensors if implemented correctly.

        # Reshape mask if necessary to broadcast over heads
        mask_reshaped = mask
        if mask is not None and len(mask.shape) == 3:
            # Add head dimension: (batch, seq, seq) -> (batch, 1, seq, seq)
            # This allows the mask to broadcast across all attention heads
            batch_size_mask, seq_len_mask, _ = mask.shape
            mask_data = mask.data.reshape(batch_size_mask, 1, seq_len_mask, seq_len_mask)
            mask_reshaped = Tensor(mask_data, requires_grad=False)

        attended, _ = scaled_dot_product_attention(Q, K, V, mask=mask_reshaped)

        # Step 6: Concatenate heads back together
        # Transpose back: (batch, num_heads, seq, head_dim) → (batch, seq, num_heads, head_dim)
        attended = attended.transpose(1, 2)

        # Reshape: (batch, seq, num_heads, head_dim) → (batch, seq, embed_dim)
        concat_output = attended.reshape(batch_size, seq_len, self.embed_dim)

        # Step 7: Apply output projection
        output = self.out_proj.forward(concat_output)

        return output

    def __call__(self, x: Tensor, mask: Tensor | None = None) -> Tensor:
        """Make MultiHeadAttention callable like attention(x)."""
        return self.forward(x, mask)

    def parameters(self) -> list[Tensor]:
        """Return all trainable parameters.

        Returns:
            List of all parameter tensors

        """
        params = []
        params.extend(self.q_proj.parameters())
        params.extend(self.k_proj.parameters())
        params.extend(self.v_proj.parameters())
        params.extend(self.out_proj.parameters())
        return params
