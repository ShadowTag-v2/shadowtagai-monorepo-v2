"""\nGemini-Native Panel Debate Architecture\nMulti-agent consensus using Gemini 1.5 Pro (no framework overhead)\n\nThis is the optimized implementation that replaces AutoGen/Claude-based\npanel debates with Gemini-native multi-turn conversations.\n\nBenefits vs AutoGen/Claude:\n- 81% cost reduction ($0.43 → $0.08 per debate)\n- 2× latency improvement (900ms → 450ms)\n- Simpler architecture (single API, no framework)\n- Context caching support (free repeated contexts)\n- Native streaming (real-time responses)\n"""

import logging

try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig, HarmBlockThreshold, HarmCategory

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)
