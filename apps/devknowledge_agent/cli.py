import argparse
import asyncio
import os
import sys
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

async def run_query(query: str):
    api_key = os.getenv("DEVELOPER_KNOWLEDGE_API_KEY")
    if not api_key:
        print("ERROR: DEVELOPER_KNOWLEDGE_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp_google_developer_knowledge"],
        env={**os.environ, "DEVELOPER_KNOWLEDGE_API_KEY": api_key}
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            try:
                # Querying developer knowledge via search_knowledge tool (or similar depending on actual schema)
                # The tutorial mentions "search_knowledge"
                response = await session.call_tool("search_knowledge", arguments={"query": query})
                print("\n--- Developer Knowledge Response ---")
                print(response)
            except Exception as e:
                print(f"Tool execution failed: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="CLI wrapper for Google Developer Knowledge MCP Server")
    parser.add_argument("query", help="The question or search query for the developer knowledge base")
    args = parser.parse_args()

    try:
        asyncio.run(run_query(args.query))
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")

if __name__ == "__main__":
    main()
