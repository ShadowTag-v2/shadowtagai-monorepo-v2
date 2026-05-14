import os
import asyncio
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

# We DO NOT use .env files. Secrets are managed via GCP Secret Manager and injected.
# DEVELOPER_KNOWLEDGE_API_KEY is provided securely via the environment.

async def run_agent():
    print("Initializing Google Developer Knowledge MCP Client...")

    api_key = os.getenv("DEVELOPER_KNOWLEDGE_API_KEY")
    
    if not api_key:
        raise ValueError(
            "ERROR: API Key missing. "
            "Please ensure DEVELOPER_KNOWLEDGE_API_KEY is injected by the platform."
        )

    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp_google_developer_knowledge"],
        env={
            **os.environ,
            "DEVELOPER_KNOWLEDGE_API_KEY": api_key
        }
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            
            await session.initialize()
            print("✅ Successfully connected to the Developer Knowledge MCP Server.")
            
            tools_response = await session.list_tools()
            print("\n--- Available Knowledge Tools ---")
            for tool in tools_response.tools:
                print(f"[{tool.name}]: {tool.description}")

if __name__ == "__main__":
    try:
        asyncio.run(run_agent())
    except KeyboardInterrupt:
        print("\nAgent connection terminated by user.")
