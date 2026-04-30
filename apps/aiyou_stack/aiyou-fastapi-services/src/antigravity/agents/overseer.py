from google.adk.core import LlmAgent

# 1. Define the Specialists
coder_agent = LlmAgent(
    name="CodeSpecialist",
    description="Writes and refactors Python/Terraform code.",
    tools=["mcp-server-filesystem", "ast-grep"],
)

ops_agent = LlmAgent(
    name="OpsSpecialist",
    description="Handles deployments, Kubernetes, and Cloud Run logs.",
    tools=["kubectl", "gcloud"],
)

data_agent = LlmAgent(
    name="DataSpecialist",
    description="Queries BigQuery, BigLake logs, and RAG knowledge base.",
    tools=["bigquery-client", "rag-router"],
)

# 2. The Overseer (Dispatcher)
# "God Mode" starts here. The router decides who gets the job.
overseer = LlmAgent(
    name="Overseer",
    instruction="""
    You are the Flying minion Orchestrator.
    Analyze the user intent:
    - If they want to write/fix code, route to CodeSpecialist.
    - If they want to deploy/restart servers, route to OpsSpecialist.
    - If they want to search logs or docs, route to DataSpecialist.
    """,
    sub_agents=[coder_agent, ops_agent, data_agent],
)
