#!/usr/bin/env bash
# Install personal skills from this repo onto the current machine.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
AGENTS_SKILLS="${HOME}/.agents/skills"
CURSOR_SKILLS="${HOME}/.cursor/skills"
MCP_JSON="${HOME}/.cursor/mcp.json"
TEMPLATE_MCP="${ROOT}/templates/mcp.json"
CODETREE_INSTALL="${ROOT}/codetree-csharp/install-codetree.sh"
CODETREE_LAUNCHER="${HOME}/.local/src/codeTree/run-mcp.sh"

mkdir -p "${AGENTS_SKILLS}" "${CURSOR_SKILLS}" "$(dirname "${MCP_JSON}")"

echo "==> Installing implement-with-caution → ${AGENTS_SKILLS}/"
cp -R "${ROOT}/skills/implement-with-caution" "${AGENTS_SKILLS}/"

ARCH_REVIEW_SRC="${ROOT}/skills/arch-review"
if [[ ! -f "${ARCH_REVIEW_SRC}/SKILL.md" || ! -f "${ARCH_REVIEW_SRC}/TEMPLATE.html" ]]; then
  echo "    [error] arch-review needs SKILL.md and TEMPLATE.html in ${ARCH_REVIEW_SRC}" >&2
  exit 1
fi
echo "==> Installing arch-review → ${CURSOR_SKILLS}/"
cp -R "${ARCH_REVIEW_SRC}" "${CURSOR_SKILLS}/"

echo
echo "==> Checking prerequisites"

if ! command -v uv >/dev/null 2>&1 && [[ ! -x "${HOME}/.local/bin/uv" ]]; then
  echo "    [missing] uv — install uv:"
  echo "      curl -LsSf https://astral.sh/uv/install.sh | sh"
  echo "    Then restart the shell so uv is on PATH."
else
  UV_BIN="$(command -v uv 2>/dev/null || echo "${HOME}/.local/bin/uv")"
  echo "    [ok] uv: ${UV_BIN} ($("${UV_BIN}" --version 2>/dev/null | head -1))"
fi

if [[ -f "${AGENTS_SKILLS}/implement/SKILL.md" && -f "${AGENTS_SKILLS}/tdd/SKILL.md" ]]; then
  echo "    [ok] mattpocock implement + tdd siblings present"
else
  echo "    [missing] mattpocock skills (need implement + tdd next to implement-with-caution)"
  echo "      npx skills@latest add mattpocock/skills"
  echo "    Include at least: setup-matt-pocock-skills, implement, tdd, code-review"
fi

echo
echo "==> Installing C#-capable codetree MCP server"
if [[ ! -x "${CODETREE_INSTALL}" ]]; then
  echo "    [error] missing ${CODETREE_INSTALL}" >&2
  exit 1
fi
"${CODETREE_INSTALL}"

echo
echo "==> Configuring global Cursor MCP (tree_sitter)"
export TEMPLATE_MCP
python3 <<'PY'
import json
import os

mcp_path = os.path.expanduser("~/.cursor/mcp.json")

with open(os.environ["TEMPLATE_MCP"]) as f:
    template = json.load(f)

tree_sitter = template["mcpServers"]["tree_sitter"]

if os.path.isfile(mcp_path):
    with open(mcp_path) as f:
        data = json.load(f)
else:
    data = {}

servers = data.setdefault("mcpServers", {})
prev = servers.get("tree_sitter")
servers["tree_sitter"] = tree_sitter

os.makedirs(os.path.dirname(mcp_path), exist_ok=True)
with open(mcp_path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")

if prev != tree_sitter:
    print(f"    Updated tree_sitter in {mcp_path}")
    print(f"    command: {tree_sitter['command']}")
else:
    print(f"    [ok] tree_sitter already configured in {mcp_path}")
PY

if [[ -x "${CODETREE_LAUNCHER}" ]]; then
  echo "    [ok] launcher present: ${CODETREE_LAUNCHER}"
else
  echo "    [warn] launcher missing at ${CODETREE_LAUNCHER} — re-run codetree-csharp/install-codetree.sh"
fi

echo
echo "Done. Restart Cursor (or reload MCP) so arch-review can see tree_sitter."
echo "Invoke: /implement-with-caution  |  /arch-review"
echo "C# codetree docs: codetree-csharp/README.md"
