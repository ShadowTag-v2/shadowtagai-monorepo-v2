#!/usr/bin/env python3
"""FastVLM Client: Apple Vision-Language Model Integration

Uses MLX-optimized FastVLM for on-device visual understanding.
Integrates with minions for visual task routing.

Features:
- 85x faster than LLaVA-OneVision
- On-device inference (Apple Silicon)
- No cloud dependency
- GPTRAM integration for caching

Part of PNKLN governance stack.
"""

import asyncio
import base64
import hashlib
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class VisionResult:
    """Result from FastVLM inference."""

    success: bool
    response: str
    image_hash: str
    latency_ms: float
    model: str
    metadata: dict[str, Any]


class FastVLMClient:
    """FastVLM inference client for Apple Silicon.

    Provides:
    - Image understanding and description
    - Visual QA
    - Document/screenshot parsing
    - Integration with minions routing
    - GPTRAM caching for repeated images

    Models:
    - fastvlm-0.5b: Fastest, 1.5GB memory, basic tasks
    - fastvlm-1.5b: Balanced, 3GB memory, recommended
    - fastvlm-7b: Most capable, 8GB memory, complex reasoning
    """

    VERSION = "1.0"

    MODEL_CONFIGS = {
        "fastvlm-0.5b": {
            "repo": "mlx-community/FastVLM-0.5B-MLX",
            "memory_gb": 1.5,
            "speed": "fastest",
            "description": "Basic image understanding",
        },
        "fastvlm-1.5b": {
            "repo": "mlx-community/FastVLM-1.5B-MLX",
            "memory_gb": 3.0,
            "speed": "fast",
            "description": "Balanced performance",
        },
        "fastvlm-7b": {
            "repo": "mlx-community/FastVLM-7B-MLX",
            "memory_gb": 8.0,
            "speed": "balanced",
            "description": "Complex visual reasoning",
        },
    }

    def __init__(
        self,
        model: str = "fastvlm-1.5b",
        minions_url: str = "http://localhost:8600",
        enable_caching: bool = True,
    ):
        """Initialize FastVLM client.

        Args:
            model: Model size (fastvlm-0.5b, fastvlm-1.5b, fastvlm-7b)
            minions_url: minions server URL
            enable_caching: Whether to cache results in GPTRAM

        """
        self.model_name = model
        self.config = self.MODEL_CONFIGS.get(model, self.MODEL_CONFIGS["fastvlm-1.5b"])
        self.fm_url = minions_url
        self.enable_caching = enable_caching

        # Model state (lazy loaded)
        self.model = None
        self.processor = None
        self._mlx_available = None
        self._generate = None
        self._apply_template = None
        self._load_config_fn = None

        # Stats tracking
        self.stats = {"images_processed": 0, "total_latency_ms": 0, "cache_hits": 0, "errors": 0}

        print(f"///▞ FASTVLM :: v{self.VERSION}")
        print(f"///▞ FASTVLM :: Model={model}, Memory={self.config['memory_gb']}GB")

    def _check_mlx_available(self) -> bool:
        """Check if MLX VLM is available."""
        if self._mlx_available is not None:
            return self._mlx_available

        try:
            import mlx_vlm

            self._mlx_available = True
        except ImportError:
            self._mlx_available = False
            print("///▞ FASTVLM :: mlx-vlm not installed")
            print("  Install with: pip install mlx-vlm")

        return self._mlx_available

    def _load_model(self):
        """Lazy load MLX model."""
        if self.model is not None:
            return True

        if not self._check_mlx_available():
            return False

        try:
            from mlx_vlm import generate, load
            from mlx_vlm.prompt_utils import apply_chat_template
            from mlx_vlm.utils import load_config

            print(f"///▞ FASTVLM :: Loading {self.model_name}...")
            self.model, self.processor = load(self.config["repo"])
            self._generate = generate
            self._apply_template = apply_chat_template
            self._load_config_fn = load_config

            print("///▞ FASTVLM :: Model loaded successfully")
            return True

        except Exception as e:
            print(f"///▞ FASTVLM :: Model load failed: {e}")
            self.stats["errors"] += 1
            return False

    def _image_to_base64(self, image_path: str) -> str:
        """Convert image file to base64."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def _hash_image(self, image_path: str) -> str:
        """Create hash of image for caching."""
        with open(image_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]

    def _hash_query(self, image_path: str, prompt: str) -> str:
        """Create hash for image+prompt combination."""
        content = f"{self._hash_image(image_path)}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    async def _check_cache(self, image_path: str, prompt: str) -> VisionResult | None:
        """Check GPTRAM cache for prior result."""
        if not self.enable_caching:
            return None

        try:
            from app.infrastructure.gptram import get_gptram

            gptram = get_gptram()

            query_hash = self._hash_query(image_path, prompt)
            cached = await gptram.get_prior_verdict(f"fastvlm:{query_hash}")

            if cached and "vision_response" in cached:
                self.stats["cache_hits"] += 1
                return VisionResult(
                    success=True,
                    response=cached["vision_response"],
                    image_hash=cached.get("image_hash", ""),
                    latency_ms=0,  # Cache hit
                    model=self.model_name,
                    metadata={"cached": True, "query_hash": query_hash},
                )
        except Exception:
            # Cache not available, continue without it
            pass

        return None

    async def _save_to_cache(self, image_path: str, prompt: str, result: VisionResult) -> None:
        """Save result to GPTRAM cache."""
        if not self.enable_caching or not result.success:
            return

        try:
            from app.infrastructure.gptram import get_gptram

            gptram = get_gptram()

            query_hash = self._hash_query(image_path, prompt)
            await gptram.save_verdict(
                f"fastvlm:{query_hash}",
                {
                    "vision_response": result.response,
                    "image_hash": result.image_hash,
                    "model": result.model,
                    "latency_ms": result.latency_ms,
                },
            )
        except Exception:
            # Cache save failed, continue anyway
            pass

    async def analyze(
        self,
        image_path: str,
        prompt: str = "Describe this image in detail.",
        max_tokens: int = 512,
        use_cache: bool = True,
    ) -> VisionResult:
        """Analyze an image with FastVLM.

        Args:
            image_path: Path to image file
            prompt: Question/instruction about the image
            max_tokens: Maximum response length
            use_cache: Whether to use GPTRAM cache

        Returns:
            VisionResult with analysis

        """
        start = time.time()

        # Validate image exists
        if not Path(image_path).exists():
            return VisionResult(
                success=False,
                response=f"Image not found: {image_path}",
                image_hash="",
                latency_ms=(time.time() - start) * 1000,
                model=self.model_name,
                metadata={"error": "image_not_found"},
            )

        # Check cache first
        if use_cache:
            cached = await self._check_cache(image_path, prompt)
            if cached:
                return cached

        # Load model if needed
        if not self._load_model():
            return VisionResult(
                success=False,
                response="FastVLM model not available. Install mlx-vlm.",
                image_hash="",
                latency_ms=(time.time() - start) * 1000,
                model=self.model_name,
                metadata={"error": "model_not_loaded"},
            )

        try:
            # Load config and apply template
            config = self._load_config_fn(self.config["repo"])
            formatted_prompt = self._apply_template(self.processor, config, prompt, num_images=1)

            # Generate response
            output = self._generate(
                self.model,
                self.processor,
                image_path,
                formatted_prompt,
                max_tokens=max_tokens,
                verbose=False,
            )

            latency_ms = (time.time() - start) * 1000

            self.stats["images_processed"] += 1
            self.stats["total_latency_ms"] += latency_ms

            result = VisionResult(
                success=True,
                response=output,
                image_hash=self._hash_image(image_path),
                latency_ms=latency_ms,
                model=self.model_name,
                metadata={"prompt": prompt, "max_tokens": max_tokens},
            )

            # Save to cache
            await self._save_to_cache(image_path, prompt, result)

            return result

        except Exception as e:
            self.stats["errors"] += 1
            return VisionResult(
                success=False,
                response=str(e),
                image_hash=self._hash_image(image_path) if Path(image_path).exists() else "",
                latency_ms=(time.time() - start) * 1000,
                model=self.model_name,
                metadata={"error": str(e)},
            )

    async def batch_analyze(
        self, image_paths: list[str], prompt: str = "Describe this image.", max_tokens: int = 256,
    ) -> list[VisionResult]:
        """Analyze multiple images.

        Args:
            image_paths: List of image file paths
            prompt: Question/instruction (same for all)
            max_tokens: Maximum response length per image

        Returns:
            List of VisionResult objects

        """
        results = []
        for path in image_paths:
            result = await self.analyze(path, prompt, max_tokens)
            results.append(result)
        return results

    async def route_visual_task(self, image_path: str, task: str) -> dict[str, Any]:
        """Route visual task through minions + FastVLM.

        1. FastVLM analyzes image
        2. Description + task sent to minions
        3. Combined result returned

        Args:
            image_path: Path to image
            task: Task to perform based on image

        Returns:
            Combined result from vision + minions

        """
        import requests

        # Step 1: Visual analysis
        vision_result = await self.analyze(
            image_path, f"Analyze this image for the following task: {task}",
        )

        if not vision_result.success:
            return {"success": False, "error": vision_result.response, "stage": "vision"}

        # Step 2: Route to minions with visual context
        combined_prompt = f"""
