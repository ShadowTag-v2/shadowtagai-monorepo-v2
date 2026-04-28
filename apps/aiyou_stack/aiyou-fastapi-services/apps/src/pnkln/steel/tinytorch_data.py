# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import random
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any

import numpy as np

from src.pnkln.steel.tinytorch_tensor import Tensor


class Dataset(ABC):
    """Abstract base class for all datasets."""

    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def __getitem__(self, idx: int) -> Any:
        pass


class TensorDataset(Dataset):
    """Dataset wrapping tensors."""

    def __init__(self, *tensors):
        assert len(tensors) > 0, "Must provide at least one tensor"
        self.tensors = tensors
        first_size = len(tensors[0].data)
        for i, tensor in enumerate(tensors):
            if len(tensor.data) != first_size:
                raise ValueError(
                    f"Tensor {i} size {len(tensor.data)} mismatch with first tensor {first_size}",
                )

    def __len__(self) -> int:
        return len(self.tensors[0].data)

    def __getitem__(self, idx: int) -> tuple[Tensor, ...]:
        if idx >= len(self) or idx < 0:
            raise IndexError(f"Index {idx} out of range")
        return tuple(Tensor(tensor.data[idx]) for tensor in self.tensors)


class DataLoader:
    """Data loader with batching and shuffling."""

    def __init__(self, dataset: Dataset, batch_size: int, shuffle: bool = False):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle

    def __len__(self) -> int:
        return (len(self.dataset) + self.batch_size - 1) // self.batch_size

    def __iter__(self) -> Iterator:
        indices = list(range(len(self.dataset)))
        if self.shuffle:
            random.shuffle(indices)

        for i in range(0, len(indices), self.batch_size):
            batch_indices = indices[i : i + self.batch_size]
            batch = [self.dataset[idx] for idx in batch_indices]
            yield self._collate_batch(batch)

    def _collate_batch(self, batch: list[tuple[Tensor, ...]]) -> tuple[Tensor, ...]:
        if not batch:
            return ()
        num_tensors = len(batch[0])
        batched_tensors = []
        for i in range(num_tensors):
            tensor_list = [sample[i].data for sample in batch]
            batched_data = np.stack(tensor_list, axis=0)
            batched_tensors.append(Tensor(batched_data))
        return tuple(batched_tensors)


class RandomHorizontalFlip:
    """Randomly flip images horizontally."""

    def __init__(self, p=0.5):
        self.p = p

    def __call__(self, x):
        if np.random.random() < self.p:
            if isinstance(x, Tensor):
                return Tensor(np.flip(x.data, axis=-1).copy())
            return np.flip(x, axis=-1).copy()
        return x


class RandomCrop:
    """Randomly crop image after padding."""

    def __init__(self, size, padding=4):
        self.size = (size, size) if isinstance(size, int) else size
        self.padding = padding

    def __call__(self, x):
        is_tensor = isinstance(x, Tensor)
        data = x.data if is_tensor else x
        target_h, target_w = self.size

        if len(data.shape) == 2:
            h, w = data.shape
            padded = np.pad(data, self.padding, mode="constant", constant_values=0)
            top = np.random.randint(0, 2 * self.padding + h - target_h + 1)
            left = np.random.randint(0, 2 * self.padding + w - target_w + 1)
            cropped = padded[top : top + target_h, left : left + target_w]
        elif len(data.shape) == 3:
            # Check for (C, H, W) vs (H, W, C). Simple check: C usually small
            if data.shape[0] <= 4:  # (C, H, W)
                c, h, w = data.shape
                padded = np.pad(
                    data,
                    (
                        (0, 0),
                        (self.padding, self.padding),
                        (self.padding, self.padding),
                    ),
                    mode="constant",
                )
                top = np.random.randint(0, 2 * self.padding + 1)
                left = np.random.randint(0, 2 * self.padding + 1)
                cropped = padded[:, top : top + target_h, left : left + target_w]
            else:  # (H, W, C)
                h, w, c = data.shape
                padded = np.pad(
                    data,
                    (
                        (self.padding, self.padding),
                        (self.padding, self.padding),
                        (0, 0),
                    ),
                    mode="constant",
                )
                top = np.random.randint(0, 2 * self.padding + 1)
                left = np.random.randint(0, 2 * self.padding + 1)
                cropped = padded[top : top + target_h, left : left + target_w, :]
        else:
            raise ValueError(f"Expected 2D or 3D input, got {data.shape}")

        return Tensor(cropped) if is_tensor else cropped


class Compose:
    """Compose multiple transforms."""

    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, x):
        for t in self.transforms:
            x = t(x)
        return x
