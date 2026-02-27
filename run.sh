#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQ_FILE="$SCRIPT_DIR/requirements.txt"
VENV_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/repo-mcp/venvs/armavita-originality-ai-mcp"
PY_BIN="$VENV_DIR/bin/python"
MARKER="$VENV_DIR/.requirements-installed"

# Enforce Python baseline explicitly so failures are deterministic.
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required (>=3.11)" >&2
  exit 1
fi

if ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)'; then
  echo "Python 3.11+ is required for armavita-originality-ai-mcp" >&2
  exit 1
fi

if [ ! -x "$PY_BIN" ] || [ "$REQ_FILE" -nt "$MARKER" ]; then
  mkdir -p "$(dirname "$VENV_DIR")"
  python3 -m venv "$VENV_DIR"
  "$PY_BIN" -m pip install --upgrade pip >/dev/null
  "$PY_BIN" -m pip install --no-input --disable-pip-version-check -r "$REQ_FILE" >/dev/null
  touch "$MARKER"
fi

exec "$PY_BIN" "$SCRIPT_DIR/run.py" "$@"
