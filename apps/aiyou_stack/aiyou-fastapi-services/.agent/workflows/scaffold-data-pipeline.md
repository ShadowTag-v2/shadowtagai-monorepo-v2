# Workflow: Scaffold Dataflow + Kafka Pipeline

1. **Ask User:** "Batch or Streaming?" and "Source/Sink?".
2. **Generate Infrastructure (Terraform):**
   - Enable APIs: `dataflow`, `managed-kafka`, `bigquery`.
   - Create Buckets: `gs://<project>-dataflow-temp`.
   - Create BigQuery Dataset: `analytics_lake`.
3. **Generate Python Pipeline (Apache Beam):**
   - Input: Kafka Topic (Managed Service).
   - Transform: `beam.Map()` for cleaning.
   - Output: BigQuery Write (Append Mode).
4. **Create Verification Script:**
   - A script to publish mock messages to Kafka.
   - A script to query BigQuery for result count.
