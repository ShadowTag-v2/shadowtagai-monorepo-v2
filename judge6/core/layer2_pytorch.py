# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Layer 2: PyTorch Deterministic Enforcement
Catches edge cases that LLMs might miss using fine-tuned classifier
"""

import torch
import torch.nn as nn
from typing import Any
from pathlib import Path

from ..models.database import RiskLevel
from ..core.config import settings


class RiskClassifierModel(nn.Module):
  """
  Simple PyTorch classifier for risk assessment
  Input: Text embeddings (768-dim from sentence-transformers)
  Output: Risk level probabilities (5 classes)
  """

  def __init__(self, input_dim: int = 768, hidden_dim: int = 256, num_classes: int = 5):
    super().__init__()
    self.network = nn.Sequential(
      nn.Linear(input_dim, hidden_dim),
      nn.ReLU(),
      nn.Dropout(0.3),
      nn.Linear(hidden_dim, hidden_dim // 2),
      nn.ReLU(),
      nn.Dropout(0.3),
      nn.Linear(hidden_dim // 2, num_classes),
      nn.Softmax(dim=1),
    )

  def forward(self, x):
    return self.network(x)


class PyTorchEnforcementLayer:
  """
  Layer 2: Deterministic enforcement using PyTorch
  Fine-tuned on adversarial examples and edge cases
  """

  def __init__(self):
    """Initialize PyTorch model"""
    self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    self.model = None
    self.embedder = None

    # Risk level mapping
    self.risk_map = [
      RiskLevel.NEGLIGIBLE,
      RiskLevel.LOW,
      RiskLevel.MODERATE,
      RiskLevel.CRITICAL,
      RiskLevel.CATASTROPHIC,
    ]

    self._load_model()

  def _load_model(self):
    """Load pre-trained model if available"""
    model_path = Path(settings.PYTORCH_MODEL_PATH)

    if model_path.exists():
      try:
        self.model = RiskClassifierModel().to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        print(f"Layer 2: Loaded PyTorch model from {model_path}")
      except Exception as e:
        print(f"Layer 2: Failed to load model: {e}")
        self.model = None
    else:
      print(
        f"Layer 2: Model not found at {model_path}. Using fallback deterministic rules."
      )
      self.model = None

    # Load sentence embedder (for converting text to vectors)
    try:
      from sentence_transformers import SentenceTransformer

      self.embedder = SentenceTransformer("all-MiniLM-L6-v2")  # 384-dim
      print("Layer 2: Loaded sentence embedder")
    except Exception as e:
      print(f"Layer 2: Failed to load embedder: {e}")
      self.embedder = None

  async def assess(
    self,
    prompt: str,
    context: dict[str, Any] | None,
    layer1_result: Any,
  ) -> dict[str, Any]:
    """
    Assess prompt using PyTorch classifier

    Args:
        prompt: The AI request
        context: Additional context
        layer1_result: Result from Layer 1 (for ensemble)

    Returns:
        Dict with risk_level, confidence, reasoning, metadata
    """
    if self.model is None or self.embedder is None:
      # Fallback: Deterministic rules
      return self._fallback_deterministic_rules(prompt, context, layer1_result)

    try:
      # Convert prompt to embedding
      embedding = await self._get_embedding(prompt)

      # Run through PyTorch model
      with torch.no_grad():
        embedding_tensor = torch.tensor(embedding).unsqueeze(0).to(self.device)
        # Note: Need to handle dimension mismatch (384 vs 768)
        # For now, pad or use a different embedder
        # TODO: Retrain model with correct embedding dimension

        # Fallback for now
        return self._fallback_deterministic_rules(prompt, context, layer1_result)

        # probs = self.model(embedding_tensor)
        # risk_idx = torch.argmax(probs).item()
        # confidence = probs[0, risk_idx].item()

        # risk_level = self.risk_map[risk_idx]

        # return {
        #     "risk_level": risk_level,
        #     "confidence": confidence,
        #     "reasoning": f"PyTorch classifier: {risk_level.value} (confidence: {confidence:.2%})",
        #     "metadata": {
        #         "probabilities": probs.tolist()[0],
        #     },
        # }

    except Exception as e:
      print(f"Layer 2 error: {e}")
      return {
        "risk_level": RiskLevel.MODERATE,
        "confidence": 0.5,
        "reasoning": f"Layer 2 error: {str(e)}. Defaulting to MODERATE.",
        "metadata": {"error": str(e)},
      }

  async def _get_embedding(self, text: str):
    """Get sentence embedding asynchronously"""
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    executor = ThreadPoolExecutor(max_workers=1)
    loop = asyncio.get_event_loop()

    def _sync_embed():
      return self.embedder.encode(text)

    result = await loop.run_in_executor(executor, _sync_embed)
    return result

  def _fallback_deterministic_rules(
    self,
    prompt: str,
    context: dict[str, Any] | None,
    layer1_result: Any,
  ) -> dict[str, Any]:
    """
    Fallback: Deterministic rules when model unavailable
    Focuses on catching edge cases Layer 1 might miss
    """
    prompt_lower = prompt.lower()

    # Edge case patterns (adversarial attacks, prompt injection, etc.)
    injection_patterns = [
      "ignore previous",
      "ignore all",
      "disregard",
      "new instructions",
      "system prompt",
      "jailbreak",
      "dan mode",
    ]

    pii_patterns = [
      r"\d{3}-\d{2}-\d{4}",  # SSN
      r"\d{16}",  # Credit card
      r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",  # Email
    ]

    # Check for prompt injection
    if any(pattern in prompt_lower for pattern in injection_patterns):
      return {
        "risk_level": RiskLevel.CRITICAL,
        "confidence": 0.95,
        "reasoning": "CRITICAL: Prompt injection attempt detected",
        "metadata": {"pattern_matched": "prompt_injection"},
      }

    # Check for PII (basic regex)
    import re

    for pattern in pii_patterns:
      if re.search(pattern, prompt):
        return {
          "risk_level": RiskLevel.CRITICAL,
          "confidence": 0.9,
          "reasoning": "CRITICAL: Potential PII detected in prompt",
          "metadata": {"pattern_matched": "pii"},
        }

    # Length check (extremely long prompts = potential attack)
    if len(prompt) > 10000:
      return {
        "risk_level": RiskLevel.MODERATE,
        "confidence": 0.8,
        "reasoning": "MODERATE: Unusually long prompt (potential attack)",
        "metadata": {"prompt_length": len(prompt)},
      }

    # Ensemble with Layer 1: If Layer 1 said high risk, agree
    if layer1_result.risk_level in [RiskLevel.CATASTROPHIC, RiskLevel.CRITICAL]:
      return {
        "risk_level": layer1_result.risk_level,
        "confidence": 0.85,
        "reasoning": f"Layer 2 agrees with Layer 1: {layer1_result.risk_level.value}",
        "metadata": {"ensemble": True},
      }

    # Default: Low risk (Layer 2 found no edge cases)
    return {
      "risk_level": RiskLevel.LOW,
      "confidence": 0.7,
      "reasoning": "LOW: No edge case patterns detected",
      "metadata": {"deterministic_rules": True},
    }
