"""Kernel 1: ATP 5-19 Violation Scanner using Gemini Flash."""

import json

import google.generativeai as genai

from app.config import settings
from app.kernels.base import Kernel, KernelChainError
from app.models.decision import DecisionContext, Violation, ViolationsScanOutput
from app.models.kernel import KernelInput, KernelMetrics, KernelOutput


class ATP519ScanKernel(Kernel):
    """
    Kernel 1: Extract ATP 5-19 violations from raw decision context.

    Specifications:
    - Input: Raw decision context (up to 50KB)
    - Output: Structured violations JSON (~2.5KB)
    - Model: Gemini Flash (cheapest, 40ms p50 target)
    - Token reduction: 50KB → 2.5KB (95% compression)
    """

    SYSTEM_PROMPT = """You are an ATP 5-19 compliance scanner. Your ONLY job is to extract violations from decision contexts.

ATP 5-19 RULE CATEGORIES:
- Authority Limits: Exceeding delegated decision authority
- Documentation: Missing required justifications or records
- Timeline: Decision made outside authorized timeframe
- Stakeholder: Required consultation not performed
- Scope: Decision outside authorized scope
- Conflict of Interest: Undisclosed conflicts

OUTPUT FORMAT (JSON only, no explanation):
{
  "violations": [
    {
      "rule_id": "ATP-5-19-<section>.<subsection>",
      "description": "Brief violation description",
      "severity": "minor|moderate|major|critical",
      "context": "Relevant excerpt from decision context",
      "suggested_action": "Remediation suggestion"
    }
  ]
}

STRICT RULES:
1. Return ONLY valid JSON, nothing else
2. If no violations: return {"violations": []}
3. Extract violations ONLY, do not make decisions
4. Be precise: cite exact ATP 5-19 rule IDs
5. Limit output to ~2.5KB (strip unnecessary context)
"""

    USER_PROMPT_TEMPLATE = """Scan this decision context for ATP 5-19 violations:

<decision_context>
{context}
</decision_context>

Return violations in JSON format only."""

    def __init__(self, api_key: str | None = None):
        super().__init__(name="ATP519ScanKernel", max_latency_ms=settings.kernel_1_max_latency_ms)

        # Configure Gemini API
        api_key = api_key or settings.gemini_api_key
        if not api_key:
            raise KernelChainError("Gemini API key not configured")

        genai.configure(api_key=api_key)

        # Initialize model with JSON output mode
        self.model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            generation_config={
                "temperature": 0.1,  # Low temperature for consistency
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": settings.kernel_1_max_output_tokens,
            },
        )

    async def execute(self, kernel_input: KernelInput) -> KernelOutput:
        """
        Scan decision context for ATP 5-19 violations.

        Args:
            kernel_input: Contains DecisionContext in data field

        Returns:
            KernelOutput with ViolationsScanOutput
        """
        try:
            # Extract decision context
            if isinstance(kernel_input.data, DecisionContext):
                context = kernel_input.data.content
            elif isinstance(kernel_input.data, str):
                context = kernel_input.data
            else:
                raise KernelChainError(
                    f"Invalid input type: expected DecisionContext or str, "
                    f"got {type(kernel_input.data)}"
                )

            # Build prompt
            prompt = self.USER_PROMPT_TEMPLATE.format(context=context)

            # Call Gemini API
            response = self.model.generate_content([self.SYSTEM_PROMPT, prompt])

            # Parse JSON response
            response_text = response.text.strip()

            # Handle markdown code blocks if present
            if response_text.startswith("```"):
                # Extract JSON from markdown code block
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])  # Remove first and last lines

            violations_data = json.loads(response_text)

            # Validate and structure violations
            violations = [Violation(**v) for v in violations_data.get("violations", [])]

            # Create structured output
            scan_output = ViolationsScanOutput(
                violations=violations,
                scan_metadata={
                    "model": settings.gemini_model,
                    "context_size_bytes": len(context.encode()),
                },
            )

            # Calculate token counts (approximate)
            input_tokens = len(context.split()) + len(self.SYSTEM_PROMPT.split())
            output_tokens = len(response_text.split())

            # Estimate cost (Gemini Flash pricing: ~$0.00001 per 1K tokens)
            cost = (input_tokens + output_tokens) / 1000 * 0.00001

            return KernelOutput(
                data=scan_output,
                kernel_name=self.name,
                success=True,
                metrics=KernelMetrics(
                    latency_ms=0,  # Will be set by base class
                    token_count_input=input_tokens,
                    token_count_output=output_tokens,
                    cost_usd=cost,
                ),
            )

        except json.JSONDecodeError as e:
            raise KernelChainError(
                f"Failed to parse Gemini response as JSON: {str(e)}\n"
                f"Response: {response_text[:200]}"
            ) from e
        except Exception as e:
            raise KernelChainError(f"ATP 5-19 scan failed: {str(e)}") from e
