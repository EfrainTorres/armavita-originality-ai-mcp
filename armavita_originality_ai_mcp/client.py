"""
Async HTTP client for the Originality.ai API v3.

Wraps all endpoints with typed helpers and consistent error handling.
"""

import httpx
from loguru import logger
from typing import Any


class OriginalityClient:
    """Thin async wrapper around the Originality.ai API."""

    BASE_URL_V3 = "https://api.originality.ai/api/v3"
    BASE_URL_V1 = "https://api.originality.ai/api/v1"

    def __init__(self, api_key: str) -> None:
        headers = {"X-OAI-API-KEY": api_key}
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL_V3,
            headers=headers,
            timeout=90.0,  # plagiarism checks can take up to 60s
        )
        # Credit balance lives on v1
        self.client_v1 = httpx.AsyncClient(
            base_url=self.BASE_URL_V1,
            headers=headers,
            timeout=15.0,
        )

    # ── Scan endpoints ────────────────────────────────────────────

    async def scan(
        self,
        content: str,
        title: str = "MCP Scan",
        *,
        check_ai: bool = False,
        check_plagiarism: bool = False,
        check_facts: bool = False,
        check_readability: bool = False,
        check_grammar: bool = False,
        check_content_optimizer: bool = False,
        ai_model_version: str = "lite-102",
        optimizer_query: str = "",
        optimizer_country: str = "United States",
        optimizer_device: str = "desktop",
        optimizer_publishing_domain: str = "",
        store_scan: bool = True,
        excluded_urls: list[str] | None = None,
    ) -> dict[str, Any]:
        """Run a content scan with the specified checks enabled."""
        body: dict[str, Any] = {
            "title": title,
            "content": content,
            "check_ai": check_ai,
            "check_plagiarism": check_plagiarism,
            "check_facts": check_facts,
            "check_readability": check_readability,
            "check_grammar": check_grammar,
            "check_contentOptimizer": check_content_optimizer,
            "aiModelVersion": ai_model_version,
            "storeScan": store_scan,
        }
        if check_content_optimizer and optimizer_query:
            body["optimizerQuery"] = optimizer_query
            body["optimizerCountry"] = optimizer_country
            body["optimizerDevice"] = optimizer_device
            if optimizer_publishing_domain:
                body["optimizerPublishingDomain"] = optimizer_publishing_domain
        if excluded_urls:
            body["excludedUrls"] = excluded_urls

        return await self._post("/scan", body)

    async def scan_url(
        self,
        url: str,
        title: str = "MCP URL Scan",
        *,
        check_ai: bool = True,
        check_plagiarism: bool = True,
        check_readability: bool = True,
        check_grammar: bool = True,
        check_facts: bool = False,
        ai_model_version: str = "lite-102",
        store_scan: bool = True,
        excluded_urls: list[str] | None = None,
    ) -> dict[str, Any]:
        """Scan content from a URL."""
        body: dict[str, Any] = {
            "url": url,
            "title": title,
            "check_ai": check_ai,
            "check_plagiarism": check_plagiarism,
            "check_facts": check_facts,
            "check_readability": check_readability,
            "check_grammar": check_grammar,
            "check_contentOptimizer": False,
            "aiModelVersion": ai_model_version,
            "storeScan": store_scan,
        }
        if excluded_urls:
            body["excludedUrls"] = excluded_urls

        return await self._post("/scan-url", body)

    # ── Retrieval endpoints ───────────────────────────────────────

    async def get_scan_results(self, scan_id: str) -> dict[str, Any]:
        """Retrieve stored scan results by ID."""
        resp = await self.client.get("/scan-results", params={"id": scan_id})
        resp.raise_for_status()
        return resp.json()

    async def get_credit_balance(self) -> dict[str, Any]:
        """Get remaining account credits (v1 endpoint)."""
        resp = await self.client_v1.get("/account/credits/balance")
        resp.raise_for_status()
        return resp.json()

    # ── Internal helpers ──────────────────────────────────────────

    async def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        """POST with logging and error handling."""
        logger.debug("POST {} body keys: {}", path, list(body.keys()))
        resp = await self.client.post(path, json=body)
        resp.raise_for_status()
        return resp.json()

    async def close(self) -> None:
        await self.client.aclose()
        await self.client_v1.aclose()
