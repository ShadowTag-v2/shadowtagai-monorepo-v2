import logging
from typing import Any

from google.cloud import bigquery

logger = logging.getLogger(__name__)


class BigQueryTool:
    def __init__(self, project_id: str):
        self.client = bigquery.Client(project=project_id)

    async def query(self, sql: str) -> list[dict[str, Any]]:
        """Executes a Standard SQL query and returns results as a list of dicts."""
        try:
            query_job = self.client.query(sql)
            results = query_job.result()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"BigQuery Query Error: {e}")
            return [{"error": str(e)}]

    async def get_schema(self, dataset_id: str, table_id: str) -> list[dict[str, str]]:
        """Retrieves schema for a specific table."""
        try:
            table_ref = self.client.dataset(dataset_id).table(table_id)
            table = self.client.get_table(table_ref)
            return [
                {"name": field.name, "type": field.field_type, "mode": field.mode}
                for field in table.schema
            ]
        except Exception as e:
            logger.error(f"BigQuery Schema Error: {e}")
            return [{"error": str(e)}]


class DataEngineeringAgent:
    """The 'Brain' of the operation. Analyzes Swarm Telemetry in BigQuery."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.bq_tool = BigQueryTool(project_id)
        self.name = "DataEngineer"

    async def run_analysis(self, sql_query: str) -> dict[str, Any]:
        """Runs a specific analysis query on the swarm memory."""
        logger.info(f"Running analysis: {sql_query}")
        results = await self.bq_tool.query(sql_query)
        return {
            "query": sql_query,
            "row_count": len(results),
            "sample_data": results[:5],  # Limit sample size
        }

    async def check_nervous_system_health(self) -> dict[str, Any]:
        """Checks the health of the Pub/Sub --> BigQuery pipeline."""
        sql = f"""
            SELECT count(*) as event_count, max(publish_time) as last_event
            FROM `{self.project_id}.antigravity_bi.swarm_raw`
        """
        return await self.run_analysis(sql)
