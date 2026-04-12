"""
Configuration management for UnGPT system
Loads from environment variables with sensible defaults
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file if it exists
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Config:
    """Application configuration"""

    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    XAI_API_KEY: str = os.getenv("XAI_API_KEY", "")

    # System Configuration
    MAX_CONCURRENT_THREADS: int = int(os.getenv("MAX_CONCURRENT_THREADS", "5"))
    ENABLE_COMPLIANCE: bool = os.getenv("ENABLE_COMPLIANCE", "true").lower() == "true"
    STRICT_MODE: bool = os.getenv("STRICT_MODE", "true").lower() == "true"
    AUTO_HALT_ON_VIOLATION: bool = os.getenv("AUTO_HALT_ON_VIOLATION", "true").lower() == "true"

    # Business Judgment Rule Gates
    MAX_COST_PER_QUERY: float = float(os.getenv("MAX_COST_PER_QUERY", "1.0"))
    ROI_THRESHOLD: float = float(os.getenv("ROI_THRESHOLD", "3.0"))
    LTV_CAC_RATIO: float = float(os.getenv("LTV_CAC_RATIO", "4.0"))
    TIME_HORIZON_MONTHS: int = int(os.getenv("TIME_HORIZON_MONTHS", "18"))

    # Voice Settings
    TRANSCRIPTION_ENGINE: str = os.getenv("TRANSCRIPTION_ENGINE", "whisper_local")
    WHISPER_MODEL_SIZE: str = os.getenv("WHISPER_MODEL_SIZE", "base")
    VOICE_LANGUAGE: str = os.getenv("VOICE_LANGUAGE", "en")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    AUDIT_TRAIL_DIR: Path = Path(os.getenv("AUDIT_TRAIL_DIR", "./audit_trails"))

    # xAI Endpoint
    XAI_ENDPOINT: str = os.getenv("XAI_ENDPOINT", "https://api.x.ai/v1/chat/completions")

    # Model Names
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    GPT_MODEL: str = "gpt-4-turbo-preview"
    GROK_MODEL: str = "grok-2-latest"

    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """
        Validate configuration
        Returns (is_valid, missing_keys)
        """
        missing = []

        if not cls.ANTHROPIC_API_KEY:
            missing.append("ANTHROPIC_API_KEY")

        # Optional: Only validate other keys if consensus mode is needed
        # For single-model mode, only Anthropic is required

        # Create audit trail directory if it doesn't exist
        cls.AUDIT_TRAIL_DIR.mkdir(parents=True, exist_ok=True)

        return (len(missing) == 0, missing)

    @classmethod
    def get_summary(cls) -> dict:
        """Get configuration summary (safe for logging - no API keys)"""
        return {
            "max_concurrent_threads": cls.MAX_CONCURRENT_THREADS,
            "enable_compliance": cls.ENABLE_COMPLIANCE,
            "strict_mode": cls.STRICT_MODE,
            "roi_threshold": cls.ROI_THRESHOLD,
            "ltv_cac_ratio": cls.LTV_CAC_RATIO,
            "transcription_engine": cls.TRANSCRIPTION_ENGINE,
            "whisper_model_size": cls.WHISPER_MODEL_SIZE,
            "claude_model": cls.CLAUDE_MODEL,
            "apis_configured": {
                "anthropic": bool(cls.ANTHROPIC_API_KEY),
                "openai": bool(cls.OPENAI_API_KEY),
                "google": bool(cls.GOOGLE_API_KEY),
                "xai": bool(cls.XAI_API_KEY),
            },
        }


# Validate on import
_is_valid, _missing = Config.validate()
if not _is_valid:
    print(f"⚠️  Warning: Missing configuration: {', '.join(_missing)}")
    print("   Set these environment variables or create a .env file")
    print("   See .env.example for template")
