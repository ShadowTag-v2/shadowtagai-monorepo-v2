import numpy as np

from src.pnkln.steel.tinytorch_tensor import Tensor


class Optimizer:
    def __init__(self, params: list):
        self.params = [p for p in params if p.requires_grad]
        self.step_count = 0

    def zero_grad(self):
        for p in self.params:
            p.zero_grad()

    def step(self):
        raise NotImplementedError


class SGD(Optimizer):
    def __init__(self, params: list, lr: float = 0.01, momentum: float = 0.0):
        super().__init__(params)
        self.lr = lr
        self.momentum = momentum
        self.momentum_buffers = [None] * len(self.params)

    def has_momentum(self):
        return self.momentum > 0

    def get_momentum_state(self):
        return [b.copy() if b is not None else None for b in self.momentum_buffers]

    def set_momentum_state(self, state):
        self.momentum_buffers = [b.copy() if b is not None else None for b in state]

    def step(self):
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            grad = p.grad.data if isinstance(p.grad, Tensor) else p.grad

            if self.momentum > 0:
                if self.momentum_buffers[i] is None:
                    self.momentum_buffers[i] = np.zeros_like(p.data)
                self.momentum_buffers[i] = self.momentum * self.momentum_buffers[i] + grad
                grad = self.momentum_buffers[i]

            p.data -= self.lr * grad
        self.step_count += 1


class Adam(Optimizer):
    def __init__(self, params: list, lr: float = 0.001, betas=(0.9, 0.999), eps=1e-8):
        super().__init__(params)
        self.lr = lr
        self.beta1, self.beta2 = betas
        self.eps = eps
        self.m = [np.zeros_like(p.data) for p in self.params]
        self.v = [np.zeros_like(p.data) for p in self.params]

    def step(self):
        self.step_count += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            grad = p.grad.data if isinstance(p.grad, Tensor) else p.grad

            self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * grad
            self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * (grad**2)

            m_hat = self.m[i] / (1 - self.beta1**self.step_count)
            v_hat = self.v[i] / (1 - self.beta2**self.step_count)

            p.data -= self.lr * m_hat / (np.sqrt(v_hat) + self.eps)
