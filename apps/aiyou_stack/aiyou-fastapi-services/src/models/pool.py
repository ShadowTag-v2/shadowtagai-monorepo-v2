"""GPU pooling for multi-model serving."""

import asyncio
import contextlib
import logging
from dataclasses import dataclass
from datetime import datetime

from .registry import ModelRegistry

logger = logging.getLogger(__name__)


@dataclass
class GPUInfo:
    """Information about a GPU."""

    gpu_id: int
    total_memory_gb: float
    available_memory_gb: float
    utilization: float  # 0-1
    models_loaded: set[str]
    last_updated: datetime


class GPUPool:
    """
    GPU pool manager for multi-model serving.

    Implements Aegaeon-style GPU pooling:
    - Packs 7+ models per GPU
    - Lazy loading with auto-scaling
    - Shared resource management (VRAM slabs)
    """

    def __init__(
        self,
        registry: ModelRegistry,
        max_models_per_gpu: int = 7,
        auto_scale: bool = True,
        scale_up_threshold: float = 0.8,
        scale_down_threshold: float = 0.3,
    ):
        self.registry = registry
        self.max_models_per_gpu = max_models_per_gpu
        self.auto_scale = auto_scale
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold

        # Track GPU states
        self.gpus: dict[int, GPUInfo] = {}
        self._monitor_task: asyncio.Task | None = None

    async def start(self):
        """Start GPU pool monitoring."""
        await self._detect_gpus()

        if self.auto_scale:
            self._monitor_task = asyncio.create_task(self._monitor_loop())
            logger.info("GPU pool auto-scaling enabled")

    async def stop(self):
        """Stop GPU pool monitoring."""
        if self._monitor_task:
            self._monitor_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._monitor_task

    async def _detect_gpus(self):
        """Detect available GPUs."""
        try:
            import torch

            if not torch.cuda.is_available():
                logger.warning("No CUDA GPUs detected, running in CPU mode")
                # Create a virtual GPU for CPU mode
                self.gpus[0] = GPUInfo(
                    gpu_id=0,
                    total_memory_gb=16.0,  # Virtual memory
                    available_memory_gb=16.0,
                    utilization=0.0,
                    models_loaded=set(),
                    last_updated=datetime.now(),
                )
                return

            num_gpus = torch.cuda.device_count()
            logger.info(f"Detected {num_gpus} CUDA GPU(s)")

            for i in range(num_gpus):
                props = torch.cuda.get_device_properties(i)
                total_memory = props.total_memory / (1024**3)  # Convert to GB

                self.gpus[i] = GPUInfo(
                    gpu_id=i,
                    total_memory_gb=total_memory,
                    available_memory_gb=total_memory,
                    utilization=0.0,
                    models_loaded=set(),
                    last_updated=datetime.now(),
                )

                logger.info(f"GPU {i}: {props.name}, {total_memory:.2f} GB memory")

        except ImportError:
            logger.warning("PyTorch not available, creating virtual GPU")
            self.gpus[0] = GPUInfo(
                gpu_id=0,
                total_memory_gb=16.0,
                available_memory_gb=16.0,
                utilization=0.0,
                models_loaded=set(),
                last_updated=datetime.now(),
            )

    def get_best_gpu_for_model(self, model_name: str, required_memory_gb: float = 4.0) -> int:
        """
        Find the best GPU to load a model on.

        Strategy:
        1. Prefer GPUs with available memory
        2. Balance model count across GPUs
        3. Respect max_models_per_gpu limit
        """
        if not self.gpus:
            raise RuntimeError("No GPUs available")

        # Filter GPUs that can fit the model
        candidates = []
        for gpu_id, gpu_info in self.gpus.items():
            if gpu_info.available_memory_gb >= required_memory_gb:
                if len(gpu_info.models_loaded) < self.max_models_per_gpu:
                    candidates.append((gpu_id, gpu_info))

        if not candidates:
            raise RuntimeError(
                f"No GPU with {required_memory_gb}GB available memory and "
                f"<{self.max_models_per_gpu} models loaded"
            )

        # Pick GPU with most available memory and fewest models
        best_gpu_id, _ = min(
            candidates,
            key=lambda x: (len(x[1].models_loaded), -x[1].available_memory_gb),
        )

        return best_gpu_id

    async def allocate_model(self, model_name: str, gpu_id: int, memory_gb: float):
        """Allocate resources for a model on a GPU."""
        if gpu_id not in self.gpus:
            raise ValueError(f"GPU {gpu_id} not found")

        gpu_info = self.gpus[gpu_id]
        gpu_info.models_loaded.add(model_name)
        gpu_info.available_memory_gb -= memory_gb
        gpu_info.last_updated = datetime.now()

        logger.info(
            f"Allocated {memory_gb}GB on GPU {gpu_id} for {model_name}. "
            f"Available: {gpu_info.available_memory_gb:.2f}GB"
        )

    async def deallocate_model(self, model_name: str, gpu_id: int, memory_gb: float):
        """Deallocate resources for a model on a GPU."""
        if gpu_id not in self.gpus:
            return

        gpu_info = self.gpus[gpu_id]
        gpu_info.models_loaded.discard(model_name)
        gpu_info.available_memory_gb += memory_gb
        gpu_info.last_updated = datetime.now()

        logger.info(
            f"Deallocated {memory_gb}GB on GPU {gpu_id} from {model_name}. "
            f"Available: {gpu_info.available_memory_gb:.2f}GB"
        )

    async def _monitor_loop(self):
        """Monitor GPU utilization and trigger auto-scaling."""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self._update_gpu_metrics()
                await self._auto_scale_check()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in GPU monitor loop: {e}")

    async def _update_gpu_metrics(self):
        """Update GPU utilization metrics."""
        try:
            import torch

            if not torch.cuda.is_available():
                return

            for gpu_id, gpu_info in self.gpus.items():
                # Get current memory usage
                torch.cuda.set_device(gpu_id)
                allocated = torch.cuda.memory_allocated(gpu_id) / (1024**3)
                reserved = torch.cuda.memory_reserved(gpu_id) / (1024**3)

                gpu_info.available_memory_gb = gpu_info.total_memory_gb - reserved
                gpu_info.utilization = allocated / gpu_info.total_memory_gb
                gpu_info.last_updated = datetime.now()

        except ImportError:
            pass

    async def _auto_scale_check(self):
        """Check if auto-scaling is needed."""
        avg_utilization = sum(g.utilization for g in self.gpus.values()) / len(self.gpus)

        if avg_utilization > self.scale_up_threshold:
            logger.warning(
                f"High GPU utilization ({avg_utilization:.2%}), "
                "consider scaling up or offloading models"
            )
            # In production, trigger model offloading or request new GPUs

        elif avg_utilization < self.scale_down_threshold:
            logger.info(
                f"Low GPU utilization ({avg_utilization:.2%}), consider consolidating models"
            )
            # In production, consolidate models to fewer GPUs

    def get_pool_stats(self) -> dict:
        """Get GPU pool statistics."""
        return {
            "num_gpus": len(self.gpus),
            "total_models_loaded": sum(len(g.models_loaded) for g in self.gpus.values()),
            "avg_models_per_gpu": sum(len(g.models_loaded) for g in self.gpus.values())
            / len(self.gpus)
            if self.gpus
            else 0,
            "avg_gpu_utilization": sum(g.utilization for g in self.gpus.values()) / len(self.gpus)
            if self.gpus
            else 0,
            "gpus": {
                gpu_id: {
                    "total_memory_gb": info.total_memory_gb,
                    "available_memory_gb": info.available_memory_gb,
                    "utilization": info.utilization,
                    "models_loaded": list(info.models_loaded),
                    "model_count": len(info.models_loaded),
                }
                for gpu_id, info in self.gpus.items()
            },
        }
