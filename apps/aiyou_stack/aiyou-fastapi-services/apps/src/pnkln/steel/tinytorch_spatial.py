import numpy as np

from src.pnkln.steel.tinytorch_autograd import Function
from src.pnkln.steel.tinytorch_tensor import Tensor


class Conv2dBackward(Function):
    def __init__(self, x, weight, bias, stride, padding, kernel_size, padded_shape):
        if bias is not None:
            super().__init__(x, weight, bias)
        else:
            super().__init__(x, weight)
        self.x = x
        self.weight = weight
        self.bias = bias
        self.stride = stride
        self.padding = padding
        self.kernel_size = kernel_size
        self.padded_shape = padded_shape

    def apply(self, grad_output):
        batch_size, out_channels, out_height, out_width = grad_output.shape
        _, in_channels, in_height, in_width = self.x.shape
        kernel_h, kernel_w = self.kernel_size

        if self.padding > 0:
            padded_input = np.pad(
                self.x.data,
                (
                    (0, 0),
                    (0, 0),
                    (self.padding, self.padding),
                    (self.padding, self.padding),
                ),
                mode="constant",
                constant_values=0,
            )
        else:
            padded_input = self.x.data

        grad_input_padded = np.zeros_like(padded_input)
        grad_weight = np.zeros_like(self.weight.data)
        grad_bias = np.zeros_like(self.bias.data) if self.bias is not None else None

        # Loop implementation for clarity (though slow)
        for b in range(batch_size):
            for out_ch in range(out_channels):
                for out_h in range(out_height):
                    for out_w in range(out_width):
                        in_h_start = out_h * self.stride
                        in_w_start = out_w * self.stride
                        grad_val = grad_output[b, out_ch, out_h, out_w]

                        for k_h in range(kernel_h):
                            for k_w in range(kernel_w):
                                for in_ch in range(in_channels):
                                    grad_weight[out_ch, in_ch, k_h, k_w] += (
                                        padded_input[b, in_ch, in_h_start + k_h, in_w_start + k_w]
                                        * grad_val
                                    )
                                    grad_input_padded[
                                        b, in_ch, in_h_start + k_h, in_w_start + k_w
                                    ] += self.weight.data[out_ch, in_ch, k_h, k_w] * grad_val

        if grad_bias is not None:
            grad_bias = grad_output.sum(axis=(0, 2, 3))

        if self.padding > 0:
            grad_input = grad_input_padded[
                :, :, self.padding : -self.padding, self.padding : -self.padding
            ]
        else:
            grad_input = grad_input_padded

        return grad_input, grad_weight, grad_bias


class Conv2d:
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0, bias=True):
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = (
            (kernel_size, kernel_size) if isinstance(kernel_size, int) else kernel_size
        )
        self.stride = stride
        self.padding = padding

        # He Init
        k_h, k_w = self.kernel_size
        fan_in = in_channels * k_h * k_w
        std = np.sqrt(2.0 / fan_in)

        self.weight = Tensor(
            np.random.normal(0, std, (out_channels, in_channels, k_h, k_w)),
            requires_grad=True,
        )
        self.bias = Tensor(np.zeros(out_channels), requires_grad=True) if bias else None

    def forward(self, x):
        if len(x.shape) != 4:
            raise ValueError(f"Expected 4D input, got {x.shape}")
        batch_size, in_channels, in_height, in_width = x.shape
        out_channels = self.out_channels
        k_h, k_w = self.kernel_size

        out_h = (in_height + 2 * self.padding - k_h) // self.stride + 1
        out_w = (in_width + 2 * self.padding - k_w) // self.stride + 1

        if self.padding > 0:
            padded = np.pad(
                x.data,
                (
                    (0, 0),
                    (0, 0),
                    (self.padding, self.padding),
                    (self.padding, self.padding),
                ),
                mode="constant",
            )
        else:
            padded = x.data

        output = np.zeros((batch_size, out_channels, out_h, out_w))

        # Simplified loop for semi-speed
        # Real impl would use im2col
        for b in range(batch_size):
            for out_ch in range(out_channels):
                for h in range(out_h):
                    for w in range(out_w):
                        h_start = h * self.stride
                        w_start = w * self.stride

                        # Vectorize over in_channels? No, stick to loops for fidelity to Module 09
                        patch = padded[b, :, h_start : h_start + k_h, w_start : w_start + k_w]
                        # weight: (out_ch, in_ch, kh, kw)
                        # patch: (in_ch, kh, kw)
                        output[b, out_ch, h, w] = np.sum(patch * self.weight.data[out_ch])

        if self.bias is not None:
            output += self.bias.data.reshape(1, -1, 1, 1)

        res = Tensor(output, requires_grad=(x.requires_grad or self.weight.requires_grad))
        if res.requires_grad:
            res._grad_fn = Conv2dBackward(
                x,
                self.weight,
                self.bias,
                self.stride,
                self.padding,
                self.kernel_size,
                padded.shape,
            )
        return res

    def parameters(self):
        return [self.weight, self.bias] if self.bias else [self.weight]

    def __call__(self, x):
        return self.forward(x)


