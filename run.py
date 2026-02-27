#!/usr/bin/env python3
"""Entry point for the Originality.ai MCP Server."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from armavita_originality_ai_mcp.server import main

if __name__ == "__main__":
    main()
