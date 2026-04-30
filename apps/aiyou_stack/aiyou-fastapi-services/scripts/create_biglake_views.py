import os

from google.cloud import bigquery

# CONFIG
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v2")
DATASET_ID = "iceberg_analytics"
TABLE_ID = "agent_historical_logs"
BUCKET_NAME = "shadowtag-iceberg-lake"
GCS_SOURCE = f"gs://{BUCKET_NAME}/metabolism/*.parquet"

client = bigquery.Client(project=PROJECT_ID)


def create_sovereign_view():
    print(f">>> ❄️  CREATING BIGLAKE LENS: {DATASET_ID}.{TABLE_ID}")

    # 1. Create Dataset if missing
    dataset_ref = bigquery.DatasetReference(PROJECT_ID, DATASET_ID)
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = "us-central1"
    try:
        client.create_dataset(dataset, exists_ok=True)
        print(f"    - Dataset '{DATASET_ID}' ready.")
    except Exception as e:
        print(f"    - Dataset creation note: {e}")

    # 2. Configure External Table pointing to GCS
    external_config = bigquery.ExternalConfig("PARQUET")
    external_config.source_uris = [GCS_SOURCE]
    external_config.autodetect = True

    # Enable Hive Partitioning (matches the Night Pipeline structure)
    # Hive partitioning assumes paths regarding /key=value/
    hive_partitioning = bigquery.HivePartitioningOptions()
    hive_partitioning.mode = "STRINGS"
    # The source uri prefix must match the root of the hive partition structure
    hive_partitioning.source_uri_prefix = f"gs://{BUCKET_NAME}/metabolism/"
    external_config.hive_partitioning = hive_partitioning

    table_ref = dataset_ref.table(TABLE_ID)
    table = bigquery.Table(table_ref)
    table.external_data_configuration = external_config

    # 3. Punch Table into BigQuery
    try:
        client.create_table(table, exists_ok=True)
        print("✅ BigLake View Created. You can now run standard SQL.")
    except Exception as e:
        print(f"❌ Table creation failed: {e}")


if __name__ == "__main__":
    create_sovereign_view()
