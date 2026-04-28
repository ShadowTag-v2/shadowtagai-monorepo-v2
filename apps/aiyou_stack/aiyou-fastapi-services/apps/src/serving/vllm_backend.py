# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""vLLM backend for efficient LLM serving."""

import asyncio
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GenerationRequest:
    """Request for text generation."""

    prompt: str
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    stream: bool = False
    stop: list[str] | None = None


@dataclass
class GenerationResponse:
    """Response from text generation."""

    text: str
    tokens: int
    finish_reason: str
    latency_ms: float


class VLLMBackend:
    """vLLM backend for high-throughput LLM serving.

    Provides 2-4x faster inference than HuggingFace Transformers
    through continuous batching and optimized attention kernels.
    """

    def __init__(
        self,
        model_name: str,
        model_path: str,
        gpu_id: int = 0,
        max_model_len: int = 4096,
        gpu_memory_utilization: float = 0.85,
        tensor_parallel_size: int = 1,
        enable_prefix_caching: bool = True,
        enable_chunked_prefill: bool = True,
        trust_remote_code: bool = True,
        dtype: str = "auto",
    ):
        self.model_name = model_name
        self.model_path = model_path
        self.gpu_id = gpu_id
        self.max_model_len = max_model_len

        self.config = {
            "model": model_path,
            "gpu_memory_utilization": gpu_memory_utilization,
            "tensor_parallel_size": tensor_parallel_size,
            "max_model_len": max_model_len,
            "trust_remote_code": trust_remote_code,
            "dtype": dtype,
        }

        # vLLM optimizations
        if enable_prefix_caching:
            self.config["enable_prefix_caching"] = True

        if enable_chunked_prefill:
            self.config["enable_chunked_prefill"] = True

        self.engine = None
        self.tokenizer = None
        self._loaded = False

    async def load(self):
        """Load the vLLM engine."""
        try:
            from transformers import AutoTokenizer
            from vllm import AsyncLLMEngine
            from vllm.engine.arg_utils import AsyncEngineArgs

            logger.info(f"Loading vLLM engine for {self.model_name}...")

            # Create engine args
            engine_args = AsyncEngineArgs(**self.config)

            # Initialize engine
            self.engine = AsyncLLMEngine.from_engine_args(engine_args)

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=self.config.get("trust_remote_code", True),
            )

            self._loaded = True
            logger.info(f"✓ vLLM engine loaded for {self.model_name}")

        except ImportError as e:
            logger.error(f"vLLM not installed: {e}")
            logger.info("Falling back to mock backend for testing")
            self._loaded = True  # Mock mode
        except Exception as e:
            logger.error(f"Failed to load vLLM engine: {e}")
            raise

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text from a prompt."""
        if not self._loaded:
            raise RuntimeError("Backend not loaded. Call load() first.")

        import time

        start_time = time.time()

        # If vLLM is available, use it
        if self.engine:
            try:
                from vllm import SamplingParams

                sampling_params = SamplingParams(
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    stop=request.stop,
                )

                # Generate
                outputs = await self.engine.generate(
                    request.prompt,
                    sampling_params,
                    request_id=None,
                )

                # Extract result
                output = outputs[0]
                generated_text = output.outputs[0].text
                num_tokens = len(output.outputs[0].token_ids)
                finish_reason = output.outputs[0].finish_reason

                latency_ms = (time.time() - start_time) * 1000

                return GenerationResponse(
                    text=generated_text,
                    tokens=num_tokens,
                    finish_reason=finish_reason,
                    latency_ms=latency_ms,
                )

            except Exception as e:
                logger.error(f"vLLM generation error: {e}")
                raise

        # Mock response for testing without GPU
        else:
            await asyncio.sleep(0.1)  # Simulate processing
            latency_ms = (time.time() - start_time) * 1000

            mock_text = f"[Mock response from {self.model_name}] Generated text for: {request.prompt[:50]}..."

            return GenerationResponse(
                text=mock_text,
                tokens=request.max_tokens,
                finish_reason="length",
                latency_ms=latency_ms,
            )

    async def generate_stream(self, request: GenerationRequest) -> AsyncIterator[str]:
        """Generate text with streaming."""
        if not self._loaded:
            raise RuntimeError("Backend not loaded. Call load() first.")

        if self.engine:
            try:
                from vllm import SamplingParams

                sampling_params = SamplingParams(
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    stop=request.stop,
                )

                # Stream generation
                async for output in self.engine.generate(
                    request.prompt,
                    sampling_params,
                    request_id=None,
                ):
                    if output.outputs:
                        yield output.outputs[0].text

            except Exception as e:
                logger.error(f"vLLM streaming error: {e}")
                raise

        else:
            # Mock streaming
            words = f"Mock streaming response from {self.model_name}".split()
            for word in words:
                await asyncio.sleep(0.05)
                yield word + " "

    async def unload(self):
        """Unload the vLLM engine."""
        if self.engine:
            # vLLM cleanup
            try:
                # vLLM doesn't have explicit cleanup, rely on garbage collection
                self.engine = None
                self.tokenizer = None
                logger.info(f"Unloaded vLLM engine for {self.model_name}")
            except Exception as e:
                logger.error(f"Error unloading vLLM engine: {e}")

        self._loaded = False

    def is_loaded(self) -> bool:
        """Check if backend is loaded."""
        return self._loaded

    def get_info(self) -> dict:
        """Get backend information."""
        return {
            "model_name": self.model_name,
            "model_path": self.model_path,
            "gpu_id": self.gpu_id,
            "max_model_len": self.max_model_len,
            "loaded": self._loaded,
            "config": self.config,
        }
