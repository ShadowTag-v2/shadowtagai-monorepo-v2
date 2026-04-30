import numpy as np

from src.pnkln.steel.tinytorch_tensor import Tensor


class MSELoss:
    def __call__(self, predictions: Tensor, targets: Tensor) -> Tensor:
        return self.forward(predictions, targets)

    def forward(self, predictions: Tensor, targets: Tensor) -> Tensor:
        diff = predictions - targets
        return (diff * diff).sum() / Tensor(np.array([predictions.data.size]))


class CrossEntropyLoss:
    def __call__(self, logits: Tensor, targets: Tensor) -> Tensor:
        return self.forward(logits, targets)

    def forward(self, logits: Tensor, targets: Tensor) -> Tensor:
        # Stable softmax
        x = logits.data
        b = x.max(axis=1, keepdims=True)
        exp_x = np.exp(x - b)
        probs = exp_x / exp_x.sum(axis=1, keepdims=True)

        # NLL
        N = x.shape[0]
        if len(targets.data.shape) > 1:  # One-hot
            # Assuming targets are one-hot
            target_indices = np.argmax(targets.data, axis=1)
        else:
            target_indices = targets.data.astype(int)

        confidences = probs[np.arange(N), target_indices]
        loss = -np.log(confidences + 1e-7).mean()
        return Tensor(np.array([loss]))
