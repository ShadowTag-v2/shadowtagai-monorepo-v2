from src.pnkln.steel.backend import np
from src.pnkln.steel.tinytorch_activations import GELU
from src.pnkln.steel.tinytorch_attention import MultiHeadAttention
from src.pnkln.steel.tinytorch_embeddings import Embedding
from src.pnkln.steel.tinytorch_layers import Layer, Linear
from src.pnkln.steel.tinytorch_tensor import Tensor

# Constants for memory calculations
BYTES_PER_FLOAT32 = 4  # Standard float32 size in bytes
MB_TO_BYTES = 1024 * 1024  # Megabytes to bytes conversion


def create_causal_mask(seq_len: int) -> Tensor:
    """Create a causal (autoregressive) attention mask.

    This mask ensures that position i can only attend to positions j where j ≤ i.
    Essential for autoregressive language models like GPT.

    Args:
        seq_len: Length of the sequence

    Returns:
        Tensor of shape (1, seq_len, seq_len) with:
        - 1.0 for positions that CAN be attended to (lower triangle)
        - 0.0 for positions that CANNOT be attended to (upper triangle)

    """
    # Lower triangular matrix: 1 = can attend, 0 = cannot attend
    mask = np.tril(np.ones((seq_len, seq_len), dtype=np.float32))
    return Tensor(mask[np.newaxis, :, :])  # Add batch dimension


class LayerNorm:
    """Layer Normalization for transformer blocks.

    Normalizes across the feature dimension (last axis) for each sample independently,
    unlike batch normalization which normalizes across the batch dimension.
    """

    def __init__(self, normalized_shape, eps=1e-5):
        """Initialize LayerNorm with learnable parameters.

        Args:
            normalized_shape: Shape to normalize over (usually embed_dim)
            eps: Small epsilon for numerical stability

        """
        if isinstance(normalized_shape, int):
            normalized_shape = (normalized_shape,)

        self.normalized_shape = normalized_shape
        self.eps = eps

        # Learnable parameters: scale and shift
        self.gamma = Tensor(np.ones(normalized_shape), requires_grad=True)  # Scale parameter
        self.beta = Tensor(np.zeros(normalized_shape), requires_grad=True)  # Shift parameter

    def forward(self, x):
        """Apply layer normalization.

        MATHEMATICAL FORMULA:
        y = (x - μ) / σ * γ + β
        where μ = mean(x), σ = sqrt(var(x) + ε)
        """
        # Compute statistics across last dimension (features)
        mean = x.mean(axis=-1, keepdims=True)

        # Compute variance: E[(x - μ)²]
        # Use Tensor operations to preserve computation graph!
        diff = x - mean
        variance = (diff * diff).mean(axis=-1, keepdims=True)

        # Normalize - use Tensor operations to preserve gradients!
        # Add eps as a Tensor for proper gradient flow
        # eps_tensor = Tensor(np.array(self.eps), requires_grad=False)
        std = Tensor(np.sqrt(variance.data + self.eps), requires_grad=variance.requires_grad)
        normalized = (x - mean) / std

        # Apply learnable transformation
        output = normalized * self.gamma + self.beta
        return output

    def __call__(self, x):
        """Allows the layer norm to be called like a function."""
        return self.forward(x)

    def parameters(self):
        """Return learnable parameters."""
        return [self.gamma, self.beta]


class MLP:
    """Multi-Layer Perceptron (Feed-Forward Network) for transformer blocks.

    Standard pattern: Linear -> GELU -> Linear with expansion ratio of 4:1.
    This provides the non-linear transformation in each transformer block.
    """

    def __init__(self, embed_dim, hidden_dim=None, _dropout_prob=0.1):
        """Initialize MLP with two linear layers.

        Args:
            embed_dim: Embedding dimension
            hidden_dim: Hidden dimension (default 4x embed_dim)
            dropout_prob: Dropout probability (unused in inference-only version)

        """
        if hidden_dim is None:
            hidden_dim = 4 * embed_dim  # Standard 4x expansion

        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim

        # Two-layer feed-forward network
        self.linear1 = Linear(embed_dim, hidden_dim)
        self.gelu = GELU()  # Use GELU activation from activations module
        self.linear2 = Linear(hidden_dim, embed_dim)

    def forward(self, x):
        """Forward pass through MLP.

        COMPUTATION FLOW:
        x -> Linear -> GELU -> Linear -> output
        """
        # First linear layer with expansion
        hidden = self.linear1.forward(x)

        # GELU activation (YOUR activation from Module 03!)
        hidden = self.gelu.forward(hidden)

        # Second linear layer back to original size
        output = self.linear2.forward(hidden)

        return output

    def __call__(self, x):
        """Allows the MLP to be called like a function."""
        return self.forward(x)

    def parameters(self):
        """Return all learnable parameters."""
        params = []
        params.extend(self.linear1.parameters())
        params.extend(self.linear2.parameters())
        return params


