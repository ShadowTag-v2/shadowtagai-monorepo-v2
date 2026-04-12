"""
Verification Script for Google Official MCP Integration.
Tests BigQuery and GKE tools using GeminiFunctionCaller.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.google_mcp_tools import get_google_mcp_tools

# Ensure we have credentials
if not os.environ.get("GOOGLE_API_KEY"):
    print("WARNING: GOOGLE_API_KEY not set. Gemini calls might fail.")
    # For verification, we might check if we can just instantiate the tools
    # and call the python functions directly if LLM is not available.


def test_tool_direct_execution():
    """Test the Python functions directly (skipping LLM layer to verify logic)."""
    print("Testing Google MCP Tools (Direct Execution)...")

    tools = get_google_mcp_tools()
    bq_schema_tool = next(t for t in tools if t.name == "bigquery_schema")
    bq_query_tool = next(t for t in tools if t.name == "bigquery_query")
    gke_tool = next(t for t in tools if t.name == "gke_list_clusters")

    # 1. Test BigQuery Schema
    print("\n1. Testing BigQuery Schema (dataset: revenue_optimization)...")
    schema = bq_schema_tool.function(dataset_id="revenue_optimization")
    print(f"Schema Result: {schema[:200]}...")

    # 2. Test BigQuery Query (Create a table if not exists, then select)
    print("\n2. Testing BigQuery Query...")
    # Create table first (standard SQL)
    create_sql = """
    CREATE TABLE IF NOT EXISTS `acquired-jet-478701-b3.revenue_optimization.test_table` (
        id INT64,
        scenario STRING
    )
    """
    bq_query_tool.function(sql_query=create_sql)

    # Select
    select_sql = "SELECT * FROM `acquired-jet-478701-b3.revenue_optimization.test_table` LIMIT 5"
    result = bq_query_tool.function(sql_query=select_sql)
    print(f"Query Result: {result}")

    # 3. Test GKE List
    print("\n3. Testing GKE Cluster List...")
    clusters = gke_tool.function()
    print(f"Clusters: {clusters}")

    print("\n✅ Verification Complete.")


if __name__ == "__main__":
    test_tool_direct_execution()
