import logging
from typing import Any

# Antigravity/ShadowTag Cloud Native Pivot
# Standardizing on in-memory storage for "Easy Button" simplicity.
# Valkey/Redis dependencies are removed to align with Google-managed only strategy.


class CacheStore:
    """Abstracted Cache/Memory layer for the Antigravity Swarm.
    Defaults to Memorystore for Valkey in production.
    """

    def __init__(self):
        self._data: dict[str, str] = {}
        logging.info("///▞ CACHE :: Initialized In-Memory Storage")

    @property
    def is_available(self) -> bool:
        return True

    def get(self, key: str) -> str | None:
        return self._data.get(key)

    def set(self, key: str, value: Any, ex: int | None = None) -> None:
        # Note: TTL (ex) is ignored in this simple in-memory implementation
        self._data[key] = str(value)

    def incr(self, key: str) -> int:
        current = self._data.get(key, "0")
        try:
            val = int(current) + 1
        except (ValueError, TypeError):
            val = 1

        self._data[key] = str(val)
        return val

    def publish(self, channel: str, message: str) -> None:
        """Standard pub/sub simulator."""
        logging.debug(f"///▞ CACHE [PUB] :: {channel} -> {message}")

    def delete(self, key: str) -> None:
        if key in self._data:
            del self._data[key]


# Singleton global instance for the swarm
cache = CacheStore()
