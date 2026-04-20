"""Multi-LLM Router - Pure Gemini Brain & Brawn Architecture

Routes requests to appropriate Gemini model based on task type:
- Brain (Planning/Reasoning): gemini-3.1-flash-lite-preview-thinking-exp
- Brawn (Coding/Execution): gemini-3.1-flash-lite-preview
- Grounding (Governance): gemini-3.1-flash-lite-preview

Target latencies:
- Planning: 2-5s
- Coding: 500ms-2s
- Quick queries: 200-500ms
"""

import asyncio
import logging
import math
import os
import time
from collections import Counter
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import google.generativeai as genai

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Available LLM providers."""

    GEMINI = "gemini"


class TaskType(Enum):
    """Task categories for routing."""

    PLANNING = "planning"  # Architecture, design docs -> Flash Thinking
    CODING = "coding"  # Bulk edits, file generation -> Flash 2.0
    QUICK_FIX = "quick_fix"  # Small fixes -> Flash 2.0
    REALTIME = "realtime"  # Social, current events -> Flash 2.0
    GOVERNANCE = "governance"  # Compliance checks -> Pro 1.5
    EMBEDDING = "embedding"  # Vector generation -> Text Gecko


@dataclass
class LLMRequest:
    """Request to an LLM."""

    prompt: str
    system_prompt: str | None = None
    task_type: TaskType = TaskType.CODING
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.9
    stream: bool = False
    stop_sequences: list[str] | None = None
    provider_override: LLMProvider | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """Response from an LLM."""

    text: str
    provider: LLMProvider
    model: str
    tokens_input: int
    tokens_output: int
    latency_ms: float
    cost_usd: float
    finish_reason: str
    metadata: dict[str, Any] = field(default_factory=dict)


class LLMRouter:
    """Routes LLM requests based on Pure Gemini architecture."""

    # Routing table: task_type -> preferred provider (Always Gemini now)
    ROUTING_TABLE = {
        TaskType.PLANNING: LLMProvider.GEMINI,
        TaskType.CODING: LLMProvider.GEMINI,
        TaskType.QUICK_FIX: LLMProvider.GEMINI,
        TaskType.REALTIME: LLMProvider.GEMINI,
        TaskType.GOVERNANCE: LLMProvider.GEMINI,
        TaskType.EMBEDDING: LLMProvider.GEMINI,
    }

    # Model configurations - Pure Gemini Stack
    MODEL_CONFIG = {
        LLMProvider.GEMINI: {
            "planning": "gemini-3.1-flash-lite-preview-thinking-exp",
            "coding": "gemini-3.1-flash-lite-preview",
            "quick": "gemini-3.1-flash-lite-preview",
            "governance": "gemini-3.1-flash-lite-preview",
            "default": "gemini-3.1-flash-lite-preview",
        },
    }

    # Pricing (USD per 1M tokens) - Updated for Gemini
    PRICING = {
        "gemini-3.1-flash-lite-preview": {"input": 0.075, "output": 0.30},
        "gemini-3.1-flash-lite-preview-thinking-exp": {"input": 0.075, "output": 0.30},
        "gemini-3.1-flash-lite-preview": {"input": 3.50, "output": 10.50},
    }

    # Ada-K: Entropy thresholds for adaptive routing
    ENTROPY_THRESHOLDS = {
        "low": 2.5,  # Single model fast path
        "medium": 4.0,  # Standard routing
        "high": 5.5,  # Multi-model consensus
    }

    def __init__(
        self,
        gemini_api_key: str | None = None,
        fallback_to_mock: bool = True,
    ):
        # API keys from env or params
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")

        self.fallback_to_mock = fallback_to_mock
        self._initialized = False
        self._available_providers: list[LLMProvider] = []

        # Clients
        self._gemini_models: dict[str, Any] = {}

        # Metrics
        self.request_count = 0
        self.total_cost_usd = 0.0
        self.latencies: list[float] = []

        # Ada-K metrics
        self.ada_k_distribution: dict[int, int] = dict.fromkeys(range(1, 9), 0)
        self.entropy_values: list[float] = []
        self.single_provider_count = 0
        self.multi_provider_count = 0

    async def initialize(self):
        """Initialize Gemini clients."""
        logger.info("Initializing Pure Gemini Router...")

        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                # Pre-load commonly used models
                for model_name in [
                    "gemini-3.1-flash-lite-preview",
                    "gemini-3.1-flash-lite-preview-thinking-exp",
                    "gemini-3.1-flash-lite-preview",
                ]:
                    try:
                        self._gemini_models[model_name] = genai.GenerativeModel(model_name)
                    except Exception as e:
                        logger.warning(f"Could not load {model_name}: {e}")

                self._available_providers.append(LLMProvider.GEMINI)
                logger.info(f"✓ Gemini initialized with {len(self._gemini_models)} models")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
        else:
            logger.warning("No GEMINI_API_KEY, Gemini provider unavailable")

        self._initialized = True
        logger.info("LLM Router ready (Pure Gemini Mode).")

    def _select_provider(self, request: LLMRequest) -> LLMProvider | None:
        """Select the best provider for a request (Always Gemini)."""
        if LLMProvider.GEMINI in self._available_providers:
            return LLMProvider.GEMINI

        if self.fallback_to_mock:
            logger.warning("No LLM providers available, using mock")
            return None
        raise RuntimeError("No LLM providers available")

    def _select_model(self, provider: LLMProvider, task_type: TaskType) -> str:
        """Select the best model for provider and task."""
        config = self.MODEL_CONFIG.get(provider, {})
        default = config.get("default", "gemini-3.1-flash-lite-preview")

        if task_type == TaskType.PLANNING:
            return config.get("planning", default)
        if task_type == TaskType.CODING:
            return config.get("coding", default)
        if task_type == TaskType.QUICK_FIX:
            return config.get("quick", default)
        if task_type == TaskType.GOVERNANCE:
            return config.get("governance", default)
        return default

    def _calculate_token_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of character distribution."""
        if not text:
            return 0.0

        text_lower = text.lower()
        counts = Counter(text_lower)
        total = len(text_lower)

        entropy = -sum(
            (count / total) * math.log2(count / total) for count in counts.values() if count > 0
        )
        return entropy

    def _ada_k_select(self, prompt: str, task_type: TaskType) -> int:
        """Select K (1-3) based on input entropy. Limited to 3 for Gemini Ensemble."""
        entropy = self._calculate_token_entropy(prompt)
        self.entropy_values.append(entropy)

        # Base K is simpler in pure Gemini mode
        # 1 = One model
        # 2 = Two models (e.g. Flash + Thinking)
        # 3 = Three models (Flash + Thinking + Pro)

        if entropy < self.ENTROPY_THRESHOLDS["low"]:
            k = 1
        elif entropy > self.ENTROPY_THRESHOLDS["high"]:
            k = 3
        else:
            k = 2

        self.ada_k_distribution[k] = self.ada_k_distribution.get(k, 0) + 1
        return k

    async def generate_adaptive(self, request: LLMRequest) -> LLMResponse:
        """Ada-K adaptive generation using Gemini Ensemble."""
        if not self._initialized:
            await self.initialize()

        k = self._ada_k_select(request.prompt, request.task_type)

        if k == 1:
            self.single_provider_count += 1
            return await self.generate(request)
        self.multi_provider_count += 1
        return await self._generate_ensemble(request, k)

    async def _generate_ensemble(self, request: LLMRequest, k: int) -> LLMResponse:
        """Query multiple Gemini models and return best response."""
        # Define model priority for ensemble
        models = [
            "gemini-3.1-flash-lite-preview-thinking-exp",
            "gemini-3.1-flash-lite-preview",
            "gemini-3.1-flash-lite-preview",
        ][:k]

        async def generate_for_model(model_name: str) -> LLMResponse | None:
            try:
                return await self._generate_gemini(request, model_name)
            except Exception as e:
                logger.warning(f"Model {model_name} failed in ensemble: {e}")
                return None

        tasks = [generate_for_model(m) for m in models]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        valid_responses = [r for r in responses if isinstance(r, LLMResponse) and r.text]

        if not valid_responses:
            return await self._mock_generate(request, time.time())

        # For now, pick the first connected response
        # Future: Use a judge model to pick the best answer
        best_response = valid_responses[0]
        best_response.metadata["ada_k"] = k
        best_response.metadata["ensemble_models"] = models
        return best_response

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response from Gemini."""
        if not self._initialized:
            await self.initialize()

        start_time = time.time()
        provider = self._select_provider(request)

        if provider is None:
            return await self._mock_generate(request, start_time)

        # Always Gemini
        model = self._select_model(provider, request.task_type)

        try:
            response = await self._generate_gemini(request, model)

            # Update metrics
            response.latency_ms = (time.time() - start_time) * 1000
            self.request_count += 1
            self.total_cost_usd += response.cost_usd
            self.latencies.append(response.latency_ms)

            return response

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            if self.fallback_to_mock:
                return await self._mock_generate(request, start_time)
            raise

    async def _generate_gemini(self, request: LLMRequest, model: str) -> LLMResponse:
        """Generate using Gemini."""
        if model not in self._gemini_models:
            # Lazy load
            try:
                self._gemini_models[model] = genai.GenerativeModel(model)
            except Exception as e:
                # Fallback to default if specific model fails load
                logger.warning(
                    f"Failed to load {model}: {e}. Fallback to gemini-3.1-flash-lite-preview"
                )
                model = "gemini-3.1-flash-lite-preview"
                if model not in self._gemini_models:
                    self._gemini_models[model] = genai.GenerativeModel(model)

        gemini_model = self._gemini_models[model]

        prompt = request.prompt
        if request.system_prompt:
            prompt = f"{request.system_prompt}\n\n{prompt}"

        # Standard config
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            stop_sequences=request.stop_sequences or [],
        )

        response = await asyncio.to_thread(
            gemini_model.generate_content,
            prompt,
            generation_config=generation_config,
        )

        # Calculate cost (estimate)
        pricing = self.PRICING.get(model, {"input": 0.001, "output": 0.002})
        # Rough token est
        in_tok = len(prompt) // 4
        out_tok = len(response.text) // 4
        cost = (in_tok / 1e6 * pricing["input"]) + (out_tok / 1e6 * pricing["output"])

        return LLMResponse(
            text=response.text,
            provider=LLMProvider.GEMINI,
            model=model,
            tokens_input=in_tok,
            tokens_output=out_tok,
            latency_ms=0,
            cost_usd=cost,
            finish_reason="STOP",
        )

    async def _mock_generate(self, request: LLMRequest, start_time: float) -> LLMResponse:
        """Generate mock response for testing."""
        await asyncio.sleep(0.1)
        mock_text = f"[MOCK GEMINI RESPONSE]\nPrompt: {request.prompt[:50]}..."
        return LLMResponse(
            text=mock_text,
            provider=LLMProvider.GEMINI,
            model="mock-gemini",
            tokens_input=len(request.prompt) // 4,
            tokens_output=len(mock_text) // 4,
            latency_ms=(time.time() - start_time) * 1000,
            cost_usd=0.0,
            finish_reason="mock",
        )

    async def generate_stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Generate with streaming (Gemini)."""
        if not self._initialized:
            await self.initialize()

        provider = self._select_provider(request)
        model = self._select_model(provider, request.task_type)

        if model not in self._gemini_models:
            # Fallback
            try:
                self._gemini_models[model] = genai.GenerativeModel(model)
            except:
                model = "gemini-3.1-flash-lite-preview"
                if model not in self._gemini_models:
                    self._gemini_models[model] = genai.GenerativeModel(model)

        gemini_model = self._gemini_models[model]

        prompt = request.prompt
        if request.system_prompt:
            prompt = f"{request.system_prompt}\n\n{prompt}"

        response = await asyncio.to_thread(gemini_model.generate_content, prompt, stream=True)

        for chunk in response:
            if chunk.text:
                yield chunk.text

    def get_stats(self) -> dict[str, Any]:
        """Get router statistics including Ada-K metrics."""
        total_adaptive = self.single_provider_count + self.multi_provider_count

        return {
            "request_count": self.request_count,
            "total_cost_usd": round(self.total_cost_usd, 4),
            "avg_latency_ms": round(sum(self.latencies) / len(self.latencies), 2)
            if self.latencies
            else 0,
            "p99_latency_ms": sorted(self.latencies)[int(len(self.latencies) * 0.99)]
            if len(self.latencies) > 10
            else 0,
            "available_providers": [p.value for p in self._available_providers],
            # Ada-K metrics
            "ada_k": {
                "distribution": {k: v for k, v in self.ada_k_distribution.items() if v > 0},
                "entropy_avg": round(sum(self.entropy_values) / len(self.entropy_values), 2)
                if self.entropy_values
                else 0,
                "single_provider_count": self.single_provider_count,
                "multi_provider_count": self.multi_provider_count,
                "single_provider_rate": round(self.single_provider_count / total_adaptive, 2)
                if total_adaptive > 0
                else 0,
            },
        }


