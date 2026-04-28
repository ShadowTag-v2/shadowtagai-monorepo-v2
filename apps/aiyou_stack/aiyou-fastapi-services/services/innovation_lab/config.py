# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Innovation Lab Service Configuration"""

from pydantic_settings import BaseSettings


class InnovationLabConfig(BaseSettings):
    """Configuration for Innovation Lab AI service"""

    # Service metadata
    service_name: str = "Innovation Lab & AI Innovation"
    version: str = "1.0.0"
    description: str = (
        "Experiments with cutting-edge tech. Tries the crazy ideas so you don't have to."
    )

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    # Claude Agent Configuration
    claude_api_key: str | None = None
    claude_model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    temperature: float = 0.8  # Higher temperature for creative ideation

    # Innovation Lab specific settings
    max_ideas_per_request: int = 10
    enable_experimental_features: bool = True
    innovation_focus_areas: list[str] = [
        "AI/ML",
        "Blockchain",
        "Quantum Computing",
        "IoT",
        "AR/VR",
        "Edge Computing",
        "Biotechnology",
        "Robotics",
    ]

    class Config:
        env_file = ".env"
        env_prefix = "INNOVATION_LAB_"
        case_sensitive = False


# Global config instance
config = InnovationLabConfig()
