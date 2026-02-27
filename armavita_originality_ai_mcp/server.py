"""
Originality.ai MCP Server — stdio transport.

Exposes AI detection, plagiarism, readability, grammar, fact-checking,
and SEO optimization tools via the Model Context Protocol.
"""

import asyncio
import os
from typing import Any

import mcp.server.stdio
from loguru import logger
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import ServerCapabilities, TextContent, ToolsCapability

from armavita_originality_ai_mcp.client import OriginalityClient
from armavita_originality_ai_mcp.handlers import (
    handle_credit_balance,
    handle_get_scan_results,
    handle_scan_ai,
    handle_scan_full,
    handle_scan_plagiarism,
    handle_scan_readability,
    handle_scan_seo,
    handle_scan_url,
)
from armavita_originality_ai_mcp.tools import ALL_TOOLS

# Initialize the MCP server
server = Server("armavita-originality-ai-mcp")

# API client (initialized lazily on first call)
_client: OriginalityClient | None = None


def _get_client() -> OriginalityClient:
    """Get or create the API client."""
    global _client
    if _client is None:
        api_key = os.getenv("ORIGINALITY_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "ORIGINALITY_API_KEY environment variable not set. "
                "Get your API key from https://app.originality.ai/home/api-token-dashboard"
            )
        _client = OriginalityClient(api_key)
    return _client


# Map tool names to handler functions
TOOL_HANDLERS = {
    "scan_ai": handle_scan_ai,
    "scan_full": handle_scan_full,
    "scan_plagiarism": handle_scan_plagiarism,
    "scan_readability": handle_scan_readability,
    "scan_seo": handle_scan_seo,
    "scan_url": handle_scan_url,
    "get_scan_results": handle_get_scan_results,
    "credit_balance": handle_credit_balance,
}


@server.list_tools()
async def list_tools() -> list:
    """List all available Originality.ai tools."""
    return ALL_TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a tool by routing to the appropriate handler."""
    try:
        client = _get_client()

        handler = TOOL_HANDLERS.get(name)
        if not handler:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}. Available: {', '.join(TOOL_HANDLERS.keys())}",
            )]

        return await handler(arguments, client)

    except RuntimeError as e:
        # Missing API key
        return [TextContent(type="text", text=str(e))]
    except Exception as e:
        logger.exception("Error executing tool {}", name)
        error_msg = f"Error executing {name}: {e}"
        if not os.getenv("ORIGINALITY_API_KEY"):
            error_msg += "\nORIGINALITY_API_KEY environment variable not set!"
        return [TextContent(type="text", text=error_msg)]


async def run() -> None:
    """Run the MCP server over stdio."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="armavita-originality-ai-mcp",
                server_version="2.0.0",
                capabilities=ServerCapabilities(tools=ToolsCapability()),
            ),
        )


def main() -> None:
    """Main entry point."""
    asyncio.run(run())


if __name__ == "__main__":
    main()
