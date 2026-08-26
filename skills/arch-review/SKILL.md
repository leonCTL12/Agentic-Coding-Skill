---
name: arch-review
description: Perform a high-level architectural dependency review and output a uniform Mermaid diagram using Tree-sitter. Trigger when user asks to "review architecture", "draw dependency graph", "check blast radius", "show public contract", or uses "/arch-review".
---

# Architecture & Dependency Review Skill

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed (`uvx` on PATH).
- Cursor MCP server `tree_sitter` running **codetree** (`mcp-server-codetree`). See repo `templates/mcp.json`.
- If `tree_sitter` tools are unavailable, stop and tell the user to finish MCP setup — do not fake an AST review.

When invoked, execute a high-level structural review on the requested target codebase or folder path.

## Execution Steps
1. **Query AST:** Use the `tree_sitter` MCP server tools to inspect public interfaces, exported classes, and public methods in the target path.
2. **Filter Noise:** Do NOT dump internal function bodies, private state, or implementation logic. Focus strictly on API surface and inter-module contracts.
3. **Generate Visual Graph:** Render a clean `mermaid` `classDiagram` showing:
   - Exposed interfaces and public classes.
   - Public methods and return signatures.
   - Direct dependencies and interface implementation links.
4. **Blast Radius Assessment:** Identify downstream modules or consumers that would break if these public contracts were refactored.

## Output Format
- **Public API Surface:** (Bullet list of key contracts and interfaces)
- **Architecture Diagram:** (Mermaid block)
- **Impact & Blast Radius:** (Analysis of upstream/downstream dependencies)
