# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Gemini 2.5 Pro Preview API Client
==================================
Design wizard for creative direction and test generation.

Specs (Gemini 2.5 Pro Preview - Default):
- Model: gemini-3.1-flash-lite-preview-preview-06-05 (latest)
- Context: 1M+ tokens
- Pricing: ~$1.25/M input, ~$10/M output (preview)
- Features: Extended thinking, code execution, web grounding, JSON mode
- Strengths: Design, complex reasoning, parsing, test generation

Available Models:
- gemini-3.1-flash-lite-preview-preview-06-05    - Best quality, extended thinking (1M context)
- gemini-3.1-flash-lite-preview-preview-05-20  - Fast inference, 1M context
- gemini-3.1-flash-lite-preview                - Fast, economical
- gemini-3.1-flash-lite-preview-lite           - Ultra-fast, minimal cost

@omarsar0 Pattern:
- Gemini 2.5 Pro leads creative direction (~$0.087/design at 7K tokens)
- Generates designs/architecture
- Opus 4.5 integrates the results
"""

import json
import logging
import os
from collections.abc import AsyncIterator
from enum import StrEnum
from typing import Any

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class GeminiModel(StrEnum):
    """Available Gemini models - Gemini 2.5 Preview (latest)"""

    # Gemini 2.5 Preview series (latest - 1M context)
    GEMINI_25_PRO = (
        "gemini-3.1-flash-lite-preview-preview-06-05"  # 1M+ context, best design/reasoning
    )
    GEMINI_25_FLASH = "gemini-3.1-flash-lite-preview-preview-05-20"  # Fast inference, 1M context

    # Gemini 2.0 series (stable)
    GEMINI_20_FLASH = "gemini-3.1-flash-lite-preview"  # Fast, economical
    GEMINI_20_FLASH_LITE = "gemini-3.1-flash-lite-preview-lite"  # Ultra-fast, minimal

    # Aliases for backwards compatibility
    GEMINI_PRO = "gemini-3.1-flash-lite-preview-preview-06-05"
    GEMINI_FLASH = "gemini-3.1-flash-lite-preview-preview-05-20"


class GeminiConfig(BaseModel):
    """Configuration for Gemini API client - Gemini 2.5 Pro Preview"""

    api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    model: GeminiModel = GeminiModel.GEMINI_25_PRO  # Default to Gemini 2.5 Pro Preview
    max_tokens: int = 16384  # Increased for Gemini 2.5 Pro
    temperature: float = 0.7
    timeout: float = 180.0  # Longer timeout for complex reasoning

    # Gemini 2.5 Pro features
    enable_code_execution: bool = True  # Run code in sandbox
    enable_grounding: bool = True  # Web grounding for research
    enable_thinking: bool = True  # Extended thinking mode
    enable_json_mode: bool = True  # Structured JSON output


class GeminiResponse(BaseModel):
    """Structured response from Gemini"""

    content: str
    model: str
    usage: dict[str, int] = Field(default_factory=dict)
    safety_ratings: list[dict[str, Any]] = Field(default_factory=list)
    finish_reason: str = "STOP"


class DesignSpec(BaseModel):
    """Frontend design specification from Gemini"""

    component_name: str
    description: str
    props: list[dict[str, Any]]
    styling: dict[str, Any]
    accessibility: list[str]
    test_cases: list[str]
    code_skeleton: str


class GeminiClient:
    """Gemini 2.5 Pro Preview API Client - Design Wizard.

    Used in the atomic pipeline for:
    - Creative direction and design leadership
    - Parsing complex requirements
    - Test case generation
    - Architecture decisions

    Implements @omarsar0 pattern: Gemini leads design, Opus integrates.
    """

    def __init__(self, config: GeminiConfig | None = None):
        self.config = config or GeminiConfig()
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            timeout=self.config.timeout,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        return self._client

    def _build_url(self, endpoint: str) -> str:
        """Build full API URL with key"""
        return f"{self.config.base_url}/models/{self.config.model.value}:{endpoint}?key={self.config.api_key}"

    async def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> GeminiResponse:
        """Generate a completion from Gemini.

        Args:
            prompt: User prompt
            system_instruction: Optional system instructions
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            GeminiResponse with content and metadata

        """
        payload: dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature or self.config.temperature,
                "maxOutputTokens": max_tokens or self.config.max_tokens,
            },
        }

        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        url = self._build_url("generateContent")
        response = await self.client.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
        candidate = data["candidates"][0]
        content = candidate["content"]["parts"][0]["text"]

        usage = {}
        if "usageMetadata" in data:
            usage = {
                "prompt_tokens": data["usageMetadata"].get("promptTokenCount", 0),
                "completion_tokens": data["usageMetadata"].get("candidatesTokenCount", 0),
                "total_tokens": data["usageMetadata"].get("totalTokenCount", 0),
            }

        return GeminiResponse(
            content=content,
            model=self.config.model.value,
            usage=usage,
            safety_ratings=candidate.get("safetyRatings", []),
            finish_reason=candidate.get("finishReason", "STOP"),
        )

    async def design_component(
        self,
        description: str,
        framework: str = "React",
        style_system: str = "MUI",
    ) -> DesignSpec:
        """Generate a frontend component design specification.

        This implements the @omarsar0 pattern where Gemini leads creative
        direction and generates the design spec (~$0.087 per design).

        Args:
            description: Component description and requirements
            framework: Target framework (React, Vue, etc.)
            style_system: Styling system (MUI, Tailwind, etc.)

        Returns:
            DesignSpec with complete component specification

        """
        system_instruction = f"""You are a senior frontend architect specializing in {framework} and {style_system}.
