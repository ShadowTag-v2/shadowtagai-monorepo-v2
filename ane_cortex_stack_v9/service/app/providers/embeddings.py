from __future__ import annotations
from typing import List, Optional
import hashlib
import os
import requests

EMBED_DIM = 1536

def fake_embed(text: str, dim: int = EMBED_DIM) -> list[float]:
    seed = hashlib.sha256(text.encode("utf-8")).digest()
    return [((seed[i % len(seed)] / 255.0) - 0.5) for i in range(dim)]

class Embedder:
    def __init__(
        self,
        provider: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        dim: int = EMBED_DIM,
        timeout_s: int = 30,
    ):
        self.provider = provider or os.getenv("EMBED_PROVIDER", "ollama")
        self.base_url = base_url or os.getenv("EMBED_BASE_URL", "http://localhost:11434/v1")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("EMBED_MODEL", "nomic-embed-text")
        self.dim = dim
        self.timeout_s = timeout_s

    def embed(self, text: str) -> list[float]:
        if self.provider == "fake":
            return fake_embed(text, self.dim)
        if self.provider in {"openai", "openai-compatible"}:
            return self._embed_openai_compatible(text)
        if self.provider == "ollama":
            return self._embed_openai_compatible(text)
        return fake_embed(text, self.dim)

    def _embed_openai_compatible(self, text: str) -> list[float]:
        url = self.base_url.rstrip("/") + "/embeddings"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {"model": self.model, "input": text}
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout_s)
            resp.raise_for_status()
            data = resp.json()
            vec = data["data"][0]["embedding"]
            if len(vec) > self.dim:
                vec = vec[: self.dim]
            elif len(vec) < self.dim:
                vec = vec + [0.0] * (self.dim - len(vec))
            return [float(x) for x in vec]
        except Exception:
            return fake_embed(text, self.dim)

_default_embedder = Embedder()

def embed_text(text: str) -> list[float]:
    return _default_embedder.embed(text)
