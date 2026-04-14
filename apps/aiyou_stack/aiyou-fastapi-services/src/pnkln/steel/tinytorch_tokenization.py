from collections import Counter

import numpy as np

# Constants for memory calculations
KB_TO_BYTES = 1024  # Kilobytes to bytes conversion


class Tokenizer:
    """Base tokenizer class providing the interface for all tokenizers.

    This defines the contract that all tokenizers must follow:
    - encode(): text → list of token IDs
    - decode(): list of token IDs → text
    """

    def encode(self, text: str) -> list[int]:
        """Convert text to a list of token IDs."""
        raise NotImplementedError("Subclasses must implement encode()")

    def decode(self, tokens: list[int]) -> str:
        """Convert list of token IDs back to text."""
        raise NotImplementedError("Subclasses must implement decode()")


class CharTokenizer(Tokenizer):
    """Character-level tokenizer that treats each character as a separate token.
    """

    def __init__(self, vocab: list[str] | None = None):
        """Initialize character tokenizer."""
        if vocab is None:
            vocab = []

        # Add special unknown token
        self.vocab = ["<UNK>"] + vocab
        self.vocab_size = len(self.vocab)

        # Create bidirectional mappings
        self.char_to_id = {char: idx for idx, char in enumerate(self.vocab)}
        self.id_to_char = {idx: char for idx, char in enumerate(self.vocab)}

        # Store unknown token ID
        self.unk_id = 0

    def build_vocab(self, corpus: list[str]) -> None:
        """Build vocabulary from a corpus of text."""
        # Collect all unique characters
        all_chars = set()
        for text in corpus:
            all_chars.update(text)

        # Sort for consistent ordering
        unique_chars = sorted(list(all_chars))

        # Rebuild vocabulary with <UNK> token first
        self.vocab = ["<UNK>"] + unique_chars
        self.vocab_size = len(self.vocab)

        # Rebuild mappings
        self.char_to_id = {char: idx for idx, char in enumerate(self.vocab)}
        self.id_to_char = {idx: char for idx, char in enumerate(self.vocab)}

    def encode(self, text: str) -> list[int]:
        """Encode text to list of character IDs."""
        tokens = []
        for char in text:
            tokens.append(self.char_to_id.get(char, self.unk_id))
        return tokens

    def decode(self, tokens: list[int]) -> str:
        """Decode list of token IDs back to text."""
        chars = []
        for token_id in tokens:
            # Use unknown token for invalid IDs
            char = self.id_to_char.get(token_id, "<UNK>")
            chars.append(char)
        return "".join(chars)


