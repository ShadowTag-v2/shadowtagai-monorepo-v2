"""Configuration management for multi-model LLM serving."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ModelConfig(BaseSettings):
    """Configuration for individual models."""

    name: str
    model_path: str
    max_model_len: int = 4096
    gpu_memory_utilization: float = 0.85
    tensor_parallel_size: int = 1
    trust_remote_code: bool = True
    dtype: str = "auto"
    quantization: str | None = None

    # Model-specific optimizations
    enable_prefix_caching: bool = True
    enable_chunked_prefill: bool = True
    max_num_batched_tokens: int | None = None
    max_num_seqs: int = 256


class AegaeonPoolingConfig(BaseSettings):
    """Aegaeon-inspired GPU pooling configuration."""

    # Token-level scheduling
    enable_token_level_scheduling: bool = True
    token_budget_per_gpu: int = 32768  # Tokens per GPU
    preemption_mode: str = "recompute"  # recompute or swap

    # Multi-model pooling
    max_models_per_gpu: int = 7
    model_loading_strategy: str = "lazy"  # lazy or eager

    # Auto-scaling
    enable_auto_scaling: bool = True
    scale_up_threshold: float = 0.8  # GPU utilization
    scale_down_threshold: float = 0.3
    cooldown_seconds: int = 60


class ServerConfig(BaseSettings):
    """Main server configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Allow extra fields in .env
    )

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # Model registry
    models: dict[str, ModelConfig] = Field(default_factory=dict)

    # Pooling configuration
    pooling: AegaeonPoolingConfig = Field(default_factory=AegaeonPoolingConfig)

    # Ray configuration
    ray_address: str | None = None  # None = local, or ray://...
    ray_namespace: str = "ShadowTag-v2-serving"

    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    log_level: str = "INFO"

    # API keys for external models (e.g., Google AI Studio)
    google_api_key: str | None = None
    openai_api_key: str | None = None

    # Redis for state management
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # --- Agent Swarm Configuration (Added for Antigravity Upgrade) ---
    AGENT_NAME: str = "minion"
    GEMINI_MODEL_NAME: str = "gemini-1.5-pro-002"
    JUDGE6_ENABLED: bool = True
    CORPUS_GUARD_ENABLED: bool = True
    ARTIFACTS_DIR: str = "artifacts"
    LOGS_DIR: str = "artifacts/logs"


# Default model configurations
DEFAULT_MODELS = {
    "deepseek-v3.2-exp": ModelConfig(
        name="deepseek-v3.2-exp",
        model_path="deepseek-ai/DeepSeek-V3.2-Exp",
        max_model_len=128000,
        gpu_memory_utilization=0.85,
        enable_prefix_caching=True,
        enable_chunked_prefill=True,
    ),
    "deepseek-ocr": ModelConfig(
        name="deepseek-ocr",
        model_path="deepseek-ai/DeepSeek-OCR",
        max_model_len=8192,
        gpu_memory_utilization=0.7,
    ),
    "qwen2.5-72b": ModelConfig(
        name="qwen2.5-72b",
        model_path="Qwen/Qwen2.5-72B-Instruct",
        max_model_len=32768,
        tensor_parallel_size=2,
    ),
}


def get_settings() -> ServerConfig:
    """Get server settings with default models."""
    settings = ServerConfig()
    if not settings.models:
        settings.models = DEFAULT_MODELS
    return settings


# Global settings instance for agent usage
settings = get_settings()
