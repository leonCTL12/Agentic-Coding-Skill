#!/usr/bin/env bash
# Bootstrap a C#-capable mcp-server-codetree checkout from upstream + local overlay.
set -euo pipefail

PKG_ROOT="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="${CODETREE_INSTALL_DIR:-${HOME}/.local/src/codeTree}"
UPSTREAM="https://github.com/ThinkyMiner/codeTree.git"
PIN="$(tr -d '[:space:]' < "${PKG_ROOT}/PIN")"
PATCH="${PKG_ROOT}/patches/csharp-support.patch"
OVERLAY="${PKG_ROOT}/overlay"

if ! command -v git >/dev/null 2>&1; then
  echo "git is required" >&2
  exit 1
fi

UV="${UV:-}"
if [[ -z "$UV" ]]; then
  if command -v uv >/dev/null 2>&1; then
    UV="$(command -v uv)"
  elif [[ -x "${HOME}/.local/bin/uv" ]]; then
    UV="${HOME}/.local/bin/uv"
  else
    echo "uv is required — install from https://docs.astral.sh/uv/" >&2
    exit 1
  fi
fi

echo "==> Installing C#-capable codetree"
echo "    upstream: ${UPSTREAM} @ ${PIN}"
echo "    install:  ${INSTALL_DIR}"

mkdir -p "$(dirname "${INSTALL_DIR}")"

if [[ -d "${INSTALL_DIR}/.git" ]]; then
  echo "==> Fetching upstream"
  git -C "${INSTALL_DIR}" fetch --tags origin
else
  echo "==> Cloning upstream (shallow)"
  git clone --filter=blob:none "${UPSTREAM}" "${INSTALL_DIR}"
  git -C "${INSTALL_DIR}" fetch --tags origin
fi

echo "==> Checking out pinned commit"
git -C "${INSTALL_DIR}" checkout --force "${PIN}"
git -C "${INSTALL_DIR}" clean -fd

echo "==> Applying C# overlay"
git -C "${INSTALL_DIR}" apply --check "${PATCH}"
git -C "${INSTALL_DIR}" apply "${PATCH}"
cp "${OVERLAY}/src/codetree/languages/csharp.py" \
   "${INSTALL_DIR}/src/codetree/languages/csharp.py"
cp "${OVERLAY}/tests/languages/test_csharp.py" \
   "${INSTALL_DIR}/tests/languages/test_csharp.py"
cp "${PKG_ROOT}/run-mcp.sh" "${INSTALL_DIR}/run-mcp.sh"
chmod +x "${INSTALL_DIR}/run-mcp.sh"

echo "==> Syncing Python dependencies (uv)"
"$UV" sync --directory "${INSTALL_DIR}"

echo "==> Running C# plugin tests"
"$UV" run --directory "${INSTALL_DIR}" --with pytest \
  pytest tests/languages/test_csharp.py -v

echo
echo "Done. MCP launcher: ${INSTALL_DIR}/run-mcp.sh"
echo "Point ~/.cursor/mcp.json tree_sitter command at that path (see templates/mcp.json)."
