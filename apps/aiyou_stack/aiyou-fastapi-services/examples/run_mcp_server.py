"""Run MCP Server for ShadowTag + ShadowTag-v4

Starts FastAPI server with all MCP tool endpoints

Usage:
    python examples/run_mcp_server.py

Environment variables:
    GEMINI_API_KEY - Google AI API key (required)
    PORT - Server port (default: 8000)
"""

import os
import sys

import uvicorn

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mcp_server import create_mcp_server


def main():
    # Get configuration
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not gemini_api_key:
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export GEMINI_API_KEY='your-api-key-here'")
        raise SystemExit(1)

    port = int(os.getenv("PORT", 8000))

    # Create MCP server
    print("\n" + "=" * 80)
    print("🚀 Starting ShadowTag-v4 MCP Server")
    print("=" * 80)
    print(f"\n📡 Server: http://0.0.0.0:{port}")
    print(f"📚 Docs: http://0.0.0.0:{port}/docs")
    print(f"🔧 Health: http://0.0.0.0:{port}/mcp/health")
    print("\n🤖 Available MCP Tools:")
    print("   • POST /mcp/tools/shadowtag/upload - ShadowTag authentication workflow")
    print("   • POST /mcp/tools/shadowtag/verify - Verify watermark & fingerprint")
    print("   • POST /mcp/tools/shadowtag_v4/ingest - ShadowTag-v4 content ranking workflow")
    print("   • GET  /mcp/tools/shadowtag_v4/feed - Get AI-cognition ranked feed")
    print("   • GET  /mcp/workflows/{id} - Get workflow status")
    print("\n" + "=" * 80 + "\n")

    # Create app
    app = create_mcp_server(gemini_api_key=gemini_api_key)

    # Run server
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
