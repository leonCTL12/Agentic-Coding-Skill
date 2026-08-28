#!/usr/bin/env bash
# Cursor MCP entrypoint: C#-capable codetree (ThinkyMiner/codeTree + csharp overlay).
# Cursor starts one stdio process per window with cwd = that window's folder.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ROOT="${1:-$PWD}"
# User-level mcp.json may pass a literal ${workspaceFolder}, or expand it to
# ~/.cursor (the folder that contains the global mcp.json) — neither is a repo.
if [[ "$ROOT" == *'workspaceFolder'* || "$ROOT" == "${HOME}/.cursor" || "$ROOT" == "${HOME}" ]]; then
  ROOT="$PWD"
fi
ROOT="$(cd "$ROOT" && pwd)"

UV="${UV:-}"
if [[ -z "$UV" ]]; then
  if command -v uv >/dev/null 2>&1; then
    UV="$(command -v uv)"
  elif [[ -x "${HOME}/.local/bin/uv" ]]; then
    UV="${HOME}/.local/bin/uv"
  else
    echo "uv not found; install from https://docs.astral.sh/uv/" >&2
    exit 1
  fi
fi

exec "$UV" run --directory "$SCRIPT_DIR" codetree --root "$ROOT"
