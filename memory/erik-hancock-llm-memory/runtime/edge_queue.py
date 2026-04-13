"""
EdgeQueue: HCQ-inspired command batching for CloudFlare Workers
Combines WebGPU's ergonomics with HCQ's performance patterns
"""

from dataclasses import dataclass
from typing import Any
import time
import hashlib
import requests


@dataclass
class EdgeCommand:
    """Single command in queue (analogous to GPU command)"""

    type: str  # 'wait', 'exec', 'signal', 'timestamp'
    args: dict[str, Any]


class EdgeSignal:
    """
    Durable Object-backed synchronization primitive
    Analog to HCQSignal (GPU memory-mapped signal)
    """

    def __init__(self, durable_object_id: str):
        self.do_id = durable_object_id
        self.base_url = f"https://signals.judge6.workers.dev/{durable_object_id}"

        # Local cache (reduce DO reads)
        self._value_cache = 0
        self._timestamp_cache = 0
        self._cache_timestamp_ms = 0
        self._cache_ttl_ms = 100  # 100ms cache lifetime

    @property
    def value(self) -> int:
        """Read signal value (cached to reduce DO latency)"""
        now_ms = time.time() * 1000

        # Use cache if fresh
        if (now_ms - self._cache_timestamp_ms) < self._cache_ttl_ms:
            return self._value_cache

        # Fetch from Durable Object
        try:
            response = requests.get(f"{self.base_url}/value", timeout=1.0)
            if response.ok:
                self._value_cache = int(response.text)
                self._cache_timestamp_ms = now_ms
        except Exception:
            pass  # Fallback to cache on error

        return self._value_cache

    def timestamp(self) -> int:
        """Get timestamp in microseconds"""
        try:
            response = requests.get(f"{self.base_url}/timestamp", timeout=1.0)
            return int(response.text)
        except Exception:
            return 0

    def wait(self, value: int, timeout_ms: int = 30000):
        """Block until signal.value >= value"""
        start_ms = time.time() * 1000

        while self.value < value:
            elapsed_ms = time.time() * 1000 - start_ms
            if elapsed_ms > timeout_ms:
                raise TimeoutError(
                    f"Signal wait timeout: {timeout_ms}ms exceeded. "
                    f"Expected value={value}, got value={self.value}"
                )
            time.sleep(0.001)  # 1ms poll interval


class PolicyWASM:
    """
    Cached WASM policy module
    Analog to HCQProgram (compiled GPU kernel)
    """

    def __init__(self, policy_name: str, wasm_binary: bytes):
        self.name = policy_name
        self.wasm = wasm_binary
        self.hash = hashlib.sha256(wasm_binary).hexdigest()[:16]

    @classmethod
    def load_precompiled(cls, policy_name: str) -> "PolicyWASM":
        """Load pre-compiled WASM from R2 cache (Simulated)"""
        # In prototype, we just use dummy bytes
        return cls(policy_name=policy_name, wasm_binary=b"DUMMY_WASM_BYTES")


class EdgeQueue:
    """
    Hardware Command Queue for CloudFlare Workers
    """

    def __init__(self):
        self.commands: list[EdgeCommand] = []
        self._submitted = False

    def wait(self, signal: EdgeSignal, value: int) -> "EdgeQueue":
        """Enqueue wait command"""
        if self._submitted:
            raise RuntimeError("Cannot modify queue after submit()")

        self.commands.append(
            EdgeCommand(type="wait", args={"signal_id": signal.do_id, "value": value})
        )
        return self

    def exec(self, policy: PolicyWASM, context: dict[str, Any]) -> "EdgeQueue":
        """Enqueue WASM policy execution"""
        if self._submitted:
            raise RuntimeError("Cannot modify queue after submit()")

        self.commands.append(
            EdgeCommand(
                type="exec",
                args={
                    "policy_name": policy.name,
                    "policy_hash": policy.hash,
                    "wasm": policy.wasm.hex(),
                    "context": context,
                },
            )
        )
        return self

    def signal(self, signal: EdgeSignal, value: int) -> "EdgeQueue":
        """Enqueue signal write"""
        if self._submitted:
            raise RuntimeError("Cannot modify queue after submit()")

        self.commands.append(
            EdgeCommand(type="signal", args={"signal_id": signal.do_id, "value": value})
        )
        return self

    def timestamp(self, signal: EdgeSignal) -> "EdgeQueue":
        """Enqueue timestamp capture"""
        if self._submitted:
            raise RuntimeError("Cannot modify queue after submit()")

        self.commands.append(EdgeCommand(type="timestamp", args={"signal_id": signal.do_id}))
        return self

    def submit(self, worker_url: str) -> dict[str, Any]:
        """Submit queue to Worker (SINGLE HTTP request)"""
        if self._submitted:
            raise RuntimeError("Queue already submitted")

        self._submitted = True

        payload = {"commands": [{"type": cmd.type, "args": cmd.args} for cmd in self.commands]}

        start_us = time.time() * 1_000_000

        response = requests.post(
            f"{worker_url}/execute_queue",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5.0,
        )

        end_us = time.time() * 1_000_000

        if not response.ok:
            raise RuntimeError(f"Queue execution failed: {response.status_code} {response.text}")

        result = response.json()
        result["queue_latency_us"] = end_us - start_us

        return result
