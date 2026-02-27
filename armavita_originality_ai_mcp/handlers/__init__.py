"""
Handler implementations for Originality.ai MCP Server.

Handlers contain the business logic for each tool — they call the API client,
process responses, and format output as TextContent for the LLM.
"""

from armavita_originality_ai_mcp.handlers.scan_handlers import (
    handle_credit_balance,
    handle_get_scan_results,
    handle_scan_ai,
    handle_scan_full,
    handle_scan_plagiarism,
    handle_scan_readability,
    handle_scan_seo,
    handle_scan_url,
)

__all__ = [
    "handle_scan_ai",
    "handle_scan_full",
    "handle_scan_plagiarism",
    "handle_scan_readability",
    "handle_scan_seo",
    "handle_scan_url",
    "handle_get_scan_results",
    "handle_credit_balance",
]
