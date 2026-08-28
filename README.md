# Agentic Coding Skills (personal)

Personal Cursor skills for backup and porting across machines.

| Skill / tool | Needs |
| --- | --- |
| `implement-with-caution` | [mattpocock/skills](https://github.com/mattpocock/skills) (`implement`, `tdd`, `code-review`) |
| `arch-review` | [uv](https://docs.astral.sh/uv/) + MCP **codetree** with C# overlay (`codetree-csharp/`) |
| `no-mistakes` | [no-mistakes](https://github.com/kunchenguid/no-mistakes) + **Cursor CLI** + **acpx** (see below) |

This repo does **not** vendor Matt’s skills — install those once per machine. It **does** vendor the C# delta for [ThinkyMiner/codeTree](https://github.com/ThinkyMiner/codeTree) (PyPI has no `.cs` support).

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

### 3. Install this repo’s skills + C# codetree MCP

```bash
chmod +x ./install.sh ./codetree-csharp/install-codetree.sh
./install.sh
```

That copies:

- `implement-with-caution` → `~/.agents/skills/`
- `arch-review` → `~/.cursor/skills/`
- Bootstraps C#-capable codetree → `~/.local/src/codeTree/` (pinned upstream + overlay)
- Writes `~/.cursor/mcp.json` `tree_sitter` entry (portable `${userHome}` path):

```json
{
  "mcpServers": {
    "tree_sitter": {
      "command": "${userHome}/.local/src/codeTree/run-mcp.sh"
    }
  }
}
```

The launcher uses each Cursor window’s cwd as `--root` (not `~/.cursor`). Do **not** use PyPI `uvx mcp-server-codetree` for C# repos — upstream skips `.cs` files.

See `codetree-csharp/README.md` for upgrade steps and verification (`index_status` / `.cs` count > 0 after MCP reload).

### 4. Reload Cursor

Restart Cursor (or reload MCP servers) so `tree_sitter` tools show up.

### 5. no-mistakes (gate pipeline)

Install [no-mistakes](https://github.com/kunchenguid/no-mistakes) with the upstream one-liner (or any other method from its docs). The upstream README covers the binary; these are the **extra prerequisites** it does not spell out for a Cursor-backed setup.

```bash
curl -fsSL https://raw.githubusercontent.com/kunchenguid/no-mistakes/main/docs/install.sh | sh
no-mistakes --version
```

#### Cursor CLI (`agent`)

Modern Cursor installs the binary as `agent` (not only `cursor-agent`). no-mistakes defaults to `cursor-agent acp`, so override that in config (step 3 below).

```bash
curl https://cursor.com/install -fsSL | bash

# zsh — ensure ~/.local/bin is on PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

agent --version
agent acp --help   # should not error
agent login
```

#### acpx (ACP bridge)

Requires Node.js **22.13+**:

```bash
node --version
npm install -g acpx@latest
acpx --version
```

#### Point no-mistakes at Cursor

Edit `~/.no-mistakes/config.yaml`:

```yaml
agent: cursor
# only if acpx isn't on PATH:
# acpx_path: /path/to/acpx

acp_registry_overrides:
  cursor: agent acp
```

If `agent` lives outside PATH, use the full path:

```yaml
acp_registry_overrides:
  cursor: /Users/you/.local/bin/agent acp
```

You can leave `agent: auto` instead of `agent: cursor` once both binaries are installed — `auto` picks Cursor when it is available.

#### Verify

```bash
no-mistakes doctor
```

You want `cursor` and `acpx` reported as found, and gate validation passing.

#### Optional: GitHub CLI (push / PR / CI)

The full pipeline also pushes and opens a PR. Without `gh`, local steps (review, test, lint) can still run, but push/PR/CI will fail.

```bash
brew install gh
gh auth login
```

#### Per-project setup

Before running the gate on a repository, initialize it once from that repo’s root:

```bash
cd /path/to/your/project
no-mistakes init
```

#### Recover after a failed run

A failed pipeline run can leave the branch in `pipeline_owned` state. Before committing new work:

```bash
no-mistakes axi sync --recover
```

Then re-run validation on your feature branch:

```bash
git checkout feat/your-branch
no-mistakes axi run --intent "<what you set out to accomplish>"
```

#### Alternative agents

If you prefer not to use the Cursor CLI, install one of these and set `agent:` explicitly in `~/.no-mistakes/config.yaml`:

| Agent | Config | Install |
| --- | --- | --- |
| Claude Code | `agent: claude` | [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) |
| Codex | `agent: codex` | [OpenAI Codex CLI](https://github.com/openai/codex) |
| Copilot | `agent: copilot` | `gh extension install github/copilot` |

Run `no-mistakes doctor` again after switching.

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
codetree-csharp/          # C# overlay + bootstrap for ThinkyMiner/codeTree
  PIN, patches/, overlay/, install-codetree.sh, run-mcp.sh, README.md
templates/
  mcp.json
install.sh
README.md
```
