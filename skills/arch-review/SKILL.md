---
name: arch-review
description: Perform a high-level architectural dependency review using Tree-sitter and output markdown analysis plus a static HTML report in the repo. Trigger when user asks to "review architecture", "draw dependency graph", "check blast radius", "show public contract", or uses "/arch-review".
---

# Architecture & Dependency Review Skill

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed (`uvx` on PATH).
- MCP server `tree_sitter` running **codetree** with C# support if reviewing `.cs`. On a new machine: clone Agentic-Coding-Skill and run `./install.sh` (bootstraps `codetree-csharp/` → `~/.local/src/codeTree/` and merges `templates/mcp.json` into `~/.cursor/mcp.json`). Do **not** use PyPI `uvx mcp-server-codetree` alone — it skips `.cs`.
- If `tree_sitter` tools are unavailable, stop and tell the user to finish MCP setup — do not fake an AST review.

When invoked, execute a high-level structural review on the requested target codebase or folder path.

## Execution Steps

1. **Query AST:** Use the `tree_sitter` MCP server tools to inspect public interfaces, exported classes, and public methods in the target path.
2. **Filter Noise:** Do NOT dump internal function bodies, private state, or implementation logic. Focus strictly on API surface and inter-module contracts.
3. **Assign Layers:** Place each public type into exactly one architectural layer (see rules below).
4. **Build Data Model:** Populate the review schema (see below) from AST findings. This is the single source of truth for the HTML report and markdown sections.
5. **Write HTML report:** Create a self-contained `.html` file in the repo (see HTML section). Start from `TEMPLATE.html` in this skill directory (same folder as this file; installed at `~/.cursor/skills/arch-review/`).
6. **Blast Radius Assessment:** Write prose + dependency table in markdown. The HTML report mirrors the same data interactively.

Do **not** output Mermaid diagrams or Cursor Canvas files. Mermaid layout breaks for layered graphs; static HTML avoids IDE lock-in.

## Layer Assignment Rules

Assign each public type to one layer. Use path/name heuristics; when ambiguous, prefer the layer that matches its primary consumer.

| Layer | Typical contents | Heuristics | Color (HTML) |
| --- | --- | --- | --- |
| **API** | Controllers, endpoints, HTTP handlers | `*Controller`, `Controllers/`, route attributes | blue |
| **Application** | Services, use-case orchestration | `*Service`, `Services/`, `I*Service` | purple |
| **Persistence** | Repositories, stores, data access | `*Repository`, `Repositories/`, `I*Repository` | green |
| **Domain** | Entities, enums, value objects | `Models/`, `Entities/`, `*Status`, `*Severity`, core nouns | yellow |
| **Contracts** | Request/response DTOs, validation attributes | `*Request`, `*Response`, `Validation/`, `*Attribute` | cyan |

Omit empty layers. If the codebase has no separate Application layer, merge services into Persistence or Domain as appropriate and note the simplification in markdown.

## Review Data Schema

Embed this JSON in the HTML `<script id="arch-data" type="application/json">` block. Keep member lists complete in data; the template truncates display at 12 members per type (`+N more…`).

```json
{
  "title": "Alert API — architecture review",
  "target": "src/Risksis.AlertApi",
  "types": [
    {
      "id": "AlertsController",
      "name": "AlertsController",
      "layer": "API",
      "kind": "class",
      "members": ["+Create(...) Task<ActionResult<Alert>>"],
      "note": "optional, e.g. extends CreateAlertRequest"
    }
  ],
  "edges": [
    { "from": "AlertsController", "to": "IAlertRepository", "relationship": "uses" }
  ],
  "blastRadius": [
    {
      "ifChanged": "IAlertRepository",
      "affected": ["AlertsController", "DetectionsController"],
      "risk": "high",
      "note": "optional"
    }
  ]
}
```

Field rules:
- `id`: stable key, usually the type name (must match `from` / `to` in edges).
- `layer`: one of `API` | `Application` | `Persistence` | `Domain` | `Contracts`.
- `kind`: `class` | `interface` | `enum` | `record`.
- `relationship`: `uses` | `implements` | `extends`.

