"""
VCR Record/Replay Subsystem
Provides deterministic test reproduction by recording API/Tool interactions and replaying them.
"""

import json
import os
import hashlib
from typing import Any


class VCRReplay:
    def __init__(self, cassette_dir: str = ".cassettes"):
        from config.feature_flags import flags
        self.cassette_dir = cassette_dir
        os.makedirs(self.cassette_dir, exist_ok=True)
        vcr_mode = flags.get_string("vcr_mode", default="off")
        self.recording = vcr_mode == "record"
        self.replaying = vcr_mode == "replay"

    def _hash_request(self, method: str, kwargs: dict[str, Any]) -> str:
        payload = json.dumps({"method": method, "kwargs": kwargs}, sort_keys=True).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def _get_cassette_path(self, req_hash: str) -> str:
        return os.path.join(self.cassette_dir, f"{req_hash}.json")

    def intercept(self, method: str, kwargs: dict[str, Any], execute_fn: callable) -> Any:
        # Sanitize kwargs for secrets before hashing and saving
        sanitized_kwargs = self._sanitize_secrets(kwargs)

        req_hash = self._hash_request(method, sanitized_kwargs)
        cassette_path = self._get_cassette_path(req_hash)

        if self.replaying and os.path.exists(cassette_path):
            with open(cassette_path) as f:
                return json.load(f)["response"]

        # Execute actual network/tool logic
        response = execute_fn()

        if self.recording:
            with open(cassette_path, "w") as f:
                json.dump({"request": {"method": method, "kwargs": sanitized_kwargs}, "response": response}, f, indent=2)

        return response

    def _sanitize_secrets(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Strip sensitive tokens from recorded cassettes."""
        sanitized = dict(kwargs)
        for key in ["token", "api_key", "password", "secret", "authorization"]:
            if key in sanitized:
                sanitized[key] = "[REDACTED]"
            # Also check nested headers if present
            if "headers" in sanitized and isinstance(sanitized["headers"], dict):
                for h_key in sanitized["headers"]:
                    if h_key.lower() == "authorization":
                        sanitized["headers"][h_key] = "[REDACTED]"
        return sanitized
