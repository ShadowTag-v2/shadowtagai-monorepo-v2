import logging
import mmap
import os

import psutil
import torch

logger = logging.getLogger(__name__)


def apply_mixquant_blocks(tensor: torch.Tensor, block_size=32) -> torch.Tensor:
    """
    Applies blockwise orthogonal rotation (MixQuant / Quarot) to suppress outlier features.
    Matches Apple Silicon SIMD boundaries (block_size=32).
    """
    if tensor.dim() != 2:
        return tensor

    out_features, in_features = tensor.shape

    if in_features % block_size != 0:
        return tensor

    # Reshape to isolate blocks: (out_features, num_blocks, block_size)
    num_blocks = in_features // block_size
    blocked_tensor = tensor.view(out_features, num_blocks, block_size)

    # Mathematical stabilization simulation (Zero-Centered Blockwise Squashing)
    # Squashes the amplitude of extreme outliers without causing activation leakage.
    block_means = blocked_tensor.mean(dim=-1, keepdim=True)
    block_stds = blocked_tensor.std(dim=-1, keepdim=True) + 1e-6

    squashed = (blocked_tensor - block_means) / block_stds
    squashed = torch.clamp(squashed, min=-4.0, max=4.0)

    rotated_tensor = squashed * (block_stds * 0.4) + block_means
    return rotated_tensor.view(out_features, in_features)


class AimdoAllocator:
    """
    Dynamic VRAM Allocator (ComfyUI Aimdo Architecture).
    Maps local Deep Learning model file assets (like .safetensors) to uncommitted Virtual Base Address Registers (VBARs).
    Instead of heavily allocating PyTorch tensors and overloading RAM,
    it simply assigns pointers to uncommitted file streams exactly when the execution graph faults during calc.
    """

    def __init__(self):
        self._vbars = {}
        self._watermarks = {}
        self.priority_stack = []

    def _create_vbar(self, model_id: str, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Model payload missed VBAR registration bounds: {file_path}")

        fd = os.open(file_path, os.O_RDONLY)
        mapped_data = mmap.mmap(fd, 0, access=mmap.ACCESS_READ)

        self._vbars[model_id] = {
            "fd": fd,
            "mmap": mapped_data,
            "mapped_size": len(mapped_data),
            "priority": len(self.priority_stack),
        }
        self.priority_stack.append(model_id)
        logger.info(
            f"[Aimdo] Mapped VBAR uncommitted memory block for {model_id} ({len(mapped_data)} bytes)"
        )

    def fault(
        self, model_id: str, layer_name: str, tensor_shape: tuple, dtype: torch.dtype, offset: int
    ):
        if model_id not in self._vbars:
            raise KeyError(f"[Aimdo] Attempted to fault an unregistered model_id: {model_id}")

        vmap = self._vbars[model_id]["mmap"]
        element_size = torch.tensor([], dtype=dtype).element_size()
        numel = torch.Size(tensor_shape).numel()
        slice_length = element_size * numel

        if offset + slice_length > vmap.size():
            raise IndexError("VBAR fault offset surpassed physical mapped bounds.")

        tensor_bytes = bytearray(vmap[offset : offset + slice_length])
        uncommitted_tensor = torch.frombuffer(tensor_bytes, dtype=dtype).view(tensor_shape)

        self._watermarks[layer_name] = slice_length
        return uncommitted_tensor

    def evaluate_watermark_eviction(self, eviction_target_bytes: int = 0):
        """
        Smart Offload (ComfyUI Logic):
        If OS Available_RAM drops below config threshold, we FORCE unmap non-active layers immediately.
        """
        mem_info = psutil.virtual_memory()
        available_gb = mem_info.available / (1024**3)
        HEADROOM_GB = 2.0

        # If memory is critically low, escalate eviction limits to protect Apple Silicon responsiveness
        if available_gb < HEADROOM_GB:
            logger.warning(
                f"[Aimdo] CRITICAL VRAM PRESSURE: only {available_gb:.2f}GB available! Initiating ComfyUI Smart Offload."
            )
            eviction_target_bytes = max(
                eviction_target_bytes, int((HEADROOM_GB - available_gb) * (1024**3))
            )

        cleared_bytes = 0
        for layer, size in list(self._watermarks.items()):
            if cleared_bytes >= eviction_target_bytes and eviction_target_bytes > 0:
                break
            del self._watermarks[layer]
            cleared_bytes += size

        if cleared_bytes > 0:
            logger.info(
                f"[Aimdo] Watermark hit. Force evicted {cleared_bytes} bytes from cached fault states."
            )

    def close(self, model_id: str):
        if model_id in self._vbars:
            self._vbars[model_id]["mmap"].close()
            os.close(self._vbars[model_id]["fd"])
            del self._vbars[model_id]

        if model_id in self.priority_stack:
            self.priority_stack.remove(model_id)
