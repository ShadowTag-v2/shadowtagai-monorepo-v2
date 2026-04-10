import hashlib
import json
import logging
import sqlite3
from datetime import datetime

from google.cloud import discoveryengine_v1 as discoveryengine

from src.config.settings import settings

logger = logging.getLogger(__name__)


class GroundedGenerationService:
    def __init__(self, db_path: str = "grounded_gen_cache.db"):
        self.project_number = settings.google_project_number
        self.location = settings.google_cloud_location
        self.db_path = db_path
        self._init_db()

        try:
            self.client = discoveryengine.GroundedGenerationServiceClient()
        except Exception as e:
            logger.error(f"Failed to initialize GroundedGenerationServiceClient: {e}")
            self.client = None

    def _init_db(self):
        """Initialize SQLite cache database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    id TEXT PRIMARY KEY,
                    prompt TEXT,
                    model_id TEXT,
                    response TEXT,
                    created_at TIMESTAMP
                )
            """)

    def _get_cache_key(self, prompt: str, model_id: str) -> str:
        """Generate a unique cache key."""
        content = f"{prompt}:{model_id}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _get_from_cache(self, prompt: str, model_id: str) -> dict | None:
        """Retrieve response from cache."""
        key = self._get_cache_key(prompt, model_id)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT response FROM cache WHERE id = ?", (key,))
            row = cursor.fetchone()
            if row:
                logger.info(f"Cache hit for prompt: '{prompt[:50]}...'")
                return json.loads(row[0])
        return None

    def _save_to_cache(self, prompt: str, model_id: str, response: dict):
        """Save response to cache."""
        key = self._get_cache_key(prompt, model_id)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (id, prompt, model_id, response, created_at) VALUES (?, ?, ?, ?, ?)",
                (key, prompt, model_id, json.dumps(response), datetime.now()),
            )

    async def generate(self, prompt: str, model_id: str = "gemini-1.5-pro") -> dict:
        # Check cache first
        cached_result = self._get_from_cache(prompt, model_id)
        if cached_result:
            return cached_result

        if not self.client:
            raise RuntimeError("GroundedGenerationServiceClient is not initialized.")

        logger.info(f"Generating grounded content for prompt: '{prompt}'")

        location_path = self.client.common_location_path(
            project=self.project_number, location=self.location
        )

        request = discoveryengine.GenerateGroundedContentRequest(
            location=location_path,
            generation_spec=discoveryengine.GenerateGroundedContentRequest.GenerationSpec(
                model_id=model_id,
            ),
            contents=[
                discoveryengine.GroundedGenerationContent(
                    role="user",
                    parts=[discoveryengine.GroundedGenerationContent.Part(text=prompt)],
                )
            ],
            system_instruction=discoveryengine.GroundedGenerationContent(
                parts=[
                    discoveryengine.GroundedGenerationContent.Part(
                        text="Be comprehensive and cite sources."
                    )
                ]
            ),
            grounding_spec=discoveryengine.GenerateGroundedContentRequest.GroundingSpec(
                grounding_sources=[
                    discoveryengine.GenerateGroundedContentRequest.GroundingSource(
                        google_search_source=discoveryengine.GenerateGroundedContentRequest.GroundingSource.GoogleSearchSource(
                            dynamic_retrieval_config=discoveryengine.GenerateGroundedContentRequest.DynamicRetrievalConfiguration(
                                predictor=discoveryengine.GenerateGroundedContentRequest.DynamicRetrievalConfiguration.DynamicRetrievalPredictor(
                                    threshold=0.7
                                )
                            )
                        )
                    )
                ]
            ),
        )

        # Note: The client library is synchronous by default.
        # For high-throughput async FastAPI, we should run this in a threadpool or use async client if available.
        # discoveryengine_v1 usually has async clients but let's stick to sync for simplicity unless requested.
        # Actually, let's wrap it in run_in_executor to avoid blocking the event loop.
        import asyncio
        from functools import partial

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None, partial(self.client.generate_grounded_content, request)
        )

        # Parse response
        result_text = ""
        citations = []

        for candidate in response.candidates:
            for part in candidate.content.parts:
                result_text += part.text

            if candidate.grounding_metadata.search_entry_point:
                citations.append(
                    {
                        "search_entry_point": candidate.grounding_metadata.search_entry_point.rendered_content
                    }
                )

            # Extract support chunks if needed, but text + search entry point is usually enough for display

        result = {
            "text": result_text,
            "citations": citations,
            # "raw_response": str(response) # Skip raw response in cache to save space, or keep if needed
        }

        # Save to cache
        self._save_to_cache(prompt, model_id, result)

        return result
