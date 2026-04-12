import numpy as np

from src.pnkln.steel.tinytorch_tensor import Tensor

# Constants
XAVIER_SCALE_FACTOR = 1.0
DROPOUT_MIN_PROB = 0.0
DROPOUT_MAX_PROB = 1.0


class Layer:
    """Base class for all neural network layers."""

    def __init__(self):
        self.training = True

    def forward(self, x: Tensor) -> Tensor:
        raise NotImplementedError("Subclasses must implement forward()")

    def __call__(self, x: Tensor, *args, **kwargs) -> Tensor:
        return self.forward(x, *args, **kwargs)

    def parameters(self):
        """Return list of trainable parameters (Tensors with requires_grad=True)."""
        return []

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class Linear(Layer):
    """
    Linear (fully connected) layer: y = xW + b
    """

    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        self.in_features = in_features
        self.out_features = out_features

        # Xavier Initialization
        scale = np.sqrt(XAVIER_SCALE_FACTOR / in_features)
        weight_data = np.random.randn(in_features, out_features) * scale
        self.weight = Tensor(weight_data, requires_grad=True)

        if bias:
            self.bias = Tensor(np.zeros(out_features), requires_grad=True)
        else:
            self.bias = None

    def forward(self, x: Tensor) -> Tensor:
        # y = xW
        output = x @ self.weight
        # + b
        if self.bias is not None:
            output = output + self.bias
        return output

    def parameters(self):
        params = [self.weight]
        if self.bias is not None:
            params.append(self.bias)
        return params

    def __repr__(self):
        return f"Linear(in_features={self.in_features}, out_features={self.out_features}, bias={self.bias is not None})"


class Dropout(Layer):
    """
    Dropout layer for regularization.
    """

    def __init__(self, p: float = 0.5):
        if not DROPOUT_MIN_PROB <= p <= DROPOUT_MAX_PROB:
            raise ValueError(f"Dropout probability must be between 0 and 1, got {p}")
        self.p = p

    def forward(self, x: Tensor, training: bool = True) -> Tensor:
        if not training or np.isclose(self.p, 0.0):
            return x
        if np.isclose(self.p, 1.0):
            return Tensor(np.zeros_like(x.data), requires_grad=x.requires_grad)

        # Create mask
        keep_prob = 1.0 - self.p
        mask = np.random.random(x.data.shape) < keep_prob

        # Scale
        scale = 1.0 / keep_prob

        # Apply mask and scale
        # We perform this on data for simplicity in this port, or could rely on Tensor ops
        # Relying on Tensor ops ensures gradients propagate correctly later
        mask_tensor = Tensor(mask.astype(np.float32), requires_grad=False)
        output = x * mask_tensor * Tensor([scale], requires_grad=False)

        return output

    def __call__(self, x: Tensor, training: bool = True) -> Tensor:
        return self.forward(x, training)

    def __repr__(self):
        return f"Dropout(p={self.p})"


class Sequential(Layer):
    """
    Container for sequential layers.
    """

    def __init__(self, *layers):
        if len(layers) == 1 and isinstance(layers[0], (list, tuple)):
            self.layers = list(layers[0])
        else:
            self.layers = list(layers)

    def forward(self, x: Tensor, training: bool = True) -> Tensor:
        for layer in self.layers:
            # Handle training arg if layer accepts it (like Dropout)
            x = layer(x, training=training) if isinstance(layer, Dropout) else layer(x)
        return x

    def __call__(self, x: Tensor, training: bool = True) -> Tensor:
        return self.forward(x, training=training)

    def parameters(self):
        params = []
        for layer in self.layers:
            params.extend(layer.parameters())
        return params

    def __repr__(self):
        return f"Sequential({', '.join(repr(l) for l in self.layers)})"