class BPETokenizer(Tokenizer):
    """Byte Pair Encoding (BPE) tokenizer that learns subword units.
    """

    def __init__(self, vocab_size: int = 1000):
        """Initialize BPE tokenizer."""
        self.vocab_size = vocab_size
        self.vocab = []
        self.merges = []  # List of (pair, new_token) merges
        self.token_to_id = {}
        self.id_to_token = {}

    def _get_word_tokens(self, word: str) -> list[str]:
        """Convert word to list of characters with end-of-word marker."""
        if not word:
            return []

        tokens = list(word)
        tokens[-1] += "</w>"  # Mark end of word
        return tokens

    def _get_pairs(self, word_tokens: list[str]) -> set[tuple[str, str]]:
        """Get all adjacent pairs from word tokens."""
        pairs = set()
        for i in range(len(word_tokens) - 1):
            pairs.add((word_tokens[i], word_tokens[i + 1]))
        return pairs

    def train(self, corpus: list[str], vocab_size: int = None) -> None:
        """Train BPE on corpus to learn merge rules."""
        if vocab_size:
            self.vocab_size = vocab_size

        # Count word frequencies
        word_freq = Counter(corpus)

        # Initialize vocabulary with characters
        vocab = set()
        word_tokens = {}

        for word in word_freq:
            tokens = self._get_word_tokens(word)
            word_tokens[word] = tokens
            vocab.update(tokens)

        # Convert to sorted list for consistency
        self.vocab = sorted(list(vocab))

        # Add special tokens
        if "<UNK>" not in self.vocab:
            self.vocab = ["<UNK>"] + self.vocab

        # Learn merges
        self.merges = []

        while len(self.vocab) < self.vocab_size:
            # Count all pairs across all words
            pair_counts = Counter()

            for word, freq in word_freq.items():
                tokens = word_tokens[word]
                pairs = self._get_pairs(tokens)
                for pair in pairs:
                    pair_counts[pair] += freq

            if not pair_counts:
                break

            # Get most frequent pair
            best_pair = pair_counts.most_common(1)[0][0]

            # Merge this pair in all words
            for word in word_tokens:
                tokens = word_tokens[word]
                new_tokens = []
                i = 0
                while i < len(tokens):
                    if (
                        i < len(tokens) - 1
                        and tokens[i] == best_pair[0]
                        and tokens[i + 1] == best_pair[1]
                    ):
                        # Merge pair
                        new_tokens.append(best_pair[0] + best_pair[1])
                        i += 2
                    else:
                        new_tokens.append(tokens[i])
                        i += 1
                word_tokens[word] = new_tokens

            # Add merged token to vocabulary
            merged_token = best_pair[0] + best_pair[1]
            self.vocab.append(merged_token)
            self.merges.append(best_pair)

        # Build final mappings
        self._build_mappings()

    def _build_mappings(self):
        """Build token-to-ID and ID-to-token mappings."""
        self.token_to_id = {token: idx for idx, token in enumerate(self.vocab)}
        self.id_to_token = {idx: token for idx, token in enumerate(self.vocab)}

    def _apply_merges(self, tokens: list[str]) -> list[str]:
        """Apply learned merge rules to token sequence."""
        if not self.merges:
            return tokens

        for merge_pair in self.merges:
            new_tokens = []
            i = 0
            while i < len(tokens):
                if (
                    i < len(tokens) - 1
                    and tokens[i] == merge_pair[0]
                    and tokens[i + 1] == merge_pair[1]
                ):
                    # Apply merge
                    new_tokens.append(merge_pair[0] + merge_pair[1])
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    i += 1
            tokens = new_tokens

        return tokens

    def encode(self, text: str) -> list[int]:
        """Encode text using BPE."""
        if not self.vocab:
            return []

        # Simple word splitting (could be more sophisticated)
        words = text.split()
        all_tokens = []

        for word in words:
            # Get character-level tokens
            word_tokens = self._get_word_tokens(word)

            # Apply BPE merges
            merged_tokens = self._apply_merges(word_tokens)

            all_tokens.extend(merged_tokens)

        # Convert to IDs
        token_ids = []
        for token in all_tokens:
            token_ids.append(self.token_to_id.get(token, 0))  # 0 = <UNK>

        return token_ids

    def decode(self, tokens: list[int]) -> str:
        """Decode token IDs back to text."""
        if not self.id_to_token:
            return ""

        # Convert IDs to tokens
        token_strings = []
        for token_id in tokens:
            token = self.id_to_token.get(token_id, "<UNK>")
            token_strings.append(token)

        # Join and clean up
        text = "".join(token_strings)

        # Replace end-of-word markers with spaces
        text = text.replace("</w>", " ")

        # Clean up extra spaces
        text = " ".join(text.split())

        return text


def create_tokenizer(
    strategy: str = "char", vocab_size: int = 1000, corpus: list[str] = None,
) -> Tokenizer:
    """Factory function to create and train tokenizers."""
    if strategy == "char":
        tokenizer = CharTokenizer()
        if corpus:
            tokenizer.build_vocab(corpus)
    elif strategy == "bpe":
        tokenizer = BPETokenizer(vocab_size=vocab_size)
        if corpus:
            tokenizer.train(corpus, vocab_size)
    else:
        raise ValueError(
            f"Unknown tokenization strategy: '{strategy}'.\n"
            f"  Available strategies: 'char', 'bpe'.\n"
            f"  Fix: Use 'char' for character-level or 'bpe' for byte-pair encoding tokenization.",
        )

    return tokenizer


def tokenize_dataset(
    texts: list[str], tokenizer: Tokenizer, max_length: int = None,
) -> list[list[int]]:
    """Tokenize a dataset with optional length limits."""
    tokenized = []
    for text in texts:
        tokens = tokenizer.encode(text)

        # Apply length limit
        if max_length and len(tokens) > max_length:
            tokens = tokens[:max_length]

        tokenized.append(tokens)

    return tokenized


def analyze_tokenization(texts: list[str], tokenizer: Tokenizer) -> dict[str, float]:
    """Analyze tokenization statistics."""
    all_tokens = []
    total_chars = 0

    for text in texts:
        tokens = tokenizer.encode(text)
        all_tokens.extend(tokens)
        total_chars += len(text)

    # Calculate statistics
    tokenized_lengths = [len(tokenizer.encode(text)) for text in texts]

    stats = {
        "vocab_size": tokenizer.vocab_size,
        "avg_sequence_length": np.mean(tokenized_lengths),
        "max_sequence_length": max(tokenized_lengths) if tokenized_lengths else 0,
        "total_tokens": len(all_tokens),
        "compression_ratio": total_chars / len(all_tokens) if all_tokens else 0,
        "unique_tokens": len(set(all_tokens)),
    }

    return stats