# Global router instance
_router: LLMRouter | None = None


async def get_router() -> LLMRouter:
    """Get or create the global LLM router."""
    global _router
    if _router is None:
        _router = LLMRouter()
        await _router.initialize()
    return _router


# Convenience functions
async def generate(
    prompt: str,
    task_type: TaskType = TaskType.CODING,
    system_prompt: str | None = None,
    **kwargs,
) -> str:
    """Quick generation helper."""
    router = await get_router()
    request = LLMRequest(prompt=prompt, task_type=task_type, system_prompt=system_prompt, **kwargs)
    response = await router.generate(request)
    return response.text


async def plan(prompt: str, **kwargs) -> str:
    """Planning/architecture task."""
    return await generate(prompt, task_type=TaskType.PLANNING, **kwargs)


async def code(prompt: str, **kwargs) -> str:
    """Coding task."""
    return await generate(prompt, task_type=TaskType.CODING, **kwargs)


async def quick_fix(prompt: str, **kwargs) -> str:
    """Quick fix task."""
    return await generate(prompt, task_type=TaskType.QUICK_FIX, **kwargs)


async def generate_adaptive(
    prompt: str,
    task_type: TaskType = TaskType.CODING,
    system_prompt: str | None = None,
    **kwargs,
) -> str:
    """Ada-K adaptive generation helper - auto-selects K based on complexity."""
    router = await get_router()
    request = LLMRequest(prompt=prompt, task_type=task_type, system_prompt=system_prompt, **kwargs)
    response = await router.generate_adaptive(request)
    return response.text


if __name__ == "__main__":

    async def test():
        router = LLMRouter()
        await router.initialize()

        # Test standard generation
        print("\\n=== Testing Standard Generation ===")
        response = await router.generate(
            LLMRequest(prompt="Hello Gemini", task_type=TaskType.QUICK_FIX),
        )
        print(f"Response: {response.text}")

        # Test Ada-K
        print("\\n=== Testing Ada-K Adaptive (Gemini Ensemble) ===")
        # Complex prompt to trigger higher K
        complex_prompt = (
            "Explain the quantum mechanical basis of photosynthesis energy transfer efficiency."
            * 10
        )
        response = await router.generate_adaptive(
            LLMRequest(prompt=complex_prompt, task_type=TaskType.PLANNING),
        )
        print(f"Ensemble Models Used: {response.metadata.get('ensemble_models')}")
        print(f"Response: {response.text[:100]}...")

    asyncio.run(test())
