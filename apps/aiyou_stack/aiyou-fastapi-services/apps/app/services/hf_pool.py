"""
Hugging Face Client Pool
Rotates politely; does NOT evade rate limits.
"""

import logging
import random
import time

import httpx
from fastapi import HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class HFEndpoint(BaseModel):
    name: str
    api_key: str
    model_id: str
    timeout_s: int = 30
    rpm_budget: int = 30  # per-endpoint soft budget
    last_minute_count: int = 0
    window_epoch: float = time.time()


class HFClientPool:
    def __init__(self, endpoints: list[HFEndpoint]):
        self.endpoints = endpoints

    def _throttle(self, ep: HFEndpoint):
        now = time.time()
        if now - ep.window_epoch >= 60:
            ep.window_epoch = now
            ep.last_minute_count = 0
        return not ep.last_minute_count >= ep.rpm_budget

    def _pick(self) -> HFEndpoint | None:
        random.shuffle(self.endpoints)  # simple spread
        for ep in self.endpoints:
            if self._throttle(ep):
                return ep
        # if all are hot, pick the soonest-to-reset
        if not self.endpoints:
            return None
        return min(self.endpoints, key=lambda e: e.window_epoch)

    async def text_generate(self, prompt: str, **gen_kwargs) -> str:
        ep = self._pick()
        if not ep:
            raise HTTPException(503, "No available HF endpoints")

        headers = {"Authorization": f"Bearer {ep.api_key}"}
        url = f"https://api-inference.huggingface.co/models/{ep.model_id}"
        payload = {"inputs": prompt, "parameters": gen_kwargs}

        try:
            async with httpx.AsyncClient(timeout=ep.timeout_s) as client:
                r = await client.post(url, headers=headers, json=payload)
                if r.status_code == 429:
                    logger.warning(f"Rate limited by HF endpoint {ep.name}")
                    # Mark as exhausted for now? Or just retry?
                    # For simplicity, we just raise for now or let the caller handle retry logic
                    raise HTTPException(429, "Rate limited by HF endpoint")
                r.raise_for_status()
                ep.last_minute_count += 1
                data = r.json()
                # Normalized extraction
                if isinstance(data, list) and data and "generated_text" in data[0]:
                    return data[0]["generated_text"]
                if isinstance(data, dict) and "generated_text" in data:
                    return data["generated_text"]
                # Fallback: raw string
                return str(data)
        except Exception as e:
            logger.error(f"HF error on {ep.name}: {e}")
            raise HTTPException(500, f"HF error on {ep.name}: {e}")
