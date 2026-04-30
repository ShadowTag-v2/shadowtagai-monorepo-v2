"""VCR interception layer for queryWithModel."""

import json
import os
import hashlib
from typing import Any, Dict, Callable

class VCRInterceptor:
    """Intercepts and records/replays model queries."""

    def __init__(self, cassette_dir: str = ".cassettes", record_mode: str = "once"):
        """
        Initialize the VCR interceptor.
        
        Args:
            cassette_dir (str): Directory to store cassettes.
            record_mode (str): Mode for recording ('once', 'all', 'none').
        """
        self.cassette_dir = cassette_dir
        self.record_mode = record_mode
        self._is_replay = False
        os.makedirs(self.cassette_dir, exist_ok=True)

    def enable_replay(self) -> None:
        """Enable replay mode."""
        self._is_replay = True

    def _get_hash(self, prompt: str, model: str) -> str:
        """Generate a unique hash for the query."""
        content = f"{model}:{prompt}".encode("utf-8")
        return hashlib.sha256(content).hexdigest()

    def _get_cassette_path(self, query_hash: str) -> str:
        """Get the file path for a given cassette hash."""
        return os.path.join(self.cassette_dir, f"vcr_{query_hash}.json")

    def queryWithModel(self, prompt: str, model: str, original_func: Callable[..., Any], **kwargs: Any) -> Any:
        """
        Intercept the queryWithModel call.
        
        Args:
            prompt (str): The prompt being queried.
            model (str): The model being used.
            original_func (Callable): The original query function to call on cache miss.
            kwargs: Additional arguments for the original function.
            
        Returns:
            Any: The response from the model or cassette.
        """
        query_hash = self._get_hash(prompt, model)
        cassette_path = self._get_cassette_path(query_hash)

        if self._is_replay or self.record_mode == "none":
            if os.path.exists(cassette_path):
                with open(cassette_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            if self._is_replay:
                raise ValueError(f"Cassette not found for query in replay mode: {query_hash}")

        # Execute original function
        response = original_func(prompt=prompt, model=model, **kwargs)

        # Record if appropriate
        if self.record_mode == "all" or (self.record_mode == "once" and not os.path.exists(cassette_path)):
            with open(cassette_path, "w", encoding="utf-8") as f:
                json.dump(response, f, ensure_ascii=False, indent=2)

        return response
