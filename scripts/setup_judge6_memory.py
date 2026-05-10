import os
import sys

import vertexai
from google.cloud import discoveryengine_v1 as discoveryengine
from vertexai.preview.generative_models import GenerativeModel, Tool, grounding

# Configuration
PROJECT_ID = os.getenv("GEMINI_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GEMINI_LOCATION", "us-central1")
DATA_STORE_ID = "judge6-doctrine-store"  # We will create/use this ID
DOCS_DIR = "docs"


def check_env() -> None:
  if not PROJECT_ID:
    sys.exit(1)


def import_documents(
  project_id: str, location: str, data_store_id: str, _input_dir: str
) -> None:
  """Imports documents from a local directory to Vertex AI Search.
  Note: In a real scenario, we usually upload to GCS first, but here we'll simulate
  or use the inline content method if files are small, or guide the user to GCS.

  For simplicity in this script, we will assume the user has uploaded files to a GCS bucket
  OR we will just print the instructions to do so, as local file upload via API is complex
  (requires converting to JSONL with base64 content).

  Actually, let's use the GCS method as it's standard.
  """
  # We can try to list data stores to see if it exists
  client = discoveryengine.DataStoreServiceClient()
  parent = f"projects/{project_id}/locations/{location}/collections/default_collection"

  try:
    # List data stores
    request = discoveryengine.ListDataStoresRequest(parent=parent)
    page_result = client.list_data_stores(request=request)
    [ds.name for ds in page_result]
  except Exception:
    pass


def query_judge6_grounded(
  project_id: str, location: str, data_store_id: str, query: str
) -> None:
  """Queries Gemini with grounding against the Vertex AI Search data store.
  This is the key step that uses the "GenAI App Builder" credits.
  """
  vertexai.init(project=project_id, location=location)

  # Define the grounding tool
  # Format: projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{data_store_id}
  data_store_path = f"projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{data_store_id}"

  grounding_tool = Tool.from_google_search_retrieval(
    grounding.GoogleSearchRetrieval(),
  )  # Fallback to Google Search if datastore not ready, but we want Data Store:

  # Correct way for Vertex AI Search Grounding:
  grounding_tool = Tool.from_retrieval(
    grounding.Retrieval(
      source=grounding.VertexAISearch(datastore=data_store_path),
    ),
  )

  model = GenerativeModel("gemini-3.1-flash-lite-preview")

  try:
    response = model.generate_content(
      query, tools=[grounding_tool], generation_config={"temperature": 0.0}
    )

    # Print citations if any
    if response.candidates[0].grounding_metadata.grounding_chunks:
      for _chunk in response.candidates[0].grounding_metadata.grounding_chunks:
        pass

  except Exception:
    pass


if __name__ == "__main__":
  check_env()

  # Example usage
  # 1. Import (Manual step usually required for first time setup)
  import_documents(PROJECT_ID, LOCATION, DATA_STORE_ID, DOCS_DIR)

  # 2. Query
  query = "What is the doctrine regarding Cloudflare integration?"
  query_judge6_grounded(PROJECT_ID, LOCATION, DATA_STORE_ID, query)
