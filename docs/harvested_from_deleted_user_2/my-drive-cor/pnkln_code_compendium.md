# PNKLN Code Compendium (Original Format)

_Generated:_ 2025-10-29T19:40:11

## Index

- `prompts/contract.prompt.txt` — #p-contract (matrix)
- `prompts/lawcal.prompt.txt` — #p-dead
- `prompts/neg.prompt.txt` — #p-neg
- `prompts/risk.prompt.txt` — #p-risk
- `prompts/spec.prompt.txt` — #p-spec
- `scripts/gcs.py` — #p-gcs
- `scripts/ocr.py` — #p-ocr
- `scripts/publish.py` — #p-publish
- `scripts/rag.py` — #p-rag
- `scripts/runners.py` — #p-prompts / #p-runners
- `scripts/util.py` — #p-util
- `scripts/vertex.py` — #p-vertex

---
## Source Code

### prompts/contract.prompt.txt — #p-contract (matrix)

```text
Summarize positions into a two-party matrix with proposed resolutions. Output JSON fields: issues, party_a, party_b, deltas, proposed.
Input:
{{input}}

```
### prompts/lawcal.prompt.txt — #p-dead

```text
Extract legal deadlines & triggers from the text. Output JSON array of objects: event, trigger, deadline_days, jurisdiction, notes.
Input:
{{input}}

```
### prompts/neg.prompt.txt — #p-neg

```text
List open issues and missing terms. Output JSON with fields: missing_terms, conflicting_terms, followups.
Input:
{{input}}

```
### prompts/risk.prompt.txt — #p-risk

```text
Top-5 risks with likelihood (1-5) and mitigation. Output JSON array: risk, likelihood, impact, mitigation.
Input:
{{input}}

```
### prompts/spec.prompt.txt — #p-spec

```text
You are PNKLN Systems. Produce a terse, machine-parseable project plan in JSON. Include objectives, milestones, risks, and owners. Input:
{{input}}

```
### scripts/gcs.py — #p-gcs

```python
"""GCS helpers for PNKLN: simple upload/download/list."""
from __future__ import annotations
from typing import List
from google.cloud import storage

def client(project: str|None=None) -> storage.Client:
    return storage.Client(project=project) if project else storage.Client()

def bucket(name: str, project: str|None=None) -> storage.Bucket:
    return client(project).bucket(name)

def upload_bytes(bkt: str, key: str, data: bytes, content_type: str="application/octet-stream") -> str:
    b = bucket(bkt).blob(key); b.upload_from_string(data, content_type); return f"gs://{bkt}/{key}"

def upload_text(bkt: str, key: str, text: str, content_type: str="text/plain") -> str:
    return upload_bytes(bkt, key, text.encode(), content_type)

def download_bytes(bkt: str, key: str) -> bytes:
    return bucket(bkt).blob(key).download_as_bytes()

def list_keys(bkt: str, prefix: str="") -> List[str]:
    return [b.name for b in bucket(bkt).list_blobs(prefix=prefix)]

```
### scripts/ocr.py — #p-ocr

```python
"""OCR using Cloud Vision and summarization via Gemini."""
from __future__ import annotations
from typing import Iterable, Dict, Any
from google.cloud import vision
from vertexai.generative_models import Part
from .vertex import gemini

_vc = vision.ImageAnnotatorClient()
_gm = gemini()

def ocr_path(path: str) -> str:
    with open(path, "rb") as f:
        img = vision.Image(content=f.read())
    r = _vc.document_text_detection(image=img)
    if r.full_text_annotation and r.full_text_annotation.text:
        return r.full_text_annotation.text
    return r.text_annotations[0].description if r.text_annotations else ""

def summarize_ocr(paths: Iterable[str]) -> str:
    texts = []
    for p in paths:
        try: texts.append(ocr_path(p))
        except Exception: texts.append("")
    joined = "\n\n".join(texts)
    return _gm.generate_content([Part.from_text("Summarize the following OCR content:"), Part.from_text(joined)]).text

```
### scripts/publish.py — #p-publish

```python
"""Publish manifest with section list and optional extra data to GCS."""
from __future__ import annotations
import time, json, os
from .gcs import upload_text

DEFAULT_SECTIONS = ["env","pip","vertex","bucket","paths","util","gcs","gem","emb","ocr","ocr_sum","rag_build","rag_query","batch_sum","prompts","runners","imgcap","ocr_dir","io_api","manifest","harvest","publish","mini_demo","end"]

def publish_manifest(bucket: str, extra: dict|None=None) -> str:
    m = {"sections":DEFAULT_SECTIONS, "ts":int(time.time())}
    if extra: m["extra"]=extra
    key = f"manifests/{m['ts']}.json"
    return upload_text(bucket, key, json.dumps(m, separators=(",",":")), "application/json")

```
### scripts/rag.py — #p-rag

