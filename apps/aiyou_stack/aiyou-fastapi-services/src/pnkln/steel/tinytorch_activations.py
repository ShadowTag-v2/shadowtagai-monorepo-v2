import numpy as np

from src.pnkln.steel.tinytorch_tensor import Tensor

# Constants for numerical comparisons
TOLERANCE = 1e-10


class Sigmoid:
    """Sigmoid activation: σ(x) = 1/(1 + e^(-x))
    Maps any real number to (0, 1) range.
    """

    def parameters(self):
        return []

    def forward(self, x: Tensor) -> Tensor:
        # Clip to prevent overflow
        z = np.clip(x.data, -500, 500)
        result_data = np.zeros_like(z)

        # Positive values
        pos_mask = z >= 0
        result_data[pos_mask] = 1.0 / (1.0 + np.exp(-z[pos_mask]))

        # Negative values: stable computation
        neg_mask = z < 0
        exp_z = np.exp(z[neg_mask])
        result_data[neg_mask] = exp_z / (1.0 + exp_z)

        return Tensor(result_data)

    def __call__(self, x: Tensor) -> Tensor:
        return self.forward(x)


class ReLU:
    """ReLU activation: f(x) = max(0, x)
    Sets negative values to zero.
    """

    def parameters(self):
        return []

    def forward(self, x: Tensor) -> Tensor:
        result = np.maximum(0, x.data)
        return Tensor(result)

    def __call__(self, x: Tensor) -> Tensor:
        return self.forward(x)


class Tanh:
    """Tanh activation: f(x) = (e^x - e^(-x))/(e^x + e^(-x))
    Maps to (-1, 1).
    """

    def parameters(self):
        return []

    def forward(self, x: Tensor) -> Tensor:
        result = np.tanh(x.data)
        return Tensor(result)

    def __call__(self, x: Tensor) -> Tensor:
        return self.forward(x)


class GELU:
    """GELU activation: f(x) = x * Φ(x) ≈ x * Sigmoid(1.702 * x)
    Smooth approximation to ReLU.
    """

    def parameters(self):
        return []

    def forward(self, x: Tensor) -> Tensor:
        sigmoid_part = 1.0 / (1.0 + np.exp(-1.702 * x.data))
        result = x.data * sigmoid_part
        return Tensor(result)

    def __call__(self, x: Tensor) -> Tensor:
        return self.forward(x)


class Softmax:
    """Softmax activation: f(x_i) = e^(x_i) / Σ(e^(x_j))
    Converts vector to probability distribution.
    """

    def parameters(self):
        return []

    def forward(self, x: Tensor, dim: int = -1) -> Tensor:
        # Numerical stability: subtract max
        x_max_data = np.max(x.data, axis=dim, keepdims=True)
        # We manually compute shifted data to keep it clean (Tensor subtraction)
        x_shifted_data = x.data - x_max_data

        # Exponentials
        exp_data = np.exp(x_shifted_data)

        # Sum
        exp_sum_data = np.sum(exp_data, axis=dim, keepdims=True)

        # Normalize
        result_data = exp_data / exp_sum_data

        return Tensor(result_data)

    def __call__(self, x: Tensor, dim: int = -1) -> Tensor:
        return self.forward(x, dim)
