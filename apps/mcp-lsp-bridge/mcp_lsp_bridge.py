import logging
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_lsp_bridge")

app = Server("mcp-lsp-bridge")

@app.call_tool()
async def translate_lsp(name: str, arguments: dict) -> list:
    logger.info(f"Translating LSP method: {name}")
    return [{"type": "text", "text": f"LSP Method {name} translated."}]

async def main():
    logger.info("Starting MCP LSP Bridge")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
