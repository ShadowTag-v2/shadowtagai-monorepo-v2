# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os

# Import the Brain Logic
# Ensure app/jobs/nightly_ingest.py is in PYTHONPATH or copied to plugins
import sys
from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

sys.path.append(os.path.join(os.environ.get("AIRFLOW_HOME", "/opt/airflow"), "dags"))

# Define Arguments
default_args = {
    "owner": "admin",
    "depends_on_past": False,
    "email": ["redacted@shadowtag-v4.local"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Define DAG
with DAG(
    "nightly_synthesis",
    default_args=default_args,
    description="The Omega Monolith Nightly Synthesis Orchestrator",
    schedule="0 2 * * *",  # 2 AM Daily
    start_date=pendulum.datetime(2025, 11, 24, tz="UTC"),
    catchup=False,
    tags=["omega", "core"],
) as dag:
    # Task 1: The Brain (Ingestion)
    # We execute the python script directly. In a production Cloud Run environment,
    # this runs inside the worker container.
    def run_ingest():
        import asyncio

        from app.jobs.nightly_ingest import run_god_mode_batch

        asyncio.run(run_god_mode_batch())

    ingest_task = PythonOperator(
        task_id="nightly_ingest",
        python_callable=run_ingest,
    )

    # Task 2: The Designer (Synthesis)
    # Checks for the report and runs the design system builder.
    # Assumes the environment has Node/NPM installed or calls out to another service.
    # For Hybrid Cloud Run, we might prefer triggering another Cloud Run Job here,
    # but for now, we keep it monolithic as requested.
    synthesis_task = BashOperator(
        task_id="design_synthesis",
        bash_command="""
        if [ -f /opt/airflow/dags/ingestion_report.json ]; then
            echo "🎨 Report found. Engaging Design Systems..."
            # Placeholder for actual NPM command or external service call
            echo "Simulating: npm run analyze -- --input /opt/airflow/dags/ingestion_report.json --fix"
        else
            echo "⚠️ No report found. Skipping."
            exit 1
        fi
        """,
    )

    ingest_task >> synthesis_task
