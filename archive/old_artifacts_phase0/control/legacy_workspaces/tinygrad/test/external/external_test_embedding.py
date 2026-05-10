from tinygrad.nn import Embedding
from tinygrad.tensor import Tensor

if __name__ == "__main__":
  vocab_size = 50257
  dim = 128
  test = Embedding(vocab_size, dim)
  ret = test(Tensor([[1, 2, 3]])).numpy()
