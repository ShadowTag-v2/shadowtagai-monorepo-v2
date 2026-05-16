# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
from google.cloud import firestore


def get_queued_tasks_count():
  """
  Leverages the new Firestore aggregation pipeline to instantly count
  total queued tasks without a BigQuery ETL Python tax.
  """
  project_id = os.getenv("GCP_PROJECT_ID", "shadowtag-omega-v4")
  db = firestore.Client(project=project_id)

  collection_ref = db.collection("agent_queue")
  query = collection_ref.where(filter=firestore.FieldFilter("status", "==", "queued"))

  # Utilizing Native Firestore Count Aggregation
  aggregate_query = db.aggregation.AggregationQuery(query)
  aggregate_query.count(alias="all_queued")

  results = aggregate_query.get()

  for result in results:
    amount = result[0].value
    print(f"🔥 Native Firestore Aggregation complete. Total queued tasks: {amount}")
    return amount


if __name__ == "__main__":
  get_queued_tasks_count()
