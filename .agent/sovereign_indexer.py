import logging
import os

import chromadb
from chromadb.api.types import Documents, Embeddings
from google import genai

# Setup SIEM-compliant logging
logging.basicConfig(
  level=logging.INFO,
  format='{"time": "%(asctime)s", "component": "SovereignIndexer", "message": "%(message)s"}',
)
logger = logging.getLogger(__name__)


class VertexEmbeddingFunction(chromadb.EmbeddingFunction):
  """Custom embedding function routing strictly through FedRAMP-authorized Vertex AI."""

  def __init__(self, project_id: str, location: str = "us-central1"):
    self.client = genai.Client(vertexai=True, project=project_id, location=location)
    self.model = "text-embedding-004"  # GCP's state-of-the-art embedding model

  def __call__(self, input: Documents) -> Embeddings:
    response = self.client.models.embed_content(
      model=self.model,
      contents=input,
    )
    # Handle batch embedding responses
    return [embedding.values for embedding in response.embeddings]


class SovereignRAG:
  def __init__(self, workspace_path: str, project_id: str):
    self.workspace = workspace_path
    self.db_path = os.path.join(workspace_path, ".rag_index")

    # Initialize Vector DB strictly on the GCS FUSE mount
    self.chroma_client = chromadb.PersistentClient(path=self.db_path)
    self.embed_fn = VertexEmbeddingFunction(project_id=project_id)

    self.collection = self.chroma_client.get_or_create_collection(
      name="antigravity_codebase", embedding_function=self.embed_fn
    )

  def _chunk_text(self, text: str, chunk_size: int = 1500) -> list[str]:
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

  def index_workspace(self):
    """Sweeps the FUSE mount and indexes code deterministically."""
    logger.info("Initiating zero-egress workspace sweep...")

    valid_extensions = {".py", ".ts", ".js", ".md", ".json", ".tf", ".yaml"}
    files_to_index = []

    for root, _, files in os.walk(self.workspace):
      if ".git" in root or ".agent" in root or "node_modules" in root:
        continue
      for file in files:
        if os.path.splitext(file)[1] in valid_extensions:
          files_to_index.append(os.path.join(root, file))

    docs, metadatas, ids = [], [], []

    for file_path in files_to_index:
      try:
        with open(file_path, encoding="utf-8") as f:
          content = f.read()

        chunks = self._chunk_text(content)
        for i, chunk in enumerate(chunks):
          docs.append(chunk)
          metadatas.append({"file": file_path, "chunk": i})
          ids.append(f"{file_path}_{i}")
      except Exception as e:
        logger.warning(f"Could not read {file_path}: {e}")

    if docs:
      # Upsert into FUSE-backed ChromaDB
      self.collection.upsert(documents=docs, metadatas=metadatas, ids=ids)
      logger.info(
        f"Successfully indexed {len(docs)} chunks across {len(files_to_index)} files."
      )
    else:
      logger.info("Workspace is empty or fully indexed.")

  def query(self, intent: str, n_results: int = 5) -> str:
    """Retrieves exact architectural context for Gemini 3.1 Flash Lite."""
    results = self.collection.query(query_texts=[intent], n_results=n_results)

    context = "RETRIEVED CODEBASE CONTEXT:\n"
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
      context += f"\n--- File: {meta['file']} ---\n{doc}\n"
    return context


if __name__ == "__main__":
  project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
  indexer = SovereignRAG(workspace_path="/workspace", project_id=project_id)
  indexer.index_workspace()
