# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Layer 1: Gemini Policy Understanding
Interprets ATP 5-19 Purpose/Reasons/Brakes using fine-tuned LLM
"""

from google import genai
from typing import Any
import json

from ..models.database import RiskLevel
from ..core.config import settings


class GeminiPolicyLayer:
  """
  Layer 1: Policy understanding using Gemini
  Evaluates Purpose, Reasons, and Brakes from ATP 5-19 framework
  """

  def __init__(self):
    """Initialize Gemini client"""
    if settings.GOOGLE_API_KEY:
      self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
      self.model_name = settings.POLICY_MODEL
    else:
      self.client = None
      self.model_name = None
      print("WARNING: GOOGLE_API_KEY not set. Layer 1 will use fallback logic.")

  async def assess(
    self,
    prompt: str,
    context: dict[str, Any] | None = None,
    user_policies: list[dict] | None = None,
  ) -> dict[str, Any]:
    """
    Assess prompt against ATP 5-19 policies

    Args:
        prompt: The AI request to assess
        context: Additional context
        user_policies: Custom policies (if any)

    Returns:
        Dict with risk_level, confidence, reasoning, metadata
    """
    # Build assessment prompt for Gemini
    assessment_prompt = self._build_assessment_prompt(prompt, context, user_policies)

    if self.client is None:
      # Fallback: Simple heuristic-based assessment
      return self._fallback_assessment(prompt, context)

    try:
      # Call Gemini API
      response = await self._call_gemini(assessment_prompt)

      # Parse response
      result = self._parse_gemini_response(response)

      return result

    except Exception as e:
      print(f"Layer 1 error: {e}")
      # Fallback to conservative assessment
      return {
        "risk_level": RiskLevel.MODERATE,
        "confidence": 0.5,
        "reasoning": f"Layer 1 error: {str(e)}. Defaulting to MODERATE risk.",
        "metadata": {"error": str(e)},
      }

  def _build_assessment_prompt(
    self,
    prompt: str,
    context: dict[str, Any] | None,
    user_policies: list[dict] | None,
  ) -> str:
    """Build prompt for Gemini assessment"""
    system_context = """You are an ATP 5-19 risk assessment expert for AI systems.
Your job is to evaluate AI requests using the military risk management framework:

ATP 5-19 FRAMEWORK:
1. PURPOSE: What is the intended outcome?
2. REASONS: Why should this be allowed or denied?
3. BRAKES: What are the hard stops (compliance, safety, ethics)?

RISK LEVELS (from ATP 5-19):
- CATASTROPHIC: Loss of life, critical system failure, massive liability
- CRITICAL: Serious harm, major compliance violation, significant financial loss
- MODERATE: Minor harm, compliance concerns, moderate financial impact
- LOW: Minimal risk, easily mitigated
- NEGLIGIBLE: No meaningful risk

Evaluate the following AI request and respond in JSON format:
{
  "risk_level": "catastrophic|critical|moderate|low|negligible",
  "confidence": 0.0-1.0,
  "purpose": "What is the user trying to accomplish?",
  "reasons_allow": ["Reason 1", "Reason 2"],
  "reasons_deny": ["Reason 1", "Reason 2"],
  "brakes_violated": ["Brake 1", "Brake 2"],
  "reasoning": "Human-readable explanation"
}
"""

    user_prompt = f"""
AI REQUEST TO ASSESS:
{prompt}

CONTEXT:
{json.dumps(context or {}, indent=2)}

CUSTOM POLICIES:
{json.dumps(user_policies or [], indent=2)}

Provide your ATP 5-19 risk assessment as JSON:
"""

    return system_context + "\n\n" + user_prompt

  async def _call_gemini(self, prompt: str) -> str:
    """Call Gemini API (async)"""
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    executor = ThreadPoolExecutor(max_workers=1)
    loop = asyncio.get_event_loop()

    def _sync_call():
      response = self.client.models.generate_content(
        model=self.model_name,
        contents=prompt,
      )
      return response.text

    result = await loop.run_in_executor(executor, _sync_call)
    return result

  def _parse_gemini_response(self, response: str) -> dict[str, Any]:
    """Parse Gemini JSON response"""
    try:
      # Extract JSON from response (may have markdown code blocks)
      if "```json" in response:
        start = response.find("```json") + 7
        end = response.find("```", start)
        json_str = response[start:end].strip()
      elif "```" in response:
        start = response.find("```") + 3
        end = response.find("```", start)
        json_str = response[start:end].strip()
      else:
        json_str = response.strip()

      data = json.loads(json_str)

      # Map to our expected format
      risk_level_str = data.get("risk_level", "moderate").upper()
      risk_level = RiskLevel[risk_level_str]

      return {
        "risk_level": risk_level,
        "confidence": float(data.get("confidence", 0.8)),
        "reasoning": data.get("reasoning", "No reasoning provided"),
        "metadata": {
          "purpose": data.get("purpose"),
          "reasons_allow": data.get("reasons_allow", []),
          "reasons_deny": data.get("reasons_deny", []),
          "brakes_violated": data.get("brakes_violated", []),
        },
      }

    except Exception as e:
      print(f"Failed to parse Gemini response: {e}")
      print(f"Raw response: {response}")
      # Fallback
      return {
        "risk_level": RiskLevel.MODERATE,
        "confidence": 0.6,
        "reasoning": "Failed to parse Layer 1 response. Defaulting to MODERATE.",
        "metadata": {"parse_error": str(e), "raw_response": response},
      }

  def _fallback_assessment(
    self, prompt: str, context: dict[str, Any] | None
  ) -> dict[str, Any]:
    """
    Fallback assessment when Gemini is unavailable
    Uses simple heuristics (for development/testing)
    """
    prompt_lower = prompt.lower()

    # Simple keyword-based risk assessment
    catastrophic_keywords = [
      "kill",
      "harm",
      "weapon",
      "bomb",
      "suicide",
      "murder",
      "illegal",
    ]
    critical_keywords = [
      "hack",
      "exploit",
      "vulnerability",
      "password",
      "credit card",
      "ssn",
    ]
    moderate_keywords = ["personal", "private", "sensitive", "confidential"]

    if any(kw in prompt_lower for kw in catastrophic_keywords):
      risk_level = RiskLevel.CATASTROPHIC
      confidence = 0.9
      reasoning = "CATASTROPHIC: Request contains dangerous keywords"
    elif any(kw in prompt_lower for kw in critical_keywords):
      risk_level = RiskLevel.CRITICAL
      confidence = 0.8
      reasoning = "CRITICAL: Request involves security/privacy concerns"
    elif any(kw in prompt_lower for kw in moderate_keywords):
      risk_level = RiskLevel.MODERATE
      confidence = 0.7
      reasoning = "MODERATE: Request involves sensitive information"
    else:
      risk_level = RiskLevel.LOW
      confidence = 0.6
      reasoning = "LOW: No obvious risk indicators detected"

    return {
      "risk_level": risk_level,
      "confidence": confidence,
      "reasoning": reasoning + " (Fallback assessment - Gemini unavailable)",
      "metadata": {"fallback": True},
    }
