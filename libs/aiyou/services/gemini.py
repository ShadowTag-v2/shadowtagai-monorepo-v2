# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from google import genai
from google.genai import types


class GeminiClient:
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        # Use Vertex AI backend per the provided user specification
        self.client = genai.Client(vertexai=True, project=self.project_id, location=self.location)

    async def generate_thought(self, prompt: str, system_instruction: str = None) -> str:
        # Defaults to Gemini 1.5 Pro (The Brain) for complex thought
        model = "gemini-1.5-pro-001"

        config = types.GenerateContentConfig(
            temperature=0.0,
        )
        if system_instruction:
            config.system_instruction = system_instruction

        # Using async generation
        response = await self.client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )
        return response.text

    async def generate_embedding(self, text: str) -> tuple[list, str]:
        # Utilizing text-embedding-004 for the AlloyDB Hippocampus
        response = await self.client.aio.models.embed_content(
            model="text-embedding-004",
            contents=text,
        )

        return response.embeddings[0].values, text
