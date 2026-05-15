"""Example client for ShadowTag-v2 LLM serving API.

Demonstrates how to use the multi-model serving endpoint with different routing strategies.
"""

import asyncio
import time

import httpx


class LLMClient:
    """Client for ShadowTag-v2 LLM API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)

    async def complete(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
        routing_strategy: str = "token_aware",
    ) -> dict:
        """Generate a completion.

        Args:
            prompt: Input prompt
            model: Specific model (None for auto-routing)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            routing_strategy: least_loaded, round_robin, or token_aware (Aegaeon-style)

        Returns:
            Completion response with text and metadata

        """
        request = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "routing_strategy": routing_strategy,
        }

        if model:
            request["model"] = model

        response = await self.client.post(
            f"{self.base_url}/v1/completions",
            json=request,
        )
        response.raise_for_status()

        return response.json()

    async def list_models(self) -> dict:
        """List available models."""
        response = await self.client.get(f"{self.base_url}/v1/models")
        response.raise_for_status()
        return response.json()

    async def get_stats(self) -> dict:
        """Get system statistics."""
        response = await self.client.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close the client."""
        await self.client.aclose()


async def example_basic_completion():
    """Example: Basic completion with auto-routing."""
    print("\n=== Example 1: Basic Completion ===")

    client = LLMClient()

    try:
        response = await client.complete(
            prompt="Explain how Aegaeon achieves 82% GPU savings:",
            max_tokens=256,
            temperature=0.7,
            routing_strategy="token_aware",
        )

        print(f"Model: {response['model']}")
        print(f"Tokens: {response['tokens']}")
        print(f"Latency: {response['latency_ms']:.2f}ms")
        print(f"Routing: {response['routing']}")
        print(f"\nGenerated text:\n{response['text']}")

    finally:
        await client.close()


async def example_specific_model():
    """Example: Request specific model."""
    print("\n=== Example 2: Specific Model ===")

    client = LLMClient()

    try:
        response = await client.complete(
            prompt="What is DeepSeek Sparse Attention?",
            model="deepseek-v3.2-exp",
            max_tokens=200,
        )

        print("Requested model: deepseek-v3.2-exp")
        print(f"Actual model: {response['model']}")
        print(f"Response: {response['text'][:200]}...")

    finally:
        await client.close()


async def example_routing_strategies():
    """Example: Compare routing strategies."""
    print("\n=== Example 3: Routing Strategies ===")

    client = LLMClient()
    prompt = "Compare vLLM and Hugging Face Transformers performance:"

    strategies = ["least_loaded", "round_robin", "token_aware"]

    try:
        for strategy in strategies:
            start = time.time()

            response = await client.complete(
                prompt=prompt,
                max_tokens=100,
                routing_strategy=strategy,
            )

            elapsed = (time.time() - start) * 1000

            print(f"\n{strategy}:")
            print(f"  Model: {response['model']}")
            print(f"  Routing reason: {response['routing']['reason']}")
            print(f"  GPU: {response['routing']['gpu_id']}")
            print(f"  Total latency: {elapsed:.2f}ms")

    finally:
        await client.close()


async def example_concurrent_requests():
    """Example: Concurrent requests to test pooling."""
    print("\n=== Example 4: Concurrent Requests (GPU Pooling Test) ===")

    client = LLMClient()

    prompts = [
        "What is vLLM?",
        "Explain Ray Serve",
        "What is DeepSeek-OCR?",
        "How does token-level scheduling work?",
        "What is GPU pooling?",
    ]

    try:
        tasks = [
            client.complete(prompt, max_tokens=100, routing_strategy="token_aware")
            for prompt in prompts
        ]

        start = time.time()
        responses = await asyncio.gather(*tasks)
        elapsed = (time.time() - start) * 1000

        print(f"Completed {len(prompts)} requests in {elapsed:.2f}ms")
        print(f"Average latency: {elapsed / len(prompts):.2f}ms")

        # Show model distribution
        model_counts = {}
        for resp in responses:
            model = resp["model"]
            model_counts[model] = model_counts.get(model, 0) + 1

        print("\nModel distribution:")
        for model, count in model_counts.items():
            print(f"  {model}: {count} requests")

    finally:
        await client.close()


async def example_stats():
    """Example: Get system statistics."""
    print("\n=== Example 5: System Statistics ===")

    client = LLMClient()

    try:
        stats = await client.get_stats()

        print("\nRegistry Stats:")
        reg = stats["registry"]
        print(f"  Total models: {reg['total_models']}")
        print(f"  Ready models: {reg['ready_models']}")
        print(f"  Total requests: {reg['total_requests']}")
        print(f"  Active requests: {reg['active_requests']}")
        print(f"  Avg GPU utilization: {reg['avg_gpu_utilization']:.2%}")

        print("\nGPU Pool Stats:")
        pool = stats["gpu_pool"]
        print(f"  GPUs: {pool['num_gpus']}")
        print(f"  Total models loaded: {pool['total_models_loaded']}")
        print(f"  Avg models/GPU: {pool['avg_models_per_gpu']:.2f}")
        print(f"  Avg GPU utilization: {pool['avg_gpu_utilization']:.2%}")

        print("\nPer-GPU breakdown:")
        for gpu_id, gpu_info in pool["gpus"].items():
            print(f"  GPU {gpu_id}:")
            print(f"    Models: {gpu_info['model_count']} ({', '.join(gpu_info['models_loaded'])})")
            print(
                f"    Memory: {gpu_info['available_memory_gb']:.1f}GB / {gpu_info['total_memory_gb']:.1f}GB",
            )
            print(f"    Utilization: {gpu_info['utilization']:.2%}")

    finally:
        await client.close()


async def main():
    """Run all examples."""
    print("=" * 60)
    print("ShadowTag-v2 FastAPI Services - Client Examples")
    print("Multi-model LLM serving with Aegaeon-inspired pooling")
    print("=" * 60)

    # Run examples
    await example_basic_completion()
    await example_specific_model()
    await example_routing_strategies()
    await example_concurrent_requests()
    await example_stats()

    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