Your role is CREATIVE DIRECTION - you design components, another AI will implement them.

Output structured JSON for component specifications including:
- Component architecture
- Props interface
- Styling approach
- Accessibility requirements
- Test cases

Be creative but practical. Focus on user experience and maintainability."""

        prompt = f"""Design a {framework} component with {style_system} styling:

{description}

Output a JSON object with this structure:
{{
    "component_name": "ComponentName",
    "description": "Brief description",
    "props": [
        {{"name": "propName", "type": "string", "required": true, "description": "..."}}
    ],
    "styling": {{
        "approach": "styled-components | sx prop | etc",
        "key_styles": {{}},
        "responsive": true
    }},
    "accessibility": ["ARIA requirements", "keyboard navigation", ...],
    "test_cases": ["should render correctly", "should handle click", ...],
    "code_skeleton": "// Component skeleton with key imports and structure"
}}"""

        response = await self.generate(
            prompt,
            system_instruction=system_instruction,
            temperature=0.8,
        )

        # Parse JSON from response
        try:
            # Extract JSON from potential markdown code blocks
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            spec_data = json.loads(content.strip())
            return DesignSpec(**spec_data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse design spec: {e}")
            # Return a basic spec with the raw content
            return DesignSpec(
                component_name="UnparsedComponent",
                description=description,
                props=[],
                styling={"raw_response": response.content},
                accessibility=[],
                test_cases=[],
                code_skeleton=response.content,
            )

    async def parse_requirements(
        self,
        requirements: str,
    ) -> dict[str, Any]:
        """Parse complex requirements into structured atomic tasks.

        Args:
            requirements: Raw requirements text

        Returns:
            Structured requirements breakdown

        """
        system_instruction = """You are a requirements analyst. Parse requirements into:
1. Atomic tasks (smallest implementable units)
2. Dependencies between tasks
3. Technical constraints
4. Acceptance criteria

Output structured JSON."""

        prompt = f"""Parse these requirements into atomic tasks:

{requirements}

Output JSON:
{{
    "summary": "Brief summary",
    "atomic_tasks": [
        {{
            "id": "task_1",
            "description": "...",
            "type": "feature|bugfix|refactor|test",
            "dependencies": [],
            "estimated_complexity": "low|medium|high",
            "acceptance_criteria": ["..."]
        }}
    ],
    "technical_constraints": ["..."],
    "suggested_order": ["task_1", "task_2", ...]
}}"""

        response = await self.generate(
            prompt,
            system_instruction=system_instruction,
            temperature=0.3,
        )

        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return json.loads(content.strip())
        except json.JSONDecodeError:
            return {"raw_response": response.content, "error": "Failed to parse"}

    async def generate_tests(
        self,
        code: str,
        framework: str = "pytest",
        coverage_target: str = "comprehensive",
    ) -> str:
        """Generate test cases for given code.

        Args:
            code: Source code to test
            framework: Test framework (pytest, jest, etc.)
            coverage_target: Coverage level (basic, standard, comprehensive)

        Returns:
            Generated test code

        """
        coverage_instructions = {
            "basic": "Cover happy path and one error case.",
            "standard": "Cover happy path, common error cases, and edge cases.",
            "comprehensive": "Cover all branches, edge cases, error handling, and integration scenarios.",
        }

        system_instruction = f"""You are a test engineer expert in {framework}.
{coverage_instructions.get(coverage_target, coverage_instructions["standard"])}
Generate production-ready tests with clear descriptions."""

        prompt = f"""Generate {framework} tests for this code:

```
{code}
```

Requirements:
- Use {framework} conventions
- Include setup/teardown if needed
- Mock external dependencies
- Clear test names describing behavior
- Assertions with helpful error messages"""

        response = await self.generate(
            prompt,
            system_instruction=system_instruction,
            temperature=0.3,
        )
        return response.content

    async def stream_generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream a completion from Gemini.

        Args:
            prompt: User prompt
            system_instruction: Optional system instructions

        Yields:
            Content chunks as they arrive

        """
        payload: dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self.config.temperature,
                "maxOutputTokens": self.config.max_tokens,
            },
        }

        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        url = self._build_url("streamGenerateContent")

        async with self.client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "candidates" in data:
                            parts = data["candidates"][0].get("content", {}).get("parts", [])
                            for part in parts:
                                if "text" in part:
                                    yield part["text"]
                    except json.JSONDecodeError:
                        continue
