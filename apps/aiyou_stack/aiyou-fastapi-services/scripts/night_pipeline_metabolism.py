import datetime
import os

import pandas as pd
from google.cloud import firestore, storage

# CONFIG
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v2")
BUCKET_NAME = "shadowtag-iceberg-lake"
db = firestore.Client(project=PROJECT_ID)
storage_client = storage.Client(project=PROJECT_ID)


def run_metabolism():
    print(f">>> 🌙 NIGHT PIPELINE: Starting metabolism for {datetime.date.today()}")

    # 1. SWEEP Velocity Lake (Firestore)
    # Target: Stale logs or transient Agent 'thoughts'
    # We grab 'internal_monitoring' as per request
    docs = db.collection("internal_monitoring").stream()
    data_points = []
    doc_ids_to_delete = []

    for doc in docs:
        d = doc.to_dict()
        d["doc_id"] = doc.id
        # Handle timestamp serialization for pandas/parquet
        # firestore timestamps might need conversion to string or datetime
        for k, v in d.items():
            if hasattr(v, "isoformat"):
                d[k] = v.isoformat()

        data_points.append(d)
        doc_ids_to_delete.append(doc.id)

    if not data_points:
        print("✅ No stale data to migrate.")
        return

    # 2. FLATTEN & COMPRESS (Iceberg Prep)
    df = pd.DataFrame(data_points)

    # Create temp dir if needed
    os.makedirs("/tmp", exist_ok=True)
    parquet_path = "/tmp/upload.parquet"
    df.to_parquet(parquet_path, index=False)

    file_name = f"metabolism/date={datetime.date.today()}/agent_logs.parquet"

    # 3. PUNCH into Iceberg Lake (GCS)
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        # Check if bucket exists, create if not (demo safety)
        if not bucket.exists():
            print(f"Creating bucket {BUCKET_NAME}...")
            bucket.create(location="US-CENTRAL1")

        blob = bucket.blob(file_name)
        blob.upload_from_filename(parquet_path)
        print(f"✅ Archived {len(data_points)} points to Iceberg: {file_name}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return

    # 4. PURGE Velocity Lake (Cost Saver)
    # In prod, verify upload checksum before delete.
    for doc_id in doc_ids_to_delete:
        db.collection("internal_monitoring").document(doc_id).delete()
    print("✅ Velocity Lake purged. Costs optimized.")


if __name__ == "__main__":
    run_metabolism()