Visual Analysis:
{vision_result.response}

Task:
{task}

Based on the visual analysis above, complete the task.
"""

        try:
            response = requests.post(
                f"{self.fm_url}/task", json={"prompt": combined_prompt}, timeout=30,
            )
            fm_result = response.json()

            return {
                "success": True,
                "vision_analysis": vision_result.response,
                "task_result": fm_result.get("response", ""),
                "image_hash": vision_result.image_hash,
                "latency_ms": vision_result.latency_ms,
                "model": self.model_name,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stage": "minions",
                "vision_analysis": vision_result.response,
            }

    async def describe_screenshot(self, screenshot_path: str) -> VisionResult:
        """Specialized method for UI screenshot analysis.

        Args:
            screenshot_path: Path to screenshot

        Returns:
            VisionResult with UI description

        """
        prompt = """Analyze this UI screenshot. Describe:
1. The type of application/interface shown
2. Main UI components visible
3. Any text content
4. Current state (e.g., loading, error, success)
5. Notable UI elements or interactions available"""

        return await self.analyze(screenshot_path, prompt, max_tokens=512)

    async def extract_text(self, image_path: str) -> VisionResult:
        """Extract text from image (OCR-like functionality).

        Args:
            image_path: Path to image with text

        Returns:
            VisionResult with extracted text

        """
        prompt = "Extract and transcribe all visible text from this image. Preserve formatting and structure where possible."

        return await self.analyze(image_path, prompt, max_tokens=1024)

    async def analyze_document(self, document_path: str) -> VisionResult:
        """Analyze document image (invoice, contract, etc.).

        Args:
            document_path: Path to document image

        Returns:
            VisionResult with document analysis

        """
        prompt = """Analyze this document image. Extract:
