"""
Tool definitions for Originality.ai MCP Server.

All MCP tool schemas organized by function.
"""

from armavita_originality_ai_mcp.tools.scan_tools import SCAN_TOOLS

ALL_TOOLS = SCAN_TOOLS

__all__ = ["ALL_TOOLS", "SCAN_TOOLS"]
