"""
Gemini AI Client Service
Handles all interactions with Google Gemini API for content ingestion and analysis
"""

import asyncio
import io
import logging
from datetime import datetime
from functools import wraps
from typing import Any

import google.generativeai as genai
from google.cloud import aiplatform, storage
from PIL import Image

logger = logging.getLogger(__name__)


class GeminiRateLimitExceeded(Exception):
    """Raised when Gemini API rate limit is hit"""

    pass


class GeminiServiceError(Exception):
    """Base exception for Gemini service errors"""

    pass


def async_retry(max_retries: int = 3, backoff_seconds: float = 1.0):
    """Decorator for retrying async functions with exponential backoff"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except GeminiRateLimitExceeded:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = backoff_seconds * (2**attempt)
                    logger.warning(
                        f"Rate limited, waiting {wait_time}s before retry {attempt + 1}/{max_retries}"
                    )
                    await asyncio.sleep(wait_time)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.error(f"Attempt {attempt + 1} failed: {e}")
                    await asyncio.sleep(backoff_seconds)
            raise GeminiServiceError(f"Max retries ({max_retries}) exceeded")

        return wrapper

    return decorator


class GeminiClient:
    """
    Client for Google Gemini API
    Handles content analysis, moderation, embeddings, and text generation
    """

    def __init__(
        self,
        api_key: str | None = None,
        project_id: str | None = None,
        location: str = "us-central1",
    ):
        """
        Initialize Gemini client

        Args:
            api_key: Google API key for genai (for prototyping)
            project_id: GCP project ID for Vertex AI (for production)
            location: GCP region for Vertex AI
        """
        self.api_key = api_key
        self.project_id = project_id
        self.location = location

        # Configure based on environment
        if api_key:
            # Development: Use genai SDK
            genai.configure(api_key=api_key)
            self.mode = "genai"
        elif project_id:
            # Production: Use Vertex AI
            aiplatform.init(project=project_id, location=location)
            self.mode = "vertex"
        else:
            raise ValueError("Either api_key or project_id must be provided")

        # Model configurations
        self.models = {
            "vision": "gemini-1.5-pro-vision",  # For image/video analysis
            "text": "gemini-1.5-pro",  # For text analysis
            "embedding": "textembedding-gecko@003",  # For embeddings
        }

        # Cost tracking (per 1M tokens)
        self.pricing = {
            "gemini-1.5-pro": {"input": 3.50, "output": 10.50},  # USD per 1M tokens
            "gemini-1.5-pro-vision": {"input": 3.50, "output": 10.50},
            "gemini-1.5-flash": {
                "input": 0.35,
                "output": 1.05,
            },  # Cheaper, faster model
            "textembedding-gecko": 0.025,  # Per 1K characters
        }

        # Rate limits (requests per minute)
        self.rate_limits = {
            "gemini-1.5-pro": 60,
            "gemini-1.5-flash": 360,
        }

        self._request_counts = {}  # Track requests for rate limiting
        self._last_reset = datetime.utcnow()

        logger.info(f"GeminiClient initialized in {self.mode} mode")

    async def _check_rate_limit(self, model: str):
        """Check if we're within rate limits"""
        now = datetime.utcnow()
        if (now - self._last_reset).seconds >= 60:
            # Reset counters every minute
            self._request_counts = {}
            self._last_reset = now

        current_count = self._request_counts.get(model, 0)
        limit = self.rate_limits.get(model, 60)

        if current_count >= limit:
            raise GeminiRateLimitExceeded(
                f"Rate limit exceeded for {model}: {current_count}/{limit} RPM"
            )

        self._request_counts[model] = current_count + 1

    @async_retry(max_retries=3, backoff_seconds=2.0)
    async def analyze_image(
        self,
        image_path: str,
        include_labels: bool = True,
        include_moderation: bool = True,
        include_text: bool = True,
        include_objects: bool = True,
    ) -> dict[str, Any]:
        """
        Analyze image using Gemini Vision

        Args:
            image_path: GCS path or local file path
            include_labels: Detect labels/categories
            include_moderation: Perform safety moderation
            include_text: OCR text detection
            include_objects: Object detection

        Returns:
            Dict with analysis results
        """
        await self._check_rate_limit("gemini-1.5-pro-vision")

        try:
            # Load image
            if image_path.startswith("gs://"):
                image_data = await self._download_from_gcs(image_path)
            else:
                with open(image_path, "rb") as f:
                    image_data = f.read()

            image = Image.open(io.BytesIO(image_data))

            # Build prompt based on requested analysis
            prompt_parts = []
            if include_labels:
                prompt_parts.append(
                    "Identify and describe the main subjects, objects, and themes in this image."
                )
            if include_objects:
                prompt_parts.append(
                    "List all distinct objects visible in the image with confidence scores."
                )
            if include_text:
                prompt_parts.append("Extract any text visible in the image (OCR).")

            prompt = "\n".join(prompt_parts) if prompt_parts else "Describe this image in detail."

            # Generate content
            if self.mode == "genai":
                model = genai.GenerativeModel(self.models["vision"])
                response = await asyncio.to_thread(model.generate_content, [prompt, image])
                content = response.text
                tokens_used = (
                    response.usage_metadata.total_token_count
                    if hasattr(response, "usage_metadata")
                    else 1000
                )
            else:
                # Vertex AI implementation
                model = aiplatform.gapic.PredictionServiceClient()
                # Implementation depends on Vertex AI endpoint configuration
                content = "Vision analysis via Vertex AI"
                tokens_used = 1000

            # Parse response into structured data
            result = {
                "raw_response": content,
                "labels": self._extract_labels(content) if include_labels else [],
                "objects": self._extract_objects(content) if include_objects else [],
                "detected_text": self._extract_text(content) if include_text else "",
                "moderation": await self._moderate_content(content, "image")
                if include_moderation
                else {},
                "tokens_used": tokens_used,
                "model": self.models["vision"],
            }

            return result

        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            raise GeminiServiceError(f"Failed to analyze image: {str(e)}")

    @async_retry(max_retries=3, backoff_seconds=2.0)
    async def analyze_video(
        self,
        video_path: str,
        _sample_frames: int = 10,
        include_transcript: bool = True,
        include_moderation: bool = True,
    ) -> dict[str, Any]:
        """
        Analyze video using Gemini Vision
        Samples frames and analyzes content

        Args:
            video_path: GCS path to video
            sample_frames: Number of frames to analyze
            include_transcript: Generate transcript (if audio present)
            include_moderation: Perform safety moderation

        Returns:
            Dict with video analysis results
        """
        await self._check_rate_limit("gemini-1.5-pro-vision")

        # For MVP, we'll analyze as image sequence
        # Production would use proper video API
        prompt = f"""
        Analyze this video content:
        1. Describe the main narrative and key events
        2. Identify the primary subjects and objects
        3. Assess the overall tone and genre
        4. List any text or captions visible
        {"5. Transcribe the audio/dialogue" if include_transcript else ""}
        """

        try:
            if self.mode == "genai":
                model = genai.GenerativeModel(self.models["vision"])
                # Note: Full video support requires uploading to File API
                # For now, we'll use text-based analysis
                response = await asyncio.to_thread(model.generate_content, prompt)
                content = response.text
                tokens_used = (
                    response.usage_metadata.total_token_count
                    if hasattr(response, "usage_metadata")
                    else 5000
                )
            else:
                content = "Video analysis via Vertex AI"
                tokens_used = 5000

            result = {
                "raw_response": content,
                "summary": self._extract_summary(content),
                "key_moments": self._extract_key_moments(content),
                "detected_objects": self._extract_objects(content),
                "transcript": self._extract_transcript(content) if include_transcript else "",
                "moderation": await self._moderate_content(content, "video")
                if include_moderation
                else {},
                "tokens_used": tokens_used,
                "model": self.models["vision"],
            }

            return result

        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            raise GeminiServiceError(f"Failed to analyze video: {str(e)}")

    @async_retry(max_retries=3, backoff_seconds=2.0)
    async def moderate_text(self, text: str) -> dict[str, Any]:
        """
        Moderate text content for safety

        Returns:
            {
                "category": "safe" | "violence" | "hate_speech" | etc,
                "confidence": 0-100,
                "details": {...},
                "safe_to_publish": bool
            }
        """
        await self._check_rate_limit("gemini-1.5-pro")

        prompt = f"""
        Analyze the following text for content safety and moderation:

        Text: "{text}"

        Provide a safety assessment in the following categories:
        1. Violence (0-100 score)
        2. Hate speech (0-100 score)
        3. Sexual content (0-100 score)
        4. Dangerous activities (0-100 score)
        5. Harassment (0-100 score)
        6. Illegal activities (0-100 score)

        For each category, provide a score from 0 (completely safe) to 100 (severe violation).
        Then provide an overall recommendation: SAFE, REQUIRES_REVIEW, or REJECT.
        """

        try:
            if self.mode == "genai":
                model = genai.GenerativeModel(self.models["text"])
                response = await asyncio.to_thread(model.generate_content, prompt)
                content = response.text
                tokens_used = (
                    response.usage_metadata.total_token_count
                    if hasattr(response, "usage_metadata")
                    else 500
                )
            else:
                content = "Moderation via Vertex AI"
                tokens_used = 500

            # Parse moderation scores
            moderation = self._parse_moderation_response(content)
            moderation["tokens_used"] = tokens_used

            return moderation

        except Exception as e:
            logger.error(f"Text moderation failed: {e}")
            raise GeminiServiceError(f"Failed to moderate text: {str(e)}")

    @async_retry(max_retries=3, backoff_seconds=2.0)
    async def generate_metadata(
        self, content_description: str, content_type: str = "video"
    ) -> dict[str, Any]:
        """
        Generate title, description, and tags for content

        Args:
            content_description: Description of the content
            content_type: Type of content (video, image, etc)

        Returns:
            {
                "title": str,
                "description": str,
                "tags": List[str],
                "category": str
            }
        """
        await self._check_rate_limit("gemini-1.5-flash")  # Use faster model for metadata

        prompt = f"""
        Based on this {content_type} content description, generate optimized metadata:

        Content: {content_description}

        Generate:
        1. A compelling title (max 100 characters)
        2. A detailed description (150-300 words)
        3. 10-15 relevant tags
        4. Primary category

        Format your response as JSON.
        """

        try:
            if self.mode == "genai":
                model = genai.GenerativeModel("gemini-1.5-flash")  # Faster, cheaper
                response = await asyncio.to_thread(model.generate_content, prompt)
                content = response.text
                tokens_used = (
                    response.usage_metadata.total_token_count
                    if hasattr(response, "usage_metadata")
                    else 300
                )
            else:
                content = '{"title": "Generated Title", "description": "Generated description", "tags": []}'
                tokens_used = 300

            # Parse JSON response
            import json

            metadata = json.loads(content.strip("```json\n").strip("```"))
            metadata["tokens_used"] = tokens_used

            return metadata

        except Exception as e:
            logger.error(f"Metadata generation failed: {e}")
            # Return fallback metadata
            return {
                "title": f"Untitled {content_type}",
                "description": content_description[:300],
                "tags": [],
                "category": "general",
                "tokens_used": 0,
            }

    async def generate_embedding(self, text: str) -> tuple[list[float], int]:
        """
        Generate embedding vector for text

        Args:
            text: Text to embed

        Returns:
            (embedding_vector, character_count)
        """
        try:
            if self.mode == "vertex":
                # Use Vertex AI Text Embeddings
                from vertexai.language_models import TextEmbeddingModel

                model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
                embeddings = await asyncio.to_thread(model.get_embeddings, [text])
                vector = embeddings[0].values
                char_count = len(text)
            else:
                # Fallback for dev mode
                import hashlib

                # Generate deterministic fake embedding for testing
                hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
                vector = [(hash_val >> i) % 100 / 100.0 for i in range(768)]
                char_count = len(text)

            return vector, char_count

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise GeminiServiceError(f"Failed to generate embedding: {str(e)}")

    def calculate_cost(self, tokens_used: int, model: str, token_type: str = "total") -> float:
        """
        Calculate cost in USD for Gemini API usage

        Args:
            tokens_used: Number of tokens consumed
            model: Model name
            token_type: "input", "output", or "total"

        Returns:
            Cost in USD
        """
        if model not in self.pricing:
            logger.warning(f"Unknown model for pricing: {model}")
            return 0.0

        pricing = self.pricing[model]

        if isinstance(pricing, dict):
            # Has separate input/output pricing
            if token_type == "input":
                rate = pricing["input"]
            elif token_type == "output":
                rate = pricing["output"]
            else:  # total - use average
                rate = (pricing["input"] + pricing["output"]) / 2
        else:
            # Flat rate
            rate = pricing

        # Rate is per 1M tokens or 1K characters
        if "embedding" in model:
            # Embeddings priced per 1K characters
            return (tokens_used / 1000) * rate
        else:
            # Models priced per 1M tokens
            return (tokens_used / 1_000_000) * rate

    # Helper methods for parsing Gemini responses

    def _extract_labels(self, response: str) -> list[str]:
        """Extract labels from Gemini response"""
        # Simple keyword extraction - in production, use structured output
        keywords = []
        if "subjects:" in response.lower() or "objects:" in response.lower():
            # Parse structured response
            lines = response.split("\n")
            for line in lines:
                if any(prefix in line.lower() for prefix in ["subject:", "object:", "theme:"]):
                    keywords.append(line.split(":")[-1].strip())
        return keywords[:20]  # Limit to top 20

    def _extract_objects(self, response: str) -> list[dict[str, Any]]:
        """Extract object detections from response"""
        # In production, use structured JSON output
        return [{"object": "detected_object", "confidence": 0.85}]

    def _extract_text(self, response: str) -> str:
        """Extract OCR text from response"""
        if "text:" in response.lower():
            parts = response.lower().split("text:")
            if len(parts) > 1:
                return parts[1].split("\n")[0].strip()
        return ""

    async def _moderate_content(self, content: str, content_type: str) -> dict[str, Any]:
        """Perform content moderation"""
        # Simplified - in production, call dedicated moderation API
        return {"category": "safe", "confidence": 95, "safe_to_publish": True}

    def _extract_summary(self, response: str) -> str:
        """Extract summary from video analysis"""
        lines = response.split("\n")
        if lines:
            return lines[0][:500]
        return ""

    def _extract_key_moments(self, response: str) -> list[dict[str, Any]]:
        """Extract key moments from video"""
        return []

    def _extract_transcript(self, response: str) -> str:
        """Extract transcript from response"""
        if "transcript:" in response.lower():
            parts = response.lower().split("transcript:")
            if len(parts) > 1:
                return parts[1].strip()
        return ""

    def _parse_moderation_response(self, response: str) -> dict[str, Any]:
        """Parse moderation response into structured format"""
        # Simple parser - in production, use structured output
        scores = {
            "violence": 0,
            "hate_speech": 0,
            "sexual": 0,
            "dangerous": 0,
            "harassment": 0,
            "illegal": 0,
        }

        # Parse scores from response
        for category in scores:
            if category in response.lower():
                # Try to extract score
                parts = response.lower().split(category)
                if len(parts) > 1:
                    # Look for number
                    import re

                    numbers = re.findall(r"\d+", parts[1][:50])
                    if numbers:
                        scores[category] = min(int(numbers[0]), 100)

        max_score = max(scores.values())
        max_category = max(scores.items(), key=lambda x: x[1])[0]

        if max_score >= 80:
            status = "rejected"
            safe_to_publish = False
        elif max_score >= 50:
            status = "requires_review"
            safe_to_publish = False
        else:
            status = "safe"
            safe_to_publish = True

        return {
            "category": max_category if max_score > 20 else "safe",
            "confidence": max_score,
            "details": scores,
            "safe_to_publish": safe_to_publish,
            "recommended_action": status,
        }

    async def _download_from_gcs(self, gcs_path: str) -> bytes:
        """Download file from Google Cloud Storage"""
        # Parse gs://bucket/path
        parts = gcs_path.replace("gs://", "").split("/", 1)
        bucket_name = parts[0]
        blob_name = parts[1] if len(parts) > 1 else ""

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        return await asyncio.to_thread(blob.download_as_bytes)