### Member label rules

- **Classes / records:** public properties and methods (`+` prefix).
- **Interfaces:** public method signatures.
- **Enums:** member names only (e.g. `Open`, `Acknowledged`).
- **Request DTOs:** public properties only.
- Fold composition into member lists: `+Status: AlertStatus` on `Alert`, not a graph edge.
- Fold inheritance into `note`: `"extends CreateAlertRequest"`.

### Edge rules (contract graph)

Include **only** cross-layer contracts in `edges`:

- controllers → interfaces they inject
- interface → concrete implementer (`implements`)
- service/repository → domain entity they operate on

**Exclude from edges:** enum nodes, request DTOs, property-level composition (`Alert → AlertStatus`). Those belong in type `members` only.

If the codebase is large, cap the graph at ~20 types and ~15 edges — show highest-risk contracts in the graph; list the rest in markdown **Public API Surface** only.

## HTML Report Requirements

Write **one self-contained file** — no build step, no npm, no CDN, no Cursor APIs.

### Output path

Default (commit-friendly):

```
docs/architecture/<target-slug>-arch-review.html
```

- `<target-slug>`: kebab-case from project or folder name (e.g. `alert-api-arch-review.html`).
- Create `docs/architecture/` if missing.

If the user or repo treats reviews as scratch work only, use:

```
.scratch/arch-review/<target-slug>-arch-review.html
```

Do not write under `.cursor/projects/…/canvases/`.

### How to author

1. Copy `TEMPLATE.html` from this skill directory to the output path.
2. Replace the JSON inside `<script id="arch-data" type="application/json">` with findings.
3. Update `<title>` and header text to match `review.title` / `review.target` (the template JS also sets these from JSON).
4. **Do not remove** the inline `<style>` or trailing `<script>` — they power the UI.

### Three panels (template provides all of this)

| Panel | Behavior |
| --- | --- |
| **Layer explorer** | `<details>` per layer (API open by default); nested `<details>` per type with full `members` |
| **Contract graph** | SVG DAG layout; click node → highlight upstream + downstream; layer filter dropdown |
| **Blast radius** | Table with risk row tinting (high / medium) |

### HTML authoring rules

- Single file only. No external assets required.
- Valid JSON in `arch-data` (escape `"` inside strings).
- **Never render empty sections** — omit layers/types with no data from the JSON.
- Open in any browser: `open docs/architecture/…html` (macOS) or file:// URL.

When mentioning the report in chat, link the **repo-relative path** (e.g. `docs/architecture/alert-api-arch-review.html`) and suggest opening it in a browser.

## Output Format (chat markdown)

Return these sections in order:

1. **Public API Surface** — bullet list of key contracts, interfaces, and DTOs (with one-line role each).
2. **Impact & Blast Radius** — prose analysis of what breaks if public contracts change; include a markdown table mirroring `blastRadius` data:

   | If changed | Affected | Risk | Note |
   | --- | --- | --- | --- |
   | `IAlertRepository` | `AlertsController`, `DetectionsController` | high | both controllers inject directly |

3. **Interactive report** — one sentence + repo path. Example: "Open `docs/architecture/alert-api-arch-review.html` in a browser to explore layers and click graph nodes to highlight dependents."

Do **not** duplicate the full member lists in chat — those live in the HTML layer explorer.

## Fallback

If HTML generation fails after one fix attempt, still deliver markdown sections 1–2 plus a **Contract dependencies** table:

| From | To | Relationship |
| --- | --- | --- |
| `AlertsController` | `IAlertRepository` | uses |

Tell the user what failed and where the partial file is.

## Notes

- Per-repo `.codetree/` caches are normal; do not treat them as architecture.
- Layer explorer = full public surface. Contract graph = wiring only. The HTML template keeps them in separate sections — same fix as the old Mermaid mess.
- This workflow is IDE-agnostic: commit the HTML, share the file, open in Chrome/Firefox/Safari; no Cursor required.