class TransformerBlock:
    """Complete Transformer Block with self-attention, MLP, and residual connections.

    This is the core building block of GPT and other transformer models.
    Each block processes the input sequence and passes it to the next block.
    """

    def __init__(self, embed_dim, num_heads, mlp_ratio=4, _dropout_prob=0.1):
        """Initialize a complete transformer block.

        TRANSFORMER BLOCK ARCHITECTURE:
        x → LayerNorm → MultiHeadAttention → + (residual) →
            LayerNorm → MLP → + (residual) → output
        """
        self.embed_dim = embed_dim
        self.num_heads = num_heads

        # Multi-head self-attention
        self.attention = MultiHeadAttention(embed_dim, num_heads)

        # Layer normalizations (pre-norm architecture)
        self.ln1 = LayerNorm(embed_dim)  # Before attention
        self.ln2 = LayerNorm(embed_dim)  # Before MLP

        # Feed-forward network
        hidden_dim = int(embed_dim * mlp_ratio)
        self.mlp = MLP(embed_dim, hidden_dim)

    def forward(self, x, mask=None):
        """Forward pass through transformer block.

        COMPUTATION FLOW:
        x → ln1 → attention → + x → ln2 → mlp → + → output
        """
        # First sub-layer: Multi-head self-attention with residual connection
        # Pre-norm: LayerNorm before attention
        normed1 = self.ln1.forward(x)
        # Self-attention: query, key, value are all the same (normed1)
        attention_out = self.attention.forward(normed1, mask)

        # Residual connection
        x = x + attention_out

        # Second sub-layer: MLP with residual connection
        # Pre-norm: LayerNorm before MLP
        normed2 = self.ln2.forward(x)
        mlp_out = self.mlp.forward(normed2)

        # Residual connection
        output = x + mlp_out

        return output

    def __call__(self, x, mask=None):
        """Allows the transformer block to be called like a function."""
        return self.forward(x, mask)

    def parameters(self):
        """Return all learnable parameters."""
        params = []
        params.extend(self.attention.parameters())
        params.extend(self.ln1.parameters())
        params.extend(self.ln2.parameters())
        params.extend(self.mlp.parameters())
        return params


class GeminiMini(Layer):
    """Complete Gemini-Style Transformer model (Mini/Educational).

    This combines embeddings, positional encoding, multiple transformer blocks,
    and a language modeling head for text generation.
    """

    def __init__(self, vocab_size, embed_dim, num_layers, num_heads, max_seq_len=1024):
        """Initialize complete Gemini-Mini model.

        ARCHITECTURE:
        tokens → embedding → + pos_embedding →
                transformer_blocks → layer_norm → lm_head → logits
        """
        super().__init__()
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.max_seq_len = max_seq_len

        # Token and positional embeddings
        self.token_embedding = Embedding(vocab_size, embed_dim)
        self.position_embedding = Embedding(max_seq_len, embed_dim)

        # Stack of transformer blocks
        self.blocks = []
        for _ in range(num_layers):
            block = TransformerBlock(embed_dim, num_heads)
            self.blocks.append(block)

        # Final layer normalization
        self.ln_f = LayerNorm(embed_dim)

        # Language modeling head (projects to vocabulary)
        self.lm_head = Linear(embed_dim, vocab_size, bias=False)

    def forward(self, tokens):
        """Forward pass through GPT model.

        COMPUTATION FLOW:
        tokens → embed + pos_embed → blocks → ln_f → lm_head → logits
        """
        _, seq_len = tokens.shape

        # Token embeddings
        token_emb = self.token_embedding.forward(tokens)

        # Positional embeddings
        positions = Tensor(np.arange(seq_len).reshape(1, seq_len))
        pos_emb = self.position_embedding.forward(positions)

        # Combine embeddings
        x = token_emb + pos_emb

        # Create causal mask for autoregressive generation
        mask = self._create_causal_mask(seq_len)

        # Pass through transformer blocks
        for block in self.blocks:
            x = block.forward(x, mask)

        # Final layer normalization
        x = self.ln_f.forward(x)

        # Language modeling head
        logits = self.lm_head.forward(x)

        return logits

    def __call__(self, tokens):
        """Allows the GPT model to be called like a function."""
        return self.forward(tokens)

    def _create_causal_mask(self, seq_len):
        """Create causal mask to prevent attending to future positions."""
        # Upper triangular matrix filled with -inf
        mask = np.triu(np.ones((seq_len, seq_len)) * -np.inf, k=1)
        return Tensor(mask)

    def generate(self, prompt_tokens, max_new_tokens=50, temperature=1.0):
        """Generate text autoregressively.

        Args:
            prompt_tokens: Initial token sequence
            max_new_tokens: Number of tokens to generate
            temperature: Sampling temperature (1.0 = normal, <1.0 = conservative, >1.0 = creative)

        """
        current_tokens = Tensor(prompt_tokens.data.copy())

        for _ in range(max_new_tokens):
            # Crop to max_seq_len if needed
            cond_tokens = current_tokens
            if current_tokens.data.shape[1] > self.max_seq_len:
                cond_tokens = Tensor(current_tokens.data[:, -self.max_seq_len :])

            logits = self.forward(cond_tokens)
            last_logits = logits.data[:, -1, :]
            scaled_logits = last_logits / temperature
            exp_logits = np.exp(scaled_logits - np.max(scaled_logits, axis=-1, keepdims=True))
            probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
            next_token = np.array([[np.random.choice(self.vocab_size, p=probs[0])]])
            current_tokens = Tensor(np.concatenate([current_tokens.data, next_token], axis=1))

        return current_tokens

    def parameters(self):
        """Return all learnable parameters."""
        params = []
        params.extend(self.token_embedding.parameters())
        params.extend(self.position_embedding.parameters())

        for block in self.blocks:
            params.extend(block.parameters())

        params.extend(self.ln_f.parameters())
        params.extend(self.lm_head.parameters())

        return params
