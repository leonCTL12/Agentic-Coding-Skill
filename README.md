# Agentic Coding Skills (personal)

Personal Cursor skills for backup and porting across machines.

| Skill | Needs |
| --- | --- |
| `implement-with-caution` | [mattpocock/skills](https://github.com/mattpocock/skills) (`implement`, `tdd`, `code-review`) |
| `arch-review` | [uv](https://docs.astral.sh/uv/) + MCP **codetree** (`mcp-server-codetree`) |

This repo does **not** vendor Matt’s skills or the MCP server — install those once per machine.

## New machine setup

```bash
git clone https://github.com/leonCTL12/Agentic-Coding-Skill.git
cd Agentic-Coding-Skill
```

### 1. Install uv (provides `uvx`)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# restart shell, confirm:
uvx --version
```

### 2. Install Matt Pocock skills

```bash
npx skills@latest add mattpocock/skills
```

Pick at least: `setup-matt-pocock-skills`, `implement`, `tdd`, `code-review`.  
They should land under `~/.agents/skills/` so sibling paths from `implement-with-caution` resolve.

### 3. Install this repo’s skills + MCP hint

```bash
chmod +x ./install.sh
./install.sh
```

That copies:

- `implement-with-caution` → `~/.agents/skills/`
- `arch-review` → `~/.cursor/skills/`

And ensures `~/.cursor/mcp.json` includes (or prompts you to merge) the portable snippet in `templates/mcp.json`:

```json
{
  "mcpServers": {
    "tree_sitter": {
      "command": "uvx",
      "args": [
        "--from",
        "mcp-server-codetree",
        "codetree",
        "--root",
        "${workspaceFolder}"
      ]
    }
  }
}
```

Use `"command": "uvx"` on PATH — do not hardcode `/Users/.../.local/bin/uvx`.

### 4. Reload Cursor

Restart Cursor (or reload MCP servers) so `tree_sitter` tools show up.

## Updating after you edit skills elsewhere

Edit under `skills/` in this repo (or copy back from `~/.agents/skills` / `~/.cursor/skills`), then:

```bash
git add -A && git commit -m "..." && git push
# on each machine:
git pull && ./install.sh
```

## Layout

```text
skills/
  implement-with-caution/SKILL.md
  arch-review/SKILL.md
templates/
  mcp.json
install.sh
README.md
```