class MaxPool2dBackward(Function):
    def __init__(self, x, kernel_size, stride, padding, output_shape):
        super().__init__(x)
        self.x = x
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        # We don't store max indices here for simplicity, reusing fwd pass logic or just implementing simplified version
        # The Module 09 impl re-finds maxes in backward. I'll do the same.

    def apply(self, grad_output):
        batch, ch, h, w = self.x.shape
        k_h, k_w = self.kernel_size

        if self.padding > 0:
            padded_input = np.pad(
                self.x.data,
                (
                    (0, 0),
                    (0, 0),
                    (self.padding, self.padding),
                    (self.padding, self.padding),
                ),
                mode="constant",
                constant_values=-np.inf,
            )
            grad_input_padded = np.zeros_like(padded_input)
        else:
            padded_input = self.x.data
            grad_input_padded = np.zeros_like(self.x.data)

        _, _, out_h, out_w = grad_output.shape

        for b in range(batch):
            for c in range(ch):
                for i in range(out_h):
                    for j in range(out_w):
                        h_start = i * self.stride
                        w_start = j * self.stride
                        patch = padded_input[b, c, h_start : h_start + k_h, w_start : w_start + k_w]
                        max_val = np.max(patch)
                        # Find argmax. If multiple, only first gets grad
                        idx = np.unravel_index(np.argmax(patch), patch.shape)
                        grad_input_padded[b, c, h_start + idx[0], w_start + idx[1]] += grad_output[
                            b, c, i, j
                        ]

        if self.padding > 0:
            grad_input = grad_input_padded[
                :, :, self.padding : -self.padding, self.padding : -self.padding
            ]
        else:
            grad_input = grad_input_padded
        return (grad_input,)


class MaxPool2d:
    def __init__(self, kernel_size, stride=None, padding=0):
        self.kernel_size = (
            (kernel_size, kernel_size) if isinstance(kernel_size, int) else kernel_size
        )
        self.stride = stride if stride is not None else self.kernel_size[0]
        self.padding = padding

    def forward(self, x):
        batch, ch, h, w = x.shape
        k_h, k_w = self.kernel_size
        out_h = (h + 2 * self.padding - k_h) // self.stride + 1
        out_w = (w + 2 * self.padding - k_w) // self.stride + 1

        if self.padding > 0:
            padded = np.pad(
                x.data,
                (
                    (0, 0),
                    (0, 0),
                    (self.padding, self.padding),
                    (self.padding, self.padding),
                ),
                mode="constant",
                constant_values=-np.inf,
            )
        else:
            padded = x.data

        output = np.zeros((batch, ch, out_h, out_w))

        for b in range(batch):
            for c in range(ch):
                for i in range(out_h):
                    for j in range(out_w):
                        h_start = i * self.stride
                        w_start = j * self.stride
                        output[b, c, i, j] = np.max(
                            padded[b, c, h_start : h_start + k_h, w_start : w_start + k_w]
                        )

        res = Tensor(output, requires_grad=x.requires_grad)
        if res.requires_grad:
            res._grad_fn = MaxPool2dBackward(
                x, self.kernel_size, self.stride, self.padding, output.shape
            )
        return res

    def parameters(self):
        return []

    def __call__(self, x):
        return self.forward(x)


class AvgPool2d:
    def __init__(self, kernel_size, stride=None, padding=0):
        self.kernel_size = (
            (kernel_size, kernel_size) if isinstance(kernel_size, int) else kernel_size
        )
        self.stride = stride if stride is not None else self.kernel_size[0]
        self.padding = padding

    def forward(self, x):
        batch, ch, h, w = x.shape
        k_h, k_w = self.kernel_size
        out_h = (h + 2 * self.padding - k_h) // self.stride + 1
        out_w = (w + 2 * self.padding - k_w) // self.stride + 1

        if self.padding > 0:
            padded = np.pad(
                x.data,
                (
                    (0, 0),
                    (0, 0),
                    (self.padding, self.padding),
                    (self.padding, self.padding),
                ),
                mode="constant",
            )
        else:
            padded = x.data

        output = np.zeros((batch, ch, out_h, out_w))

        for b in range(batch):
            for c in range(ch):
                for i in range(out_h):
                    for j in range(out_w):
                        h_start = i * self.stride
                        w_start = j * self.stride
                        output[b, c, i, j] = np.mean(
                            padded[b, c, h_start : h_start + k_h, w_start : w_start + k_w]
                        )

        res = Tensor(output, requires_grad=x.requires_grad)
        return res

    def parameters(self):
        return []

    def __call__(self, x):
        return self.forward(x)
