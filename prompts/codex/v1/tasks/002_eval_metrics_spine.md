# Task 002 — Add eval and metrics spine

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

Add a first offline eval harness for `classify-exception` without changing production behavior.

## Allowed paths

- `evals/**`
- `src/lawfirm_os_orchestrator/evals/**`
- `scripts/run_evals.py`
- `tests/**`
- docs updates under `docs/seed` or `docs/architecture*`

## Deliverables

- fixture JSONL;
- gold labels JSONL;
- grader functions;
- CLI/script to run evals;
- metrics JSON output;
- tests proving unknown route/event fails closed.

## Validation

- `python -m pytest`
- `python scripts/run_evals.py --fixture evals/fixtures/classify_exception_cases.jsonl --gold evals/gold/classify_exception_gold.jsonl --stdout json`

