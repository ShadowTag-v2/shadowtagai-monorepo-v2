"""GeminiAntigravity - Core intelligence engine.
Replaces MediaPipe/Emotion/Text pipelines with native Gemini multimodal.
Supports both Vertex AI and direct API key authentication.

Rate Limit Fallback Chain (ID/EGO/SUPEREGO):
- Primary:   gemini-2.5-pro-preview-06-05 (ID: max capability)
- Fallback1: gemini-2.5-flash-preview-05-20 (EGO: balanced)
- Fallback2: gemini-2.0-flash (SUPEREGO: guaranteed execution)
"""

import contextlib
import hashlib
import json
import logging
import os
import time

# Google Generative AI (API key) imports
import google.generativeai as genai
import redis

# Vertex AI imports
import vertexai
from google.generativeai.types import HarmBlockThreshold, HarmCategory
from vertexai.generative_models import GenerativeModel as VertexModel
from vertexai.generative_models import Part, SafetySetting

logger = logging.getLogger(__name__)

# Model fallback chain - ID → EGO → SUPEREGO
MODEL_FALLBACK_CHAIN = [
    "gemini-2.5-pro-preview-06-05",  # ID: Maximum capability, aggressive optimization
    "gemini-2.5-flash",  # EGO: Balanced performance/cost
    "gemini-2.0-flash",  # SUPEREGO: Guaranteed execution, survivability
]


