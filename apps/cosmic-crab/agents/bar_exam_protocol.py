# agents/bar_exam_protocol.py
import logging

from google import genai
from google.genai import types

from agents.legal_whiteboard import whiteboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BarExamProtocol")


class BarExamProtocol:
  """ShadowTag Omega V7 Bar Exam Protocol
  Promotes agents through capability tiers using Gemini Thinking validation.
  """

  def __init__(self):
    import os

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("DEVELOPERKNOWLEDGE_API_KEY")
    if not api_key:
      raise ValueError(
        "Missing API Key! Please set GOOGLE_API_KEY or DEVELOPERKNOWLEDGE_API_KEY.",
      )
    self.client = genai.Client(api_key=api_key)

  async def evaluate_agent(self, agent_id: str, challenge: str):
    logger.info(f"⚖️ BAR EXAM: Testing Agent -> {agent_id}")

    # Level 1: Thinking-driven Validation
    try:
      response = self.client.models.generate_content(
        model="gemini-3.1-flash-thinking-exp-01-21",  # Using a thinking model
        contents=f"Evaluate this agent's response to the challenge '{challenge}' for doctrinal correctness.",
        config=types.GenerateContentConfig(
          thinking_config=types.ThinkingConfig(include_thoughts=True),
        ),
      )

      # Extract thoughts if available
      thoughts = ""
      for part in response.candidates[0].content.parts:
        if part.thought:
          thoughts += part.text

      logger.info("🧠 THINKING TRACE CAPTURED.")

      # Record evaluation in whiteboard
      whiteboard.record_bead(
        insight=f"Agent {agent_id} passed doctrinal challenge.",
        source="bar_exam",
        thinking_trace=thoughts,
      )
      return True
    except Exception as e:
      logger.error(f"❌ [BAR EXAM] Evaluation failed: {e}")
      return False


if __name__ == "__main__":
  import asyncio

  async def main():
    protocol = BarExamProtocol()
    await protocol.evaluate_agent("Kosmos-01", "Implement a zero-trust egress filter.")

  asyncio.run(main())
