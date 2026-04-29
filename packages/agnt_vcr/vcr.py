"""
VCR Record/Replay Subsystem
Provides deterministic test reproduction by recording API/Tool interactions and replaying them.
"""
import json
import os
import hashlib
from typing import Any, Dict, Optional

class VCRReplay:
    def __init__(self, cassette_dir: str = ".cassettes"):
        self.cassette_dir = cassette_dir
        os.makedirs(self.cassette_dir, exist_ok=True)
        self.recording = os.environ.get("AGNT_VCR_RECORD") == "1"
        self.replaying = os.environ.get("AGNT_VCR_REPLAY") == "1"
        
    def _hash_request(self, method: str, kwargs: Dict[str, Any]) -> str:
        payload = json.dumps({"method": method, "kwargs": kwargs}, sort_keys=True).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def _get_cassette_path(self, req_hash: str) -> str:
        return os.path.join(self.cassette_dir, f"{req_hash}.json")

    def intercept(self, method: str, kwargs: Dict[str, Any], execute_fn: callable) -> Any:
        req_hash = self._hash_request(method, kwargs)
        cassette_path = self._get_cassette_path(req_hash)
        
        if self.replaying and os.path.exists(cassette_path):
            with open(cassette_path, "r") as f:
                return json.load(f)["response"]
                
        # Execute actual network/tool logic
        response = execute_fn()
        
        if self.recording:
            with open(cassette_path, "w") as f:
                json.dump({"request": {"method": method, "kwargs": kwargs}, "response": response}, f, indent=2)
                
        return response
