# codetree + C# overlay

Upstream [ThinkyMiner/codeTree](https://github.com/ThinkyMiner/codeTree) has no `.cs` plugin. This package vendors the **delta** (C# `LanguagePlugin`, registry/pyproject/indexer patches) and bootstraps a pinned checkout at `~/.local/src/codeTree`.

PyPI `mcp-server-codetree` is unchanged — do **not** use `uvx --from mcp-server-codetree` if you need C# indexing.

## One-time install

From this repo root (requires `git` and [uv](https://docs.astral.sh/uv/)):

```bash
chmod +x codetree-csharp/install-codetree.sh
./codetree-csharp/install-codetree.sh
```

Or run the top-level installer (skills + codetree + MCP config):

```bash
./install.sh
```

That writes `~/.cursor/mcp.json` (or merges) with:

```json
{
  "mcpServers": {
    "tree_sitter": {
      "command": "${userHome}/.local/src/codeTree/run-mcp.sh"
    }
  }
}
```

Restart Cursor (or reload MCP servers). Server name stays **`tree_sitter`** — `/arch-review` depends on it.

## Verify

1. Open a C# repo in Cursor.
2. After MCP connects, ask the agent to call `index_status` on the `tree_sitter` MCP (or run locally):

```bash
uv run --directory ~/.local/src/codeTree codetree --root /path/to/csharp/repo index build
uv run --directory ~/.local/src/codeTree python -c "
from codetree.indexer import Indexer
i = Indexer('/path/to/csharp/repo')
i.build()
cs = [p for p in i.files if p.suffix == '.cs']
print(f'.cs files indexed: {len(cs)}')
"
```

Expect `.cs files indexed` > 0. MSBuild `bin/` and `obj/` dirs are skipped.

Plugin unit tests (also run by the installer):

```bash
uv run --directory ~/.local/src/codeTree --with pytest \
  pytest tests/languages/test_csharp.py -v
```

## Upgrade when upstream moves

1. Pick a new upstream commit (test without C# regressions).
2. Update `codetree-csharp/PIN`.
3. Re-run `./codetree-csharp/install-codetree.sh` — it resets the checkout, reapplies patches, and re-runs tests.
4. If upstream changed `registry.py`, `pyproject.toml`, or `indexer.py`, refresh `patches/csharp-support.patch`:

```bash
cd ~/.local/src/codeTree
git checkout PIN
# apply overlay manually, then:
git diff HEAD -- pyproject.toml src/codetree/registry.py src/codetree/indexer.py \
  > /path/to/Agentic-Coding-Skill/codetree-csharp/patches/csharp-support.patch
```

## Layout

```text
codetree-csharp/
  PIN                              # pinned upstream commit
  patches/csharp-support.patch     # registry, pyproject, indexer delta
  overlay/                         # new csharp.py + tests
  install-codetree.sh              # clone, patch, uv sync, test
  run-mcp.sh                       # copied to ~/.local/src/codeTree/
```

Install location override: `CODETREE_INSTALL_DIR=/other/path ./codetree-csharp/install-codetree.sh`

## tree-sitter ABI note

Pin `tree-sitter-c-sharp>=0.23.1` (installer resolves latest compatible). Mismatch between `tree-sitter` and grammar wheels can segfault — let `uv sync` pick a consistent set. Known-good combo: `tree-sitter` 0.26.x + `tree-sitter-c-sharp` 0.23.5.
