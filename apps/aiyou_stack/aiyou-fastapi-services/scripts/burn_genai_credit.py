#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Vertex AI Search Ingestion Script (Burn Strategy A)
Target: $1,000 GenAI App Builder Credit
"""

import glob
import os
import time

from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1beta as discoveryengine

# Configuration
PROJECT_ID = "acquired-jet-478701-b3"
LOCATION = "global"  # GenAI App Builder is global
DATA_STORE_ID = "antigravity-knowledge-base"  # We will create/use this
flattened_dir = os.path.expanduser("~/antigravity-flattened")


def import_documents(
    project_id: str,
    location: str,
    data_store_id: str,
    gcs_uri: str = None,
    local_files: list[str] = None,
):
    """Imports documents into Vertex AI Search."""
    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )

    client = discoveryengine.DocumentServiceClient(client_options=client_options)
    # Fix: Use correct path helper
    parent = client.branch_path(project_id, location, data_store_id, "default_branch")

    print(f"///▞ IMPORT :: Targeting Branch: {parent}")

    # Check if Data Store exists (by listing or trying to create)
    # For elegance, we'll try to create it if we can't find it, but DocumentService doesn't create DataStores.
    # We need DataStoreServiceClient for that.

    ds_client = discoveryengine.DataStoreServiceClient(client_options=client_options)
    ds_parent = f"projects/{project_id}/locations/{location}"
    ds_name = f"{ds_parent}/dataStores/{data_store_id}"

    try:
        ds_client.get_data_store(name=ds_name)
        print(f"///▞ CHECK :: Data Store {data_store_id} exists.")
    except Exception:
        print(f"///▞ CREATE :: Data Store {data_store_id} not found. Creating...")
        try:
            operation = ds_client.create_data_store(
                parent=ds_parent,
                data_store_id=data_store_id,
                data_store=discoveryengine.DataStore(
                    display_name="Antigravity Knowledge Base",
                    industry_vertical=discoveryengine.IndustryVertical.GENERIC,
                    content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
                    solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
                ),
            )
            print("///▞ WAIT :: Waiting for Data Store creation...")
            operation.result()
            print("///▞ SUCCESS :: Data Store created.")
        except Exception as e:
            print(f"///▞ ERROR :: Failed to create Data Store: {e}")
            return

    # For local files, we need to convert them to JSONL format expected by Discovery Engine
    # OR upload them to GCS first. Uploading to GCS is cleaner for batch processing.
    # However, for "Burn A", we can try inline creation if the content is small, but for 3000 repos, GCS is better.

    # Strategy:
    # 1. We assume files are already flattened.
    # 2. We will simulate the "Burn" by iterating and creating documents one by one (inefficient but burns credits via API calls)
    #    OR batch import for speed.
    #    User asked for "As quickly as possible". Batch import via GCS is fastest.
    #    But we might not have GCS bucket ready.

    # Let's do direct Document creation loop to verify connectivity and start the burn.

    if local_files:
        print(f"///▞ BURN :: Starting ingestion of {len(local_files)} files...")
        for i, file_path in enumerate(local_files):
            try:
                with open(file_path, errors="ignore") as f:
                    content = f.read()

                file_name = os.path.basename(file_path)

                if not content.strip():
                    print(f"Skipping empty file: {file_name}")
                    continue

                # Revert to using Document.content (standard for Unstructured)
                # Ensure parent_id is NOT passed.
                document = discoveryengine.Document(
                    content=discoveryengine.Document.Content(
                        raw_bytes=content.encode("utf-8"),
                        mime_type="text/plain",
                    ),
                    id=f"doc-{i}-{int(time.time())}",
                )

                request = discoveryengine.CreateDocumentRequest(
                    parent=parent,
                    document=document,
                    document_id=document.id,
                )

                response = client.create_document(request=request)
                print(f"[{i}/{len(local_files)}] Ingested: {file_name} -> {response.name}")

            except Exception as e:
                print(f"Error ingesting {file_path}: {e}")
                # Rate limit handling?
                time.sleep(0.5)


if __name__ == "__main__":
    # 1. Get list of files
    files = glob.glob(os.path.join(flattened_dir, "*"))  # Ingest EVERYTHING (not just .py)
    # files = files[:1000] # REMOVED LIMIT - FULL INGESTION

    print(f"///▞ SCALE :: Found {len(files)} files to ingest.")

    if not files:
        print("No files found in ~/antigravity-flattened. Is the fork script finished?")
    else:
        import_documents(PROJECT_ID, LOCATION, DATA_STORE_ID, local_files=files)
