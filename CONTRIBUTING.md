# Contributing

Thanks for contributing to `armavita-originality-ai-mcp`.

## Workflow

1. Fork the repo and create a feature branch.
2. Keep changes focused and include docs updates when behavior changes.
3. Run basic checks locally before opening a PR.

## Local Checks

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m py_compile run.py armavita_originality_ai_mcp/server.py armavita_originality_ai_mcp/client.py armavita_originality_ai_mcp/handlers/scan_handlers.py armavita_originality_ai_mcp/tools/scan_tools.py
```

## Pull Requests

- Use clear commit messages.
- Explain user-visible behavior changes in the PR description.
- Include examples for new tools or changed tool parameters.
