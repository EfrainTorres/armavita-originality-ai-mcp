# Changelog

All notable changes to this project are documented in this file.

## [2.0.0] - 2026-02-27

- Removed all legacy `originality` compatibility aliases and shim paths.
- Removed `originality-mcp` CLI alias; canonical CLI is now `armavita-originality-ai-mcp` only.
- Removed legacy `originality` server key from local MCP config examples.
- Hard-break rename complete: canonical naming only.

## [1.1.1] - 2026-02-27

- Standardized project license metadata and docs to AGPL-3.0-only.
- Replaced MIT license file with GNU Affero General Public License v3.0 text.
- Added explicit Python `3.11+` enforcement in `run.sh`.
- Improved README install guidance to match CLI entrypoint behavior.
- Added required environment variable and development sections to README.
- Removed generated build/cache artifacts from the repository tree.

## [1.1.0] - 2026-02-27

- Renamed project to `armavita-originality-ai-mcp`.
- Renamed Python package namespace to `armavita_originality_ai_mcp`.
- Updated MCP server metadata to `armavita-originality-ai-mcp`.
- Added canonical CLI entrypoint `armavita-originality-ai-mcp`.
- Kept `originality-mcp` CLI as a compatibility alias.
- Added compatibility shim folder at `../originality/` for legacy run-paths.
- Removed committed Python cache artifacts.

## [1.0.0] - 2026-02-23

- Initial standalone OSS release.
- Added Originality.ai MCP tools:
  - AI scan
  - full audit scan
  - readability scan
  - SEO scan
  - URL scan
  - scan result retrieval
  - credit balance check
