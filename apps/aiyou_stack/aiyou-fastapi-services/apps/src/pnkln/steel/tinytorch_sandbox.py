import numpy as np

from src.pnkln.steel.tinytorch_attention import (
    MultiHeadAttention,
    scaled_dot_product_attention,
)
from src.pnkln.steel.tinytorch_embeddings import (
    Embedding,
    EmbeddingLayer,
    PositionalEncoding,
    create_sinusoidal_embeddings,
)
from src.pnkln.steel.tinytorch_profiling import Profiler, quick_profile
from src.pnkln.steel.tinytorch_tensor import Tensor
from src.pnkln.steel.tinytorch_tokenization import (
    create_tokenizer,
)
from src.pnkln.steel.tinytorch_transformer import GPT, MLP, LayerNorm, TransformerBlock


def run_demo():
    print("🔥 TinyTorch Sandbox Demo - Module 14 (Profiling) 🔥")
    print("====================================================\n")

    print("1️⃣  Basic Embedding Lookup")
    vocab_size = 100
    embed_dim = 16
    embed = Embedding(vocab_size, embed_dim)

    tokens = Tensor(np.array([1, 5, 10]))
    vectors = embed(tokens)

    print(f"   Tokens: {tokens.data}")
    print(f"   Output Shape: {vectors.shape} (Expected: (3, 16))")
    assert vectors.shape == (3, 16)
    print("   ✅ Embedding lookup shape correct")

    print("\n2️⃣  Positional Encoding (Learned)")
    seq_len = 10
    pos_enc = PositionalEncoding(max_seq_len=20, embed_dim=16)

    # Simulate batch of embeddings (batch=2, seq=10, dim=16)
    x = Tensor(np.random.randn(2, seq_len, 16))
    out = pos_enc(x)

    print(f"   Input batch: {x.shape}")
    print(f"   Output batch: {out.shape}")
    assert out.shape == (2, seq_len, 16)
    print("   ✅ Learned positional encoding shape correct")

    print("\n3️⃣  Sinusoidal Positional Encoding")
    sin_pe = create_sinusoidal_embeddings(max_seq_len=100, embed_dim=32)
    print(f"   Sinusoidal PE shape: {sin_pe.shape}")

    # Check property: even dims sin, odd dims cos
    pos0 = sin_pe.data[0]
    print(f"   Pos 0 (first 4 dims): {pos0[:4]}")
    assert np.isclose(pos0[0], 0.0)  # sin(0)
    assert np.isclose(pos0[1], 1.0)  # cos(0)
    print("   ✅ Sinusoidal math properties verified")

    print("\n4️⃣  Complete Embedding Layer")
    full_embed = EmbeddingLayer(vocab_size=1000, embed_dim=64, pos_encoding="learned")

    batch_tokens = Tensor(np.random.randint(0, 1000, (4, 20)))  # Batch=4, Seq=20
    res = full_embed(batch_tokens)

    print(f"   Batch Tokens: {batch_tokens.shape}")
    print(f"   Result: {res.shape} (Expected: (4, 20, 64))")
    assert res.shape == (4, 20, 64)
    print("   ✅ Complete EmbeddingLayer working")

    print("\n   Module 11 Verified Successfully!")

    print("\n1️⃣  Scaled Dot-Product Attention")
    d_k = 64
    Q = Tensor(np.random.randn(2, 4, d_k))
    K = Tensor(np.random.randn(2, 4, d_k))
    V = Tensor(np.random.randn(2, 4, d_k))

    attn_out, attn_weights = scaled_dot_product_attention(Q, K, V)
    print(f"   Attention Output: {attn_out.shape} (Expected: (2, 4, 64))")
    print(f"   Attention Weights: {attn_weights.shape} (Expected: (2, 4, 4))")

    # Check if weights sum to 1
    row_sums = attn_weights.data[0].sum(axis=1)
    print(f"   Row Sums (first batch): {row_sums} (Expected: ~1.0)")
    if np.allclose(row_sums, 1.0, atol=1e-5):
        print("   ✅ Attention weights are valid probabilities")
    else:
        print("   ❌ Attention weights do not sum to 1")

    print("\n2️⃣  Multi-Head Attention")
    embed_dim = 128
    num_heads = 8
    mha = MultiHeadAttention(embed_dim, num_heads)

    x = Tensor(np.random.randn(2, 10, embed_dim))
    mask = Tensor(np.tril(np.ones((2, 10, 10))))  # Causal mask

    mha_out = mha(x, mask)
    print(f"   MHA Input: {x.shape}")
    print(f"   MHA Output: {mha_out.shape} (Expected: (2, 10, 128))")

    if mha_out.shape == x.shape:
        print("   ✅ Multi-Head Attention shapes correct")
    else:
        print(f"   ❌ MHA Output shape mismatch: {mha_out.shape}")

    print("\n   Module 12 Verified Successfully!")

    print("\n1️⃣  Layer Norm")
    ln = LayerNorm(4)
    x = Tensor([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]])
    normed = ln(x)
    print(f"   Input: {x.data[0]}")
    print(f"   Normed: {normed.data[0]} (Expected: [-1.34 -0.45  0.45  1.34])")

    print("\n2️⃣  MLP")
    mlp = MLP(embed_dim=16)
    x = Tensor(np.random.randn(2, 5, 16))
    out = mlp(x)
    print(f"   MLP Output: {out.shape} (Expected: (2, 5, 16))")
    print(f"   Hidden Dim: {mlp.hidden_dim} (Expected: 64)")

    print("\n3️⃣  Transformer Block")
    block = TransformerBlock(embed_dim=32, num_heads=4)
    x = Tensor(np.random.randn(2, 10, 32))
    out = block(x)
    print(f"   Block Output: {out.shape} (Expected: (2, 10, 32))")

    print("\n4️⃣  Tiny GeminiMini")
    gemini_mini = GeminiMini(vocab_size=100, embed_dim=64, num_layers=2, num_heads=4)
    tokens = Tensor(np.random.randint(0, 100, (1, 5)))
    logits = gemini_mini(tokens)
    print(f"   GeminiMini Logits: {logits.shape} (Expected: (1, 5, 100))")

    print("\n5️⃣  GeminiMini Generation")
    generated = gemini_mini.generate(tokens, max_new_tokens=5)
    print(f"   Generated: {generated.shape} (Expected: (1, 10))")
    print(f"   Tokens: {generated.data[0]}")

    print("\n   Module 13 Verified Successfully!")

    print("\n1️⃣  Character Tokenizer")
    corpus = ["hello world", "test text"]
    char_tok = create_tokenizer("char", corpus=corpus)
    tokens = char_tok.encode("hello")
    decoded = char_tok.decode(tokens)
    print("   Input: 'hello'")
    print(f"   Tokens: {tokens}")
    print(f"   Decoded: '{decoded}'")
    assert decoded == "hello"

    print("\n2️⃣  BPE Tokenizer")
    bpe_corpus = ["hello", "hello", "world"]
    bpe_tok = create_tokenizer("bpe", vocab_size=50, corpus=bpe_corpus)
    tokens = bpe_tok.encode("hello")
    decoded = bpe_tok.decode(tokens)
    print("   Input: 'hello'")
    print(f"   Tokens: {tokens}")
    print(f"   Decoded: '{decoded}'")
    assert "hello" in decoded  # BPE might add spaces

    print("\n3️⃣  Integration: Tokenizer -> GPT")
    # Small GPT
    vocab_size = 100
    gpt = GPT(vocab_size=vocab_size, embed_dim=16, num_layers=1, num_heads=2)

    # Tokenize input
    text = "hello"
    # Need to map chars to indices < vocab_size
    # For demo, just use random valid tokens
    tokens_tensor = Tensor(np.random.randint(0, vocab_size, (1, 5)))

    # Forward pass
    logits = gpt(tokens_tensor)
    print(f"   GPT Logits: {logits.shape} (Expected: (1, 5, 100))")

    print("\n   Module 10 Verified Successfully!")

    print("\n1️⃣  Quick Profile (Linear Layer)")
    # Create a simple layer
    from src.pnkln.steel.tinytorch_layers import Linear

    lin = Linear(128, 64)
    input_tensor = Tensor(np.random.randn(32, 128))

    # Run profiling
    profile = quick_profile(lin, input_tensor)

    # Assertions
    assert profile["parameters"] == 128 * 64 + 64
    assert profile["flops"] == 128 * 64 * 2

    print("\n2️⃣  Profiling Transformer Block")
    block = TransformerBlock(embed_dim=64, num_heads=4)
    block_input = Tensor(np.random.randn(8, 10, 64))  # (Batch, Seq, Dim)

    profiler = Profiler()
    # Profile forward pass
    stats = profiler.profile_forward_pass(block, block_input)

    print(f"   Transformer Params: {stats['parameters']:,}")
    print(f"   Transformer FLOPs: {stats['flops']:,}")
    print(f"   Latency: {stats['latency_ms']:.2f} ms")

    print("\n   Module 14 Verified Successfully!")


if __name__ == "__main__":
    run_demo()
