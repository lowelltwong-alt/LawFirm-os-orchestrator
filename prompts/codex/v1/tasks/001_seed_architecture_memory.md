# Task 001 — Seed architecture memory docs

**Codex level:** Medium


## Required opening statement

Before editing, state:

```text
Route:
Mode:
Allowed paths:
Forbidden paths:
Contract surfaces touched:
Validation plan:
Stop conditions:
Expected artifacts:
Codex level:
```

## Global constraints

- No real client/matter data.
- No Semantic Substrate writes.
- No Lake runtime ingest by default.
- No autonomous self-patching.
- No production connectors.
- No framework expansion unless the task explicitly asks.

## Goal

Add this seed pack into the Orchestrator repo as architecture memory.

## Allowed paths

- `docs/seed/**`
- `prompts/codex/v1/**`
- `README_Codex_V1_Seed.md`
- `scripts/README_SEED_PACK.md`

## Tasks

1. Verify current repo tests still pass.
2. Ensure seed docs are present and readable.
3. Add links from `AI_WORK_START_HERE.md` or `AGENTS.md` to `docs/seed/00_CODEX_READ_FIRST.md` if those files exist.
4. Do not change runtime behavior.

## Validation

- `python -m pytest`
- `git diff --check`

