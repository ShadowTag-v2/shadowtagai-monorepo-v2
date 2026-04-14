import os
import time
from pathlib import Path

import google.auth
import google.auth.transport.requests
import requests as http_requests
from google.cloud import discoveryengine_v1beta as discoveryengine

PROJECT_ID = os.getenv("GCP_PROJECT", "shadowtag-omega-v2")

# ── LanceDB / Vertex AI config ────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
_LANCEDB_PATH = _REPO_ROOT / "data" / "lancedb" / "workspace_knowledge"
_GCP_PROJECT = os.getenv("GCP_PROJECT_ID", "shadowtag-omega-v4")
_LOCATION = "us-central1"
_EMBED_MODEL = "text-embedding-004"
_VERTEX_URL = (
    f"https://{_LOCATION}-aiplatform.googleapis.com/v1/projects/{_GCP_PROJECT}"
    f"/locations/{_LOCATION}/publishers/google/models/{_EMBED_MODEL}:predict"
)
_TOKEN_CACHE: dict = {"token": None, "expires_at": 0.0}


def _get_access_token() -> str:
    if _TOKEN_CACHE["token"] and time.time() < _TOKEN_CACHE["expires_at"]:
        return _TOKEN_CACHE["token"]
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    req = google.auth.transport.requests.Request()
    creds.refresh(req)
    _TOKEN_CACHE["token"] = creds.token
    _TOKEN_CACHE["expires_at"] = time.time() + 3300
    return creds.token


def _embed_query(text: str) -> list[float] | None:
    token = _get_access_token()
    resp = http_requests.post(
        _VERTEX_URL,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"instances": [{"content": text[:60000]}]},
        timeout=30,
    )
    if resp.status_code != 200:
        return None
    predictions = resp.json().get("predictions", [])
    return predictions[0]["embeddings"]["values"] if predictions else None


def search_lancedb(query: str, top_k: int = 5) -> dict:
    """Embeds query via Vertex AI and searches LanceDB 'documents' + 'code_files' tables.
    Returns merged results ranked by cosine similarity.
    Falls back gracefully if LanceDB is unavailable.
    """
    try:
        import lancedb
    except ImportError:
        return {"results": [], "error": "lancedb not installed"}

    if not _LANCEDB_PATH.exists():
        return {"results": [], "error": f"LanceDB store not found at {_LANCEDB_PATH}"}

    vec = _embed_query(query)
    if vec is None:
        return {"results": [], "error": "embedding failed"}

    db = lancedb.connect(str(_LANCEDB_PATH))
    results = []

    for table_name, label in [("documents", "doc"), ("code_files", "code")]:
        if table_name not in db.table_names():
            continue
        tbl = db.open_table(table_name)
        rows = tbl.search(vec).limit(top_k).to_pandas()
        for _, row in rows.iterrows():
            entry = {
                "source": label,
                "id": str(row.get("id", "")),
                "text": str(row.get("text", ""))[:500],
                "score": float(row.get("_distance", 0.0)),
            }
            if label == "code":
                entry["file_path"] = str(row.get("file_path", ""))
                entry["language"] = str(row.get("language", ""))
            else:
                entry["document_id"] = str(row.get("document_id", ""))
            results.append(entry)

    # Sort by ascending distance (closer = better)
    results.sort(key=lambda r: r["score"])
    return {"results": results[: top_k * 2]}


LOCATION = "global"  # Or 'us-central1'
DATA_STORE_ID = "shadowtag-knowledge-base"  # Placeholder


def search_knowledge_base(query: str):
    """Queries the Vertex AI Search Data Store.
    """
    client = discoveryengine.SearchServiceClient()
    serving_config = client.serving_config_path(
        project=PROJECT_ID,
        location=LOCATION,
        data_store=DATA_STORE_ID,
        serving_config="default_config",
    )

    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=5,
        content_search_spec={
            "snippet_spec": {"return_snippet": True},
            "summary_spec": {"summary_result_count": 5, "include_citations": True},
        },
    )

    response = client.search(request)

    results = []
    for result in response.results:
        results.append(
            {
                "title": result.document.derived_struct_data.get("title"),
                "link": result.document.derived_struct_data.get("link"),
                "snippet": result.document.derived_struct_data.get("snippets")[0].get("snippet")
                if result.document.derived_struct_data.get("snippets")
                else "",
            },
        )

    return {
        "results": results,
        "summary": response.summary.summary_text if response.summary else "",
    }


if __name__ == "__main__":
    # Test query
    print(search_knowledge_base("What is the Omega Protocol?"))