1. Document type (invoice, contract, letter, etc.)
2. Key information (dates, amounts, names, addresses)
3. Important sections or clauses
4. Any signatures or stamps
5. Summary of the document's purpose"""

        return await self.analyze(document_path, prompt, max_tokens=1024)

    def get_stats(self) -> dict[str, Any]:
        """Get processing statistics."""
        return {
            "version": self.VERSION,
            "model": self.model_name,
            "model_loaded": self.model is not None,
            "memory_gb": self.config["memory_gb"],
            "images_processed": self.stats["images_processed"],
            "cache_hits": self.stats["cache_hits"],
            "avg_latency_ms": (
                self.stats["total_latency_ms"] / max(self.stats["images_processed"], 1)
            ),
            "errors": self.stats["errors"],
            "caching_enabled": self.enable_caching,
        }

    def health_check(self) -> dict[str, Any]:
        """Check FastVLM health."""
        return {
            "healthy": True,
            "mlx_available": self._check_mlx_available(),
            "model_loaded": self.model is not None,
            "model": self.model_name,
            "version": self.VERSION,
        }


# Convenience functions
def create_fastvlm(model: str = "fastvlm-1.5b") -> FastVLMClient:
    """Create FastVLM client instance."""
    return FastVLMClient(model=model)


def get_available_models() -> dict[str, dict]:
    """Get available FastVLM models."""
    return FastVLMClient.MODEL_CONFIGS


# Standalone test
if __name__ == "__main__":

    async def main():
        print("=" * 60)
        print("FastVLM Client Test")
        print("=" * 60)

        client = FastVLMClient(model="fastvlm-0.5b")

        # Show available models
        print("\nAvailable models:")
        for name, config in get_available_models().items():
            print(f"  {name}: {config['description']} ({config['memory_gb']}GB)")

        # Health check
        print("\nHealth check:")
        health = client.health_check()
        for key, value in health.items():
            print(f"  {key}: {value}")

        # Test with sample image
        test_image = "/tmp/test_image.png"

        if not Path(test_image).exists():
            print(f"\nNo test image at {test_image}")
            print("Create a test image or provide a different path.")

            # Try to find any image
            for ext in ["png", "jpg", "jpeg"]:
                for path in Path("/tmp").glob(f"*.{ext}"):
                    test_image = str(path)
                    print(f"Found: {test_image}")
                    break
                if Path(test_image).exists():
                    break

        if Path(test_image).exists():
            print(f"\nAnalyzing: {test_image}")
            result = await client.analyze(test_image, "What is shown in this image?")

            print(f"Success: {result.success}")
            if result.success:
                print(f"Response: {result.response[:200]}...")
            else:
                print(f"Error: {result.response}")
            print(f"Latency: {result.latency_ms:.2f}ms")

        # Show stats
        print("\nStats:")
        stats = client.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")

        print("\n" + "=" * 60)

    asyncio.run(main())