```python
"""Minimal RAG: build embeddings matrix (NPY) + metadata, and answer queries with cosine."""
from __future__ import annotations
from typing import List, Dict, Any
import json, numpy as np
from .vertex import embedding, gemini

_em = embedding()
_gm = gemini()

def build(items: List[Dict[str, Any]], np_out: str, meta_out: str) -> None:
    vecs, meta = [], []
    for it in items:
        e = _em.get_embeddings([it["t"]])[0].values
        vecs.append(np.array(e, dtype=np.float32)); meta.append({"k":it["k"], "t":it["t"]})
    np.save(np_out, np.stack(vecs, 0))
    with open(meta_out,"w",encoding="utf-8") as f: json.dump(meta, f, separators=(",",":"))

def query(q: str, np_path: str, meta_path: str, top: int=3) -> str:
    V = np.load(np_path); M = json.load(open(meta_path))
    e = np.array(_em.get_embeddings([q])[0].values, dtype=np.float32)
    scores = []
    for i in range(len(M)):
        vi = V[i]; s = float(vi.dot(e) / ((np.linalg.norm(vi)*np.linalg.norm(e)) or 1e-9))
        scores.append((i,s))
    scores.sort(key=lambda x: x[1], reverse=True)
    ctx = "\n".join(M[i]["t"] for i,_ in scores[:top])
    return _gm.generate_content(["Use context to answer.\n", ctx, "\nQ:", q]).text

```
### scripts/runners.py — #p-prompts / #p-runners

```python
"""High-level prompt runners and templates."""
from __future__ import annotations
from vertexai.generative_models import Part
from .vertex import gemini

_gm = gemini()
PROMPTS = {
 "spec":"You are PNKLN Systems. Produce a machine-parseable JSON plan.",
 "contract":"Summarize contract positions into his/hers matrix JSON.",
 "lawcal":"Extract deadlines & triggers JSON.",
 "neg":"List open issues, missing terms JSON.",
 "risk":"Top-5 risks JSON with mitigations."
}

def run(tag: str, text: str) -> str:
    tpl = PROMPTS[tag]
    return _gm.generate_content([Part.from_text(tpl), Part.from_text(text)]).text

```
### scripts/util.py — #p-util

```python
"""Utility helpers for PNKLN: IO, hashing, compression, cosine similarity."""
from __future__ import annotations
import json, gzip, hashlib
from typing import Any, Iterable
import numpy as np

def json_dumps(x: Any) -> str:
    """Compact JSON serialization."""
    return json.dumps(x, separators=(",",":"))

def write(path: str, x: Any) -> str:
    """Write bytes/str/obj as bytes to path and return path."""
    if isinstance(x, (bytes, bytearray)):
        data = x
    elif isinstance(x, str):
        data = x.encode()
    else:
        data = json_dumps(x).encode()
    with open(path, "wb") as f: f.write(data)
    return path

def read(path: str) -> bytes:
    """Read file as bytes."""
    with open(path, "rb") as f: return f.read()

def gz_compress(x: Any) -> bytes:
    """Gzip compress any serializable input."""
    if isinstance(x, (bytes, bytearray)):
        data = x
    elif isinstance(x, str):
        data = x.encode()
    else:
        data = json_dumps(x).encode()
    return gzip.compress(data)

def sha256_short(x: Any) -> str:
    """First 16 hex chars of sha256 for content addressing."""
    if not isinstance(x, (bytes, bytearray)):
        x = x.encode() if isinstance(x, str) else json_dumps(x).encode()
    return hashlib.sha256(x).hexdigest()[:16]

def cosine(a: Iterable[float], b: Iterable[float]) -> float:
    """Cosine similarity between 1-D vectors."""
    a = np.asarray(list(a)); b = np.asarray(list(b))
    denom = (np.linalg.norm(a)*np.linalg.norm(b)) or 1e-9
    return float(a.dot(b)/denom)

```
### scripts/vertex.py — #p-vertex

```python
"""Vertex AI init and model accessors."""
from __future__ import annotations
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.language_models import TextEmbeddingModel

def init(project: str, location: str="us-central1") -> None:
    vertexai.init(project=project, location=location)

def gemini(model: str="gemini-1.5-flash") -> GenerativeModel:
    return GenerativeModel(model)

def embedding(model: str="text-embedding-005") -> TextEmbeddingModel:
    return TextEmbeddingModel.from_pretrained(model)

```