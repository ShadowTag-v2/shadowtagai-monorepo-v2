"""Ironwood Transformer Block
Architectural Equivalent to tinytorch_transformer.py but powered by JAX/Flax.
Optimized for Google Cloud TPU v5e/v6.

COMPATIBILITY:
- Uses 'flax.linen' for NN definition.
- Uses 'jax' for XLA compilation.
- Maps 1:1 to 'TransformerBlock' structure.
"""

from collections.abc import Callable
from typing import Any

# Import through Ironwood Bridge
import jax.numpy as jnp
from flax import linen as nn

# Type aliases
Array = Any
PRNGKey = Any
Shape = tuple[int, ...]
Dtype = Any


class MLP(nn.Module):
    """Ironwood Multi-Layer Perceptron.
    """

    hidden_dim: int
    out_dim: int
    dropout_rate: float = 0.1
    activation: Callable = nn.gelu

    @nn.compact
    def __call__(self, x, deterministic: bool = True):
        # 1. Linear Expansion
        x = nn.Dense(features=self.hidden_dim, use_bias=True)(x)
        # 2. Activation
        x = self.activation(x)
        # 3. Dropout
        x = nn.Dropout(rate=self.dropout_rate, deterministic=deterministic)(x)
        # 4. Linear Projection
        x = nn.Dense(features=self.out_dim, use_bias=True)(x)
        # 5. Dropout
        x = nn.Dropout(rate=self.dropout_rate, deterministic=deterministic)(x)
        return x


class IronwoodAttention(nn.Module):
    """Ironwood Multi-Head Self-Attention.
    """

    num_heads: int
    dtype: Dtype = jnp.float32
    head_dim: int | None = None
    dropout_rate: float = 0.1

    @nn.compact
    def __call__(self, x, mask=None, deterministic: bool = True):
        # Flax provides a robust MultiHeadDotProductAttention
        # We wrap it to match our 'tinytorch' signature if needed,
        # but pure Flax is preferred for TPU.

        # x shape: (batch, seq, feature)
        # Standard Self-Attention: q, k, v are all x
        return nn.SelfAttention(
            num_heads=self.num_heads,
            dtype=self.dtype,
            qkv_features=self.head_dim * self.num_heads if self.head_dim else None,
            dropout_rate=self.dropout_rate,
            deterministic=deterministic,
        )(x, mask=mask)


class IronwoodBlock(nn.Module):
    """Complete Ironwood Transformer Block (Flax).
    x -> LN -> Attn -> + -> LN -> MLP -> + -> Out
    """

    embed_dim: int
    num_heads: int
    mlp_ratio: int = 4
    dropout_rate: float = 0.1

    @nn.compact
    def __call__(self, x, mask=None, deterministic: bool = True):
        # Sublayer 1: Attention
        residual = x
        x = nn.LayerNorm()(x)
        x = IronwoodAttention(
            num_heads=self.num_heads,
            head_dim=self.embed_dim // self.num_heads,
            dropout_rate=self.dropout_rate,
        )(x, mask=mask, deterministic=deterministic)
        x = x + residual

        # Sublayer 2: MLP
        residual = x
        x = nn.LayerNorm()(x)
        x = MLP(
            hidden_dim=self.embed_dim * self.mlp_ratio,
            out_dim=self.embed_dim,
            dropout_rate=self.dropout_rate,
        )(x, deterministic=deterministic)
        x = x + residual

        return x


class IronwoodGemini(nn.Module):
    """Ironwood JAX/Flax Gemini-Style Model.
    """

    vocab_size: int
    embed_dim: int
    num_layers: int
    num_heads: int
    max_seq_len: int = 1024
    dropout_rate: float = 0.1

    @nn.compact
    def __call__(self, tokens, train: bool = False):
        deterministic = not train

        # 1. Embeddings
        # Token Embeddings
        token_embs = nn.Embed(
            num_embeddings=self.vocab_size,
            features=self.embed_dim,
            embedding_init=nn.initializers.normal(stddev=0.02),
        )(tokens)

        # Positional Embeddings
        # Create position indices: (batch, seq_len)
        batch_size, seq_len = tokens.shape
        positions = jnp.arange(0, seq_len)
        positions = jnp.broadcast_to(positions, (batch_size, seq_len))

        pos_embs = nn.Embed(
            num_embeddings=self.max_seq_len,
            features=self.embed_dim,
            embedding_init=nn.initializers.normal(stddev=0.02),
        )(positions)

        x = token_embs + pos_embs
        x = nn.Dropout(rate=self.dropout_rate, deterministic=deterministic)(x)

        # 2. Transformer Blocks
        # Create Causal Mask
        # Flax attention expects mask of shape (batch, heads, q_len, kv_len)
        # or (batch, 1, q_len, kv_len) for broadcasting.
        # Simple causal mask:
        mask = nn.make_causal_mask(tokens, dtype=bool)

        for _ in range(self.num_layers):
            x = IronwoodBlock(
                embed_dim=self.embed_dim, num_heads=self.num_heads, dropout_rate=self.dropout_rate,
            )(x, mask=mask, deterministic=deterministic)

        # 3. Final Norm
        x = nn.LayerNorm()(x)

        # 4. LM Head (Dense to vocab)
        logits = nn.Dense(features=self.vocab_size)(x)

        return logits
