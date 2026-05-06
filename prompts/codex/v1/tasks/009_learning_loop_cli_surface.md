# Task 009 — Learning loop CLI surface

**Codex level:** High


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

Expose small CLI commands for learning artifacts.

## Candidate commands

```bash
python -m lawfirm_os_orchestrator learning label-run --run-id ... --route-id ... --event-class ... --defect-tag ...
python -m lawfirm_os_orchestrator learning propose-upgrade --from-defects ... --out ...
```

## Constraints

- Local artifacts only.
- No automatic commits.
- No external network.
- No real data.

