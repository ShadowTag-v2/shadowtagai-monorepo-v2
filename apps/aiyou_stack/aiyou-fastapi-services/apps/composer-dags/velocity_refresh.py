# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.utils.dates import days_ago

default_args = {
    "owner": "gucci-ops",
    "retries": 3,
}

with DAG(
    "velocity_lake_sentinel",
    default_args=default_args,
    schedule="@hourly",
    start_date=days_ago(1),
    tags=["velocity", "biglake"],
    catchup=False,
) as dag:
    refresh_metadata = BigQueryInsertJobOperator(
        task_id="refresh_external_table",
        configuration={
            "query": {
                "query": "CALL BQ.REFRESH_EXTERNAL_METADATA_CACHE('shadowtag-omega-v2.velocity_dataset.events_raw');",
                "useLegacySql": False,
            },
        },
    )
