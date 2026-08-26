#!/usr/bin/env bash
# Install personal skills from this repo onto the current machine.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
AGENTS_SKILLS="${HOME}/.agents/skills"
CURSOR_SKILLS="${HOME}/.cursor/skills"
MCP_JSON="${HOME}/.cursor/mcp.json"
TEMPLATE_MCP="${ROOT}/templates/mcp.json"

mkdir -p "${AGENTS_SKILLS}" "${CURSOR_SKILLS}" "$(dirname "${MCP_JSON}")"

echo "==> Installing implement-with-caution → ${AGENTS_SKILLS}/"
cp -R "${ROOT}/skills/implement-with-caution" "${AGENTS_SKILLS}/"

echo "==> Installing arch-review → ${CURSOR_SKILLS}/"
cp -R "${ROOT}/skills/arch-review" "${CURSOR_SKILLS}/"

echo
echo "==> Checking prerequisites"

if ! command -v uvx >/dev/null 2>&1; then
  echo "    [missing] uvx — install uv:"
  echo "      curl -LsSf https://astral.sh/uv/install.sh | sh"
  echo "    Then restart the shell so uvx is on PATH."
else
  echo "    [ok] uvx: $(command -v uvx) ($(uvx --version 2>/dev/null | head -1))"
fi

if [[ -f "${AGENTS_SKILLS}/implement/SKILL.md" && -f "${AGENTS_SKILLS}/tdd/SKILL.md" ]]; then
  echo "    [ok] mattpocock implement + tdd siblings present"
else
  echo "    [missing] mattpocock skills (need implement + tdd next to implement-with-caution)"
  echo "      npx skills@latest add mattpocock/skills"
  echo "    Include at least: setup-matt-pocock-skills, implement, tdd, code-review"
fi

if [[ -f "${MCP_JSON}" ]] && grep -q 'mcp-server-codetree' "${MCP_JSON}" 2>/dev/null; then
  echo "    [ok] ${MCP_JSON} already mentions mcp-server-codetree"
else
  echo "    [todo] merge tree_sitter MCP into ${MCP_JSON}"
  echo "    Template: ${TEMPLATE_MCP}"
  if [[ ! -f "${MCP_JSON}" ]]; then
    cp "${TEMPLATE_MCP}" "${MCP_JSON}"
    echo "    Wrote new ${MCP_JSON} from template (uses 'uvx' on PATH)."
  else
    echo "    File exists — merge the tree_sitter block from templates/mcp.json manually."
    echo "    Prefer \"command\": \"uvx\" (not a machine-specific absolute path)."
  fi
fi

echo
echo "Done. Restart Cursor (or reload MCP) so arch-review can see tree_sitter."
echo "Invoke: /implement-with-caution  |  /arch-review"
