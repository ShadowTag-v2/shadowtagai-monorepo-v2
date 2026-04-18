import os
import sys

import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from src.pnkln.steel.tinytorch_data import DataLoader, Dataset
from src.pnkln.steel.tinytorch_losses import CrossEntropyLoss
from src.pnkln.steel.tinytorch_miras import Yaad
from src.pnkln.steel.tinytorch_optimizers import Adam
from src.pnkln.steel.tinytorch_tensor import Tensor
from src.pnkln.steel.tinytorch_tokenization import CharTokenizer

# Constants
SEQ_LEN = 64
BATCH_SIZE = 32
EMBED_DIM = 256
NUM_HEADS = 8  # Not used in simple MirasLayer, but kept for param parity
M_HIDDEN = 256  # Miras hidden dim
NUM_LAYERS = 6
LEARNING_RATE = 3e-4
EPOCHS = 1
MAX_ITERS = 500
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
        chunk = self.encoded[idx : idx + self.seq_len + 1]
        x = chunk[:-1]
        y = chunk[1:]
        return Tensor(np.array(x)), Tensor(np.array(y))


def train_miras():
    print("🔥 TinyTorch Miras Training: Yaad on Shakespeare 🎭")
    print("==================================================")

    # 1. Load Data
    if not os.path.exists(DATA_PATH):
        print(f"❌ Data file not found at {DATA_PATH}")
        return

    print(f"📚 Loading {DATA_PATH}...")
    with open(DATA_PATH) as f:
        text = f.read()

    # 2. Tokenize
    print("🔤 Building tokenizer...")
    tokenizer = CharTokenizer()
    tokenizer.build_vocab([text])
    vocab_size = tokenizer.vocab_size
    print(f"   Vocabulary size: {vocab_size}")

    # 3. Create Dataset
    demo_limit = 100000
    train_text = text[:demo_limit]
    val_text = text[demo_limit : demo_limit + 10000]

    train_dataset = CharDataset(train_text, SEQ_LEN, tokenizer)
    val_dataset = CharDataset(val_text, SEQ_LEN, tokenizer)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # 4. Initialize Model (Yaad)
    print("\n🏗️  Initializing Yaad Model...")
    model = Yaad(
        vocab_size=vocab_size,
        embed_dim=EMBED_DIM,
        hidden_dim=M_HIDDEN,
        num_layers=NUM_LAYERS,
        max_seq_len=SEQ_LEN,
    )

    print(f"   Parameters: {sum(p.size for p in model.parameters()):,}")

    # 5. Setup Training
    optimizer = Adam(model.parameters(), lr=LEARNING_RATE)
    loss_fn = CrossEntropyLoss()

    # 6. Training Loop
    print("\n🚀 Starting Training...")

    for epoch in range(EPOCHS):
        print(f"\nEpoch {epoch + 1}/{EPOCHS}")

        model.training = True
        total_loss = 0

        dataloader_iter = iter(train_loader)
        for i in range(MAX_ITERS):
            try:
                inputs, targets = next(dataloader_iter)
            except StopIteration:
                break

            outputs = model(inputs)  # (B, S, V)

            B, S, V = outputs.shape
            flat_outputs = Tensor(
                outputs.data.reshape(B * S, V),
                requires_grad=outputs.requires_grad,
            )
            flat_targets = Tensor(targets.data.flatten())

            loss = loss_fn(flat_outputs, flat_targets)

            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            total_loss += loss.data[0]

            if i % 10 == 0:
                print(f"   Step {i}/{MAX_ITERS} | Loss: {loss.data[0]:.4f}", end="\r")

        print(f"\n   Epoch {epoch + 1} Complete | Average Loss: {total_loss / MAX_ITERS:.4f}")

        # 7. Generation Demo
        print("\n✨ Generating Text...")
        context_str = "To be or not to be"
        context_ids = tokenizer.encode(context_str)
        context_tensor = Tensor(np.array([context_ids]))

        model.training = False
        generated = model.generate(context_tensor, max_new_tokens=200, temperature=0.8)

        gen_ids = generated.data[0].astype(int).tolist()
        gen_text = tokenizer.decode(gen_ids)

        print("-" * 50)
        print(gen_text)
        print("-" * 50)


if __name__ == "__main__":
    train_miras()
