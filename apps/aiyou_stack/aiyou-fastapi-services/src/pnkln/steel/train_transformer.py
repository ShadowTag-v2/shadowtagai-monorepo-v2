import os
import sys

import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.pnkln.steel.tinytorch_data import DataLoader, Dataset
from src.pnkln.steel.tinytorch_losses import CrossEntropyLoss
from src.pnkln.steel.tinytorch_optimizers import Adam
from src.pnkln.steel.tinytorch_tensor import Tensor
from src.pnkln.steel.tinytorch_tokenization import CharTokenizer
from src.pnkln.steel.tinytorch_training import Trainer
from src.pnkln.steel.tinytorch_transformer import GeminiMini

# Constants
SEQ_LEN = 64
BATCH_SIZE = 32
EMBED_DIM = 256
NUM_HEADS = 8
NUM_LAYERS = 6
LEARNING_RATE = 3e-4
EPOCHS = 1  # For demo purposes
MAX_ITERS = 500  # Limit iterations for demo speed
DATA_PATH = os.path.join(os.path.dirname(__file__), "tinyshakespeare.txt")


class CharDataset(Dataset):
    """Character-level dataset for autoregressive training."""

    def __init__(self, data: str, seq_len: int, tokenizer: CharTokenizer):
        self.data = data
        self.seq_len = seq_len
        self.tokenizer = tokenizer
        self.encoded = tokenizer.encode(data)

    def __len__(self) -> int:
        return len(self.encoded) - self.seq_len

    def __getitem__(self, idx: int) -> tuple[Tensor, Tensor]:
        # x: input sequence
        # y: target sequence (shifted by 1)
        chunk = self.encoded[idx : idx + self.seq_len + 1]
        x = chunk[:-1]
        y = chunk[1:]

        return Tensor(np.array(x)), Tensor(np.array(y))


def train_gpt():
    print("🔥 TinyTorch Training Demo: GPT on Shakespeare 🎭")
    print("==================================================")

    # 1. Load Data
    if not os.path.exists(DATA_PATH):
        print(f"❌ Data file not found at {DATA_PATH}")
        print(
            "Run: curl -o src/pnkln/steel/tinyshakespeare.txt https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"
        )
        return

    print(f"📚 Loading {DATA_PATH}...")
    with open(DATA_PATH) as f:
        text = f.read()

    print(f"   Total characters: {len(text):,}")

    # 2. Tokenize
    print("🔤 Building tokenizer...")
    tokenizer = CharTokenizer()
    tokenizer.build_vocab([text])
    vocab_size = tokenizer.vocab_size
    print(f"   Vocabulary size: {vocab_size}")
    print(f"   Chars: {''.join(tokenizer.vocab)}")

    # 3. Create Dataset & DataLoader
    # Use first 90% for train, rest for valid
    train_size = int(len(text) * 0.9)
    train_text = text[:train_size]
    val_text = text[train_size:]

    # Limit dataset size for this demo to ensure it finishes quickly
    # Use 100k chars for fast training demo
    demo_limit = 100000
    if len(train_text) > demo_limit:
        print(f"⚠️  Limiting training data to {demo_limit} chars for demo speed...")
        train_text = train_text[:demo_limit]

    train_dataset = CharDataset(train_text, SEQ_LEN, tokenizer)
    val_dataset = CharDataset(
        val_text[: demo_limit // 10], SEQ_LEN, tokenizer
    )  # Small validation set

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    print(f"   Training samples: {len(train_dataset):,}")
    print(f"   Validation samples: {len(val_dataset):,}")

    # 4. Initialize Model
    print("\n🏗️  Initializing GPT Model...")
    print(
        f"   Embed Dim: {EMBED_DIM}, Heads: {NUM_HEADS}, Layers: {NUM_LAYERS}, Seq Len: {SEQ_LEN}"
    )

    model = GeminiMini(
        vocab_size=vocab_size,
        embed_dim=EMBED_DIM,
        num_layers=NUM_LAYERS,
        num_heads=NUM_HEADS,
        max_seq_len=SEQ_LEN,
    )

    print(f"   Parameters: {sum(p.size for p in model.parameters()):,}")

    # 5. Setup Training
    optimizer = Adam(model.parameters(), lr=LEARNING_RATE)
    loss_fn = CrossEntropyLoss()

    Trainer(model, optimizer, loss_fn)

    # 6. Training Loop
    print("\n🚀 Starting Training...")

    for epoch in range(EPOCHS):
        print(f"\nEpoch {epoch + 1}/{EPOCHS}")

        # Train
        model.training = True
        total_loss = 0

        # Custom loop to control iterations for demo
        dataloader_iter = iter(train_loader)
        for i in range(MAX_ITERS):
            try:
                inputs, targets = next(dataloader_iter)
            except StopIteration:
                break

            # One-hot encode targets for CrossEntropyLoss if needed,
            # OR CrossEntropyLoss handles indices.
            # Checking tinytorch_losses.py: handles sparse indices if targets.shape is 1D?
            # Looking at CrossEntropyLoss code:
            # if len(targets.data.shape) > 1: target_indices = np.argmax...
            # else: target_indices = targets.data.astype(int)
            # Our targets from Dataset are (Batch, Seq).
            # Our logits are (Batch, Seq, Vocab).
            # We need to flatten them for the loss calculation because current CrossEntropyLoss
            # implementation likely expects (N, C) logits and (N,) targets.

            # Reshape inputs/targets for processing
            # Since TinyTorch CrossEntropyLoss typically expects (N, C) logits and (N,) targets:

            outputs = model(inputs)  # (B, S, V)

            B, S, V = outputs.shape
            flat_outputs = Tensor(
                outputs.data.reshape(B * S, V), requires_grad=outputs.requires_grad
            )
            flat_targets = Tensor(targets.data.flatten())

            # Manual training step since we needed reshaping logic not in generic Trainer
            loss = loss_fn(flat_outputs, flat_targets)

            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            total_loss += loss.data[0]

            if i % 10 == 0:
                print(f"   Step {i}/{MAX_ITERS} | Loss: {loss.data[0]:.4f}", end="\r")

        print(f"\n   Epoch {epoch + 1} Complete | Average Loss: {total_loss / MAX_ITERS:.4f}")

        # Simple Validation
        # (Skipping full validation loop for brevity in demo script)

        # 7. Generation Demo
        print("\n✨ Generating Text...")
        context_str = "To be or not to be"
        context_ids = tokenizer.encode(context_str)
        context_tensor = Tensor(np.array([context_ids]))

        model.training = False
        generated = model.generate(context_tensor, max_new_tokens=200, temperature=0.8)

        # Decode
        gen_ids = generated.data[0].astype(int).tolist()
        gen_text = tokenizer.decode(gen_ids)

        print("-" * 50)
        print(gen_text)
        print("-" * 50)


if __name__ == "__main__":
    train_gpt()
