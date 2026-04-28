# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import math

import numpy as np

from src.pnkln.steel.tinytorch_autograd import EmbeddingBackward
from src.pnkln.steel.tinytorch_tensor import Tensor


class Embedding:
    """Learnable embedding layer."""

    def __init__(self, vocab_size: int, embed_dim: int):
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim

        # Xavier initialization
        limit = math.sqrt(6.0 / (vocab_size + embed_dim))
        self.weight = Tensor(
            np.random.uniform(-limit, limit, (vocab_size, embed_dim)),
            requires_grad=True,
        )

    def forward(self, indices: Tensor) -> Tensor:
        if np.any(indices.data >= self.vocab_size) or np.any(indices.data < 0):
            raise ValueError("Index out of range")

        # Advanced indexing for lookup
        embedded = self.weight.data[indices.data.astype(int)]

        result = Tensor(embedded, requires_grad=self.weight.requires_grad)

        if result.requires_grad:
            result._grad_fn = EmbeddingBackward(self.weight, indices)

        return result

    def __call__(self, indices: Tensor) -> Tensor:
        return self.forward(indices)

    def parameters(self) -> list[Tensor]:
        return [self.weight]


class PositionalEncoding:
    """Learnable positional encoding."""

    def __init__(self, max_seq_len: int, embed_dim: int):
        self.max_seq_len = max_seq_len
        self.embed_dim = embed_dim

        limit = math.sqrt(2.0 / embed_dim)
        self.position_embeddings = Tensor(
            np.random.uniform(-limit, limit, (max_seq_len, embed_dim)),
            requires_grad=True,
        )

    def forward(self, x: Tensor) -> Tensor:
        batch_size, seq_len, embed_dim = x.shape

        if seq_len > self.max_seq_len:
            raise ValueError(f"Sequence length {seq_len} exceeds max {self.max_seq_len}")

        pos_embeddings = self.position_embeddings[:seq_len]  # (seq_len, embed_dim)

        # Broadcast add
        # x: (batch, seq, embed)
        # pos: (seq, embed) -> broadcast to (batch, seq, embed) in numpy/tensor
        # We need to reshape pos for proper broadcasting if implicit broadcasting fails
        # Assuming Tensor supports numpy-like broadcasting

        # Explicit reshape for safety
        pos_reshaped = pos_embeddings.data[np.newaxis, :, :]
        pos_tensor = Tensor(pos_reshaped, requires_grad=pos_embeddings.requires_grad)

        return x + pos_tensor

    def parameters(self) -> list[Tensor]:
        return [self.position_embeddings]

    def __call__(self, x: Tensor) -> Tensor:
        return self.forward(x)


def create_sinusoidal_embeddings(max_seq_len: int, embed_dim: int) -> Tensor:
    """Fixed sinusoidal positional encodings."""
    position = np.arange(max_seq_len, dtype=np.float32)[:, np.newaxis]
    div_term = np.exp(
        np.arange(0, embed_dim, 2, dtype=np.float32) * -(math.log(10000.0) / embed_dim),
    )

    pe = np.zeros((max_seq_len, embed_dim), dtype=np.float32)
    pe[:, 0::2] = np.sin(position * div_term)

    if embed_dim % 2 == 1:
        pe[:, 1::2] = np.cos(position * div_term[:-1])
    else:
        pe[:, 1::2] = np.cos(position * div_term)

    return Tensor(pe, requires_grad=False)


class EmbeddingLayer:
    """Complete embedding system."""

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int,
        max_seq_len: int = 512,
        pos_encoding: str = "learned",
        scale_embeddings: bool = False,
    ):
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.max_seq_len = max_seq_len
        self.pos_encoding_type = pos_encoding
        self.scale_embeddings = scale_embeddings

        self.token_embedding = Embedding(vocab_size, embed_dim)

        if pos_encoding == "learned":
            self.pos_encoding = PositionalEncoding(max_seq_len, embed_dim)
        elif pos_encoding == "sinusoidal":
            self.pos_encoding = create_sinusoidal_embeddings(max_seq_len, embed_dim)
        else:
            self.pos_encoding = None

    def forward(self, tokens: Tensor) -> Tensor:
        token_embeds = self.token_embedding.forward(tokens)

        if self.scale_embeddings:
            token_embeds = token_embeds * math.sqrt(self.embed_dim)

        if self.pos_encoding_type == "learned":
            output = self.pos_encoding.forward(token_embeds)
        elif self.pos_encoding_type == "sinusoidal":
            seq_len = token_embeds.shape[1]
            pos_emb = self.pos_encoding[:seq_len]
            pos_data = pos_emb.data[np.newaxis, :, :]
            pos_tensor = Tensor(pos_data, requires_grad=False)
            output = token_embeds + pos_tensor
        else:
            output = token_embeds

        return output

    def parameters(self) -> list[Tensor]:
        params = self.token_embedding.parameters()
        if self.pos_encoding_type == "learned":
            params.extend(self.pos_encoding.parameters())
        return params

    def __call__(self, tokens: Tensor) -> Tensor:
        return self.forward(tokens)
