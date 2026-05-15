-- 1. Create the External Table (Iceberg Format)
-- This tells BigQuery: "Look at this GCS bucket, treat it as an Iceberg table"
CREATE OR REPLACE EXTERNAL TABLE `agent_lakehouse.extracted_invoices`
WITH CONNECTION `iceberg-conn`
OPTIONS (
  format = 'ICEBERG',
  uris = ['gs://your-project-agent-lake/raw_data/invoices_iceberg_metadata/*']
);

-- 2. Query the Agent's Work (Zero ETL)
-- You can query the data seconds after the agent finishes
SELECT
  task_id,
  invoice_total,
  vendor_name,
  processing_date
FROM `agent_lakehouse.extracted_invoices`
WHERE processing_date > '2025-01-01'
ORDER BY invoice_total DESC;
