# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""LLM Client Factory"""

# Conditional imports to avoid hard crashes if packages missing,
# though they are expected in this environment
try:
    from langchain_google_genai import ChatGoogleGenerativeAI

    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False

try:
    from langchain_openai import ChatOpenAI

    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

from app.config import get_settings

settings = get_settings()


def get_cheap_llm(temperature: float = 0.0):
    """Returns the 'Tier 0' cheap model (Gemini Flash).
    Fails over to OpenAI if configured/needed, or raises error.
    """
    if HAS_GOOGLE and settings.gemini_api_key:
        return ChatGoogleGenerativeAI(
            model=settings.gemini_model or "gemini-3.1-flash-lite-preview",
            google_api_key=settings.gemini_api_key,
            temperature=temperature,
            convert_system_message_to_human=True,
        )

    # Fallback to OpenAI if configured (e.g. gpt-4o-mini or similar cheap model)
    if HAS_OPENAI and settings.openai_api_key:
        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.openai_api_key,
            temperature=temperature,
        )

    raise RuntimeError("No cheap LLM provider configured (Gemini or OpenAI)")


def get_strong_llm(temperature: float = 0.0):
    """Returns the 'Tier 2' strong model (GPT-4o or similar)."""
    if HAS_OPENAI and settings.openai_api_key:
        return ChatOpenAI(model="gpt-4o", api_key=settings.openai_api_key, temperature=temperature)

    # Fallback to strongest available Gemini
    if HAS_GOOGLE and settings.gemini_api_key:
        return ChatGoogleGenerativeAI(
            model="gemini-3.1-flash-lite-preview",
            google_api_key=settings.gemini_api_key,
            temperature=temperature,
            convert_system_message_to_human=True,
        )

    raise RuntimeError("No strong LLM provider configured (OpenAI or Gemini)")
