"""
Scan tool definitions for Originality.ai MCP Server.

Contains: scan_ai, scan_full, scan_readability, scan_seo, scan_url, get_results, credit_balance
"""

from typing import List

from mcp.types import Tool

SCAN_TOOLS: List[Tool] = [
    Tool(
        name="scan_ai",
        description=(
            "Detect AI-generated content using Originality.ai. Returns an overall "
            "AI vs. Original percentage and a sentence-by-sentence breakdown with "
            "confidence scores. Use this after writing content to check AI detection "
            "scores before publishing. Costs ~1 credit per 100 words."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Plain text content to scan. Strip HTML/markdown for best accuracy. Minimum ~50 words for reliable results.",
                },
                "title": {
                    "type": "string",
                    "default": "AI Detection Scan",
                    "description": "Label for the scan (for reference in stored results).",
                },
            },
            "required": ["content"],
        },
    ),
    Tool(
        name="scan_full",
        description=(
            "Run a comprehensive content audit: AI detection + plagiarism + readability "
            "+ grammar/spelling + fact-checking. Returns all scores in one call. "
            "Plagiarism checks can take up to 60 seconds. Use for pre-publish content audits. "
            "Costs credits for each enabled check."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Plain text content to scan.",
                },
                "title": {
                    "type": "string",
                    "default": "Full Content Audit",
                    "description": "Label for the scan.",
                },
                "check_facts": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable fact-checking (verifies claims against sources). Adds processing time.",
                },
                "excluded_urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "URLs to exclude from plagiarism matching (e.g., your own site).",
                },
            },
            "required": ["content"],
        },
    ),
    Tool(
        name="scan_plagiarism",
        description=(
            "Check content for plagiarism only — no AI detection, readability, or grammar. "
            "Returns an overall plagiarism percentage and matched sources with URLs. "
            "Plagiarism checks can take up to 60 seconds. Use to verify content originality "
            "before publishing. Cheaper than scan_full since only plagiarism credits are used."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Plain text content to check for plagiarism. Strip HTML/markdown for best accuracy.",
                },
                "title": {
                    "type": "string",
                    "default": "Plagiarism Scan",
                    "description": "Label for the scan (for reference in stored results).",
                },
                "excluded_urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "URLs to exclude from plagiarism matching (e.g., your own site).",
                },
            },
            "required": ["content"],
        },
    ),
    Tool(
        name="scan_readability",
        description=(
            "Analyze content readability and grammar only — no AI detection or plagiarism. "
            "Returns Flesch Reading Ease, grade level, sentence difficulty breakdown, "
            "and grammar/spelling errors with corrections. Fast and cheap. "
            "Use to check if content meets the 8th-9th grade reading level target."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Plain text content to analyze.",
                },
                "title": {
                    "type": "string",
                    "default": "Readability Scan",
                    "description": "Label for the scan.",
                },
            },
            "required": ["content"],
        },
    ),
    Tool(
        name="scan_seo",
        description=(
            "Run SEO content optimization analysis for a target keyword. Returns "
            "keyword seed recommendations with min/max/current density targets. "
            "Combine with AI detection and readability for a full content quality check. "
            "Currently supports United States only."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Plain text content to analyze.",
                },
                "keyword": {
                    "type": "string",
                    "description": "Target keyword or phrase for SEO optimization.",
                },
                "title": {
                    "type": "string",
                    "default": "SEO Scan",
                    "description": "Label for the scan.",
                },
                "device": {
                    "type": "string",
                    "enum": ["desktop", "mobile"],
                    "default": "desktop",
                    "description": "Device type for ranking prediction.",
                },
                "publishing_domain": {
                    "type": "string",
                    "description": "Your website URL for context (e.g., 'example.com'). Optional but improves accuracy.",
                },
                "check_ai": {
                    "type": "boolean",
                    "default": True,
                    "description": "Also run AI detection alongside SEO analysis.",
                },
                "check_readability": {
                    "type": "boolean",
                    "default": True,
                    "description": "Also run readability analysis alongside SEO.",
                },
            },
            "required": ["content", "keyword"],
        },
    ),
    Tool(
        name="scan_url",
        description=(
            "Scan a published URL for AI content, plagiarism, readability, and grammar. "
            "Originality.ai fetches and extracts the page content automatically. "
            "Use to audit competitor content or verify published articles."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Full URL of the page to scan (e.g., 'https://example.com/blog/article').",
                },
                "title": {
                    "type": "string",
                    "default": "URL Scan",
                    "description": "Label for the scan.",
                },
                "check_ai": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable AI detection.",
                },
                "check_plagiarism": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable plagiarism checking.",
                },
                "check_readability": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable readability scoring.",
                },
                "check_grammar": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable grammar/spelling check.",
                },
                "check_facts": {
                    "type": "boolean",
                    "default": False,
                    "description": "Enable fact-checking.",
                },
                "excluded_urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "URLs to exclude from plagiarism matching.",
                },
            },
            "required": ["url"],
        },
    ),
    Tool(
        name="get_scan_results",
        description=(
            "Retrieve previously stored scan results by scan ID. Use this to fetch "
            "full results for scans that were stored (storeScan=true), or to check "
            "on scans that may have been processing when originally submitted."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "scan_id": {
                    "type": "string",
                    "description": "The scan ID (returned as 'id' in the original scan response).",
                },
            },
            "required": ["scan_id"],
        },
    ),
    Tool(
        name="credit_balance",
        description=(
            "Check your Originality.ai credit balance. Returns remaining credits "
            "available for scanning. Use before batch operations to verify you have "
            "enough credits."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
]