class GeminiAntigravity:
    def __init__(
        self,
        project_id: str = None,
        location: str = "us-central1",
        api_key: str = None,
        redis_host: str = "10.85.19.187",
        redis_port: int = 6379,
        cache_ttl: int = 3600,
    ):
        """Initialize Gemini engine.

        Args:
            project_id: GCP project ID for Vertex AI (optional if using API key)
            location: GCP region for Vertex AI
            api_key: Gemini API key (optional, falls back to GEMINI_API_KEY env var)
            redis_host: Redis host for caching
            redis_port: Redis port
            cache_ttl: Cache TTL in seconds (default 1 hour)

        """
        self.use_vertex = False
        self.cache_ttl = cache_ttl

        # Redis connection for caching (graceful fallback)
        try:
            self._redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            self._redis.ping()
            self._cache_available = True
        except:
            self._redis = None
            self._cache_available = False

        # Try API key first (simpler setup)
        api_key = api_key or os.getenv("GEMINI_API_KEY")

        # Rate limit tracking - which models are currently limited
        self._rate_limited_models: set = set()
        self._rate_limit_reset: dict = {}  # model -> reset timestamp

        # Current model index in fallback chain
        self._current_model_idx = 0
        self._api_key = api_key or os.getenv("GEMINI_API_KEY")
        self._project_id = project_id
        self._location = location

        if self._api_key:
            # Use Google Generative AI SDK with API key
            genai.configure(api_key=self._api_key)
            # Gemini 2.5 Pro Preview - 1M context, Deep Think mode
            self.model = genai.GenerativeModel(MODEL_FALLBACK_CHAIN[0])
            self.current_model_name = MODEL_FALLBACK_CHAIN[0]
            self.use_vertex = False

            # Safety config for genai SDK
            self.safety_config = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
        elif project_id:
            # Fall back to Vertex AI
            vertexai.init(project=project_id, location=location)
            # Gemini 2.5 Pro Preview - 1M context, Deep Think mode
            self.model = VertexModel(MODEL_FALLBACK_CHAIN[0])
            self.current_model_name = MODEL_FALLBACK_CHAIN[0]
            self.use_vertex = True

            # Safety config for Vertex AI
            self.safety_config = [
                SafetySetting(
                    category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                ),
            ]
        else:
            raise ValueError("Either api_key or project_id must be provided")

    def _get_generation_config(self, thinking_level: str = "high", json_output: bool = False):
        """Get generation config with Gemini 3 Deep Think mode.

        Args:
            thinking_level: "high" (Deep Think) or "low" (fast response)
            json_output: Return JSON formatted output

        """
        # Gemini 3 Deep Think mode for complex reasoning
        config = {"thinking_level": thinking_level}
        if json_output:
            config["response_mime_type"] = "application/json"
        return config

    def _cache_key(self, prefix: str, content: str) -> str:
        """Generate cache key from content hash."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"gemini:{prefix}:{content_hash}"

    def _get_cached(self, key: str) -> str | None:
        """Get cached response."""
        if self._cache_available:
            try:
                return self._redis.get(key)
            except:
                pass
        return None

    def _set_cached(self, key: str, value: str) -> None:
        """Set cached response with TTL."""
        if self._cache_available:
            with contextlib.suppress(BaseException):
                self._redis.setex(key, self.cache_ttl, value)

    # =========================================================================
    # Rate Limit Fallback (ID → EGO → SUPEREGO)
    # =========================================================================

    def _is_rate_limited(self, model_name: str) -> bool:
        """Check if a model is currently rate limited."""
        if model_name not in self._rate_limited_models:
            return False

        # Check if rate limit has expired (default 60s reset)
        reset_time = self._rate_limit_reset.get(model_name, 0)
        if time.time() > reset_time:
            self._rate_limited_models.discard(model_name)
            return False

        return True

    def _mark_rate_limited(self, model_name: str, retry_after: int = 60) -> None:
        """Mark a model as rate limited."""
        self._rate_limited_models.add(model_name)
        self._rate_limit_reset[model_name] = time.time() + retry_after
        logger.warning(f"Model {model_name} rate limited, reset in {retry_after}s")

    def _get_next_available_model(self) -> str:
        """Get next available model in fallback chain.

        ID → EGO → SUPEREGO pattern:
        - ID (Pro): Maximum capability, aggressive optimization
        - EGO (Flash Preview): Balanced performance/cost
        - SUPEREGO (Flash): Guaranteed execution, survivability
        """
        for model_name in MODEL_FALLBACK_CHAIN:
            if not self._is_rate_limited(model_name):
                return model_name

        # All models rate limited - use SUPEREGO (last resort, always works)
        logger.warning("All models rate limited, forcing SUPEREGO tier")
        return MODEL_FALLBACK_CHAIN[-1]

    def _switch_model(self, model_name: str) -> None:
        """Switch to a different model in the fallback chain."""
        if model_name == self.current_model_name:
            return

        logger.info(f"Switching model: {self.current_model_name} → {model_name}")

        if self.use_vertex:
            self.model = VertexModel(model_name)
        else:
            self.model = genai.GenerativeModel(model_name)

        self.current_model_name = model_name

    def _execute_with_fallback(self, execute_fn, *args, **kwargs):
        """Execute a function with automatic rate-limit fallback.

        ID/EGO/SUPEREGO Decision Framework:
        - ID: Try maximum capability first (gemini-2.5-pro-preview)
        - EGO: Fall back to balanced tier on rate limit (gemini-2.5-flash-preview)
        - SUPEREGO: Guarantee execution via stable tier (gemini-2.0-flash)

        p99 survivability gate: Operation MUST complete, even at reduced capability.
        """
        last_error = None

        for _attempt, model_name in enumerate(MODEL_FALLBACK_CHAIN):
            if self._is_rate_limited(model_name):
                continue

            try:
                self._switch_model(model_name)
                return execute_fn(*args, **kwargs)

            except Exception as e:
                error_str = str(e).lower()

                # Check for rate limit errors (429, quota, rate limit)
                if any(
                    x in error_str for x in ["429", "rate limit", "quota", "resource exhausted"]
                ):
                    # Extract retry-after if available
                    retry_after = 60
                    if "retry-after" in error_str:
                        with contextlib.suppress(BaseException):
                            retry_after = int(error_str.split("retry-after")[1].split()[0])

                    self._mark_rate_limited(model_name, retry_after)
                    last_error = e
                    logger.warning(f"Rate limit on {model_name}, trying next tier...")
                    continue
                # Non-rate-limit error, propagate
                raise

        # All models exhausted - raise last error
        if last_error:
            raise last_error
        raise RuntimeError("All models in fallback chain exhausted")

    def get_model_status(self) -> dict:
        """Get current model status and rate limit state."""
        return {
            "current_model": self.current_model_name,
            "fallback_chain": MODEL_FALLBACK_CHAIN,
            "rate_limited": list(self._rate_limited_models),
            "tier": "ID"
            if self.current_model_name == MODEL_FALLBACK_CHAIN[0]
            else "EGO"
            if self.current_model_name == MODEL_FALLBACK_CHAIN[1]
            else "SUPEREGO",
        }

    def analyze_video_stream(self, video_uri: str, mime_type: str = "video/mp4") -> dict:
        """Multimodal analysis: Single pass extraction of gestures, emotions, transcript.
        """
        prompt = """
        Analyze this video segment for the 'ShadowTagAi' platform.
        Output JSON only with these keys:
        1. 'gestures': List of ASL or hand gestures identified with timestamps.
        2. 'emotions': Dominant micro-expressions detected (Ekman scale).
        3. 'conflict_score': 0.0 to 1.0 float indicating verbal/non-verbal aggression.
        4. 'transcript': Verbatim text.
        """

        if self.use_vertex:
            video_part = Part.from_uri(uri=video_uri, mime_type=mime_type)
            response = self.model.generate_content(
                [video_part, prompt],
                safety_settings=self.safety_config,
                generation_config=self._get_generation_config(json_output=True),
            )
        else:
            # For API key mode, upload video file
            video_file = genai.upload_file(video_uri)
            response = self.model.generate_content(
                [video_file, prompt],
                safety_settings=self.safety_config,
                generation_config=self._get_generation_config(json_output=True),
            )

        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {"raw_output": response.text}

    def generate_governance_decision(self, conflict_data: dict) -> str:
        """The 'Living Regulator' logic: Proposes binding resolutions.
        """
        response = self.model.generate_content(
            f"Act as a neutral arbitrator. Review this conflict data: {conflict_data}. "
            "Propose a de-escalation path based on ATP 5-19 principles.",
            safety_settings=self.safety_config,
        )
        return response.text

    def generate_text(self, prompt: str, json_output: bool = False, use_cache: bool = True) -> str:
        """Text generation with automatic rate-limit fallback.

        ID/EGO/SUPEREGO Decision Framework:
        - ID (gemini-2.5-pro-preview): Maximum capability, try first
        - EGO (gemini-2.5-flash-preview): Balanced fallback on rate limit
        - SUPEREGO (gemini-2.0-flash): p99 survivability guarantee

        Args:
            prompt: The input prompt
            json_output: Whether to return JSON formatted output
            use_cache: Whether to use Redis caching (default True)

        Returns:
            Generated text response

        """
        cache_key = self._cache_key("text", f"{prompt}:{json_output}")

        # Check cache first
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached

        def _generate():
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_config,
                generation_config=self._get_generation_config(json_output=json_output),
            )
            return response.text

        # Execute with automatic fallback on rate limit
        result = self._execute_with_fallback(_generate)

        # Cache the result
        if use_cache:
            self._set_cached(cache_key, result)

        return result

    def chat(self, messages: list[dict]) -> str:
        """Multi-turn chat conversation.

        Args:
            messages: List of {"role": "user"|"model", "parts": ["text"]}

        Returns:
            Model response text

        """
        chat_session = self.model.start_chat(history=messages[:-1] if len(messages) > 1 else [])
        response = chat_session.send_message(
            messages[-1]["parts"] if messages else "",
            safety_settings=self.safety_config,
        )
        return response.text
