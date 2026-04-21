"""Configuration for the DSPy Swarm Router."""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SwarmEndpoint:
    """A model endpoint in the swarm."""
    name: str
    host: str
    port: int
    model_id: str
    role: str  # "sidekick" | "auditor" | "sovereign"
    max_tokens: int = 4096
    temperature: float = 0.7


@dataclass
class SwarmConfig:
    """Top-level swarm configuration."""
    endpoints: list[SwarmEndpoint] = field(default_factory=list)
    fallback_model: str = "gemini-3.1-flash-lite-preview"
    timeout_seconds: int = 30
    retry_count: int = 3

    def get_endpoint(self, role: str) -> SwarmEndpoint | None:
        """Get the first endpoint matching a role."""
        return next((e for e in self.endpoints if e.role == role), None)
