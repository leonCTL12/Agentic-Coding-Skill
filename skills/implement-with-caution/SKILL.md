---
name: implement-with-caution
description: "Same as /implement, but pause for human review before declaration or test changes. Use when learning a codebase and /implement moves too fast."
disable-model-invocation: true
---

# Implement with caution

Delta over `/implement`: same outer flow and `/tdd` loop; **pause** before declaration or test edits so the human keeps the contract in their head. **Tests are the contract** — if bad behaviour ships, strengthen the tests; do not add implementation-review gates.

## Prerequisites

- [mattpocock/skills](https://github.com/mattpocock/skills) installed so `implement` and `tdd` are siblings of this skill (same skills root).
- Install location for this skill: `~/.agents/skills/implement-with-caution` (next to Matt's skills).

## Base (do not fork)

1. Read and follow [`../implement/SKILL.md`](../implement/SKILL.md) for the outer flow (tdd, typecheck, `/code-review`). Skip its commit step — see **Git** below.
2. When that flow uses `/tdd`, read and follow [`../tdd/SKILL.md`](../tdd/SKILL.md) for loop rules, seams, and anti-patterns.
3. Keep implement/tdd's **natural work order**. This skill only inserts pauses; it does not reorder slices or batch seams differently.

Re-read those files each run. Own only the pause rules below so upstream updates still apply.

## Pause rules

Before writing a **declaration** change (public signature / type surface — new or edited), stop:

1. Show the proposed declaration (and only that).
2. Wait for explicit okay.
3. Then write it. Do not advance to tests or implementation in the same turn.

Before writing a **test** change (any edit to a test file), stop:

1. Show the proposed test change (and only that).
2. Wait for explicit okay.
3. Then write it. Do not implement in the same turn.

**No pause** for implementation-only edits (including bugfixes that do not touch tests). Green against the agreed tests is enough.

If one slice needs both a declaration and a test, pause twice in the order the loop naturally reaches them (usually declaration, then test), never as one combined dump of unrelated seams.

## Git

Do **not** commit or push unless the user explicitly asks. Leave all changes uncommitted on the working tree so the human can review the full diff first.

## Completion

After the work is done, finish the rest of `/implement` (full suite once, `/code-review`) with no extra gates unless a declaration or test still needs changing. Skip the commit step from `/implement` unless the user explicitly asks for it.
