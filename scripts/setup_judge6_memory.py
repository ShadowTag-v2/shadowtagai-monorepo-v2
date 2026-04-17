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


def check_env():
    if not PROJECT_ID:
        print("❌ Error: GEMINI_PROJECT_ID or GOOGLE_CLOUD_PROJECT environment variable not set.")
        sys.exit(1)
    print(f"✅ Using Project: {PROJECT_ID}")
    print(f"✅ Using Location: {LOCATION}")


def import_documents(project_id: str, location: str, data_store_id: str, input_dir: str):
    """
    Imports documents from a local directory to Vertex AI Search.
    Note: In a real scenario, we usually upload to GCS first, but here we'll simulate
    or use the inline content method if files are small, or guide the user to GCS.

    For simplicity in this script, we will assume the user has uploaded files to a GCS bucket
    OR we will just print the instructions to do so, as local file upload via API is complex
    (requires converting to JSONL with base64 content).

    Actually, let's use the GCS method as it's standard.
    """
    print(f"\n--- 1. Data Ingestion for {data_store_id} ---")
    print(f"To utilize your credits, you should upload your '{input_dir}' content to a GCS bucket.")
    print("Then create a Data Store in Vertex AI Agent Builder pointing to that bucket.")
    print("\nRun this command to upload your docs:")
    print(f"  gsutil mb -l {location} gs://{project_id}-judge6-docs")
    print(f"  gsutil cp {input_dir}/* gs://{project_id}-judge6-docs/")
    print("\nThen creates the data store (can be done via UI or API).")

    # We can try to list data stores to see if it exists
    client = discoveryengine.DataStoreServiceClient()
    parent = f"projects/{project_id}/locations/{location}/collections/default_collection"

    try:
        # List data stores
        request = discoveryengine.ListDataStoresRequest(parent=parent)
        page_result = client.list_data_stores(request=request)
        existing_stores = [ds.name for ds in page_result]
        print(f"Found {len(existing_stores)} existing data stores.")
    except Exception as e:
        print(f"⚠️  Could not list data stores (API enabled?): {e}")


def query_judge6_grounded(project_id: str, location: str, data_store_id: str, query: str):
    """
    Queries Gemini with grounding against the Vertex AI Search data store.
    This is the key step that uses the "GenAI App Builder" credits.
    """
    print("\n--- 2. Querying Judge #6 (Grounded) ---")
    vertexai.init(project=project_id, location=location)

    # Define the grounding tool
    # Format: projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{data_store_id}
    data_store_path = f"projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{data_store_id}"

    grounding_tool = Tool.from_google_search_retrieval(
        grounding.GoogleSearchRetrieval()
    )  # Fallback to Google Search if datastore not ready, but we want Data Store:

    # Correct way for Vertex AI Search Grounding:
    grounding_tool = Tool.from_retrieval(
        grounding.Retrieval(
            source=grounding.VertexAISearch(datastore=data_store_path),
        )
    )

    model = GenerativeModel("gemini-1.5-flash-001")

    print(f"❓ Question: {query}")
    try:
        response = model.generate_content(query, tools=[grounding_tool], generation_config={"temperature": 0.0})
        print("\n⚖️  Judge #6 Verdict:")
        print(response.text)

        # Print citations if any
        if response.candidates[0].grounding_metadata.grounding_chunks:
            print("\n📜 Citations (from Sovereign Memory):")
            for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
                print(f" - {chunk.retrieved_context.title}")

    except Exception as e:
        print(f"❌ Error querying model: {e}")
        print("Ensure you have enabled the 'Vertex AI API' and 'Vertex AI Search API'.")


if __name__ == "__main__":
    check_env()

    # Example usage
    # 1. Import (Manual step usually required for first time setup)
    import_documents(PROJECT_ID, LOCATION, DATA_STORE_ID, DOCS_DIR)

    # 2. Query
    query = "What is the doctrine regarding Cloudflare integration?"
    query_judge6_grounded(PROJECT_ID, LOCATION, DATA_STORE_ID, query)
