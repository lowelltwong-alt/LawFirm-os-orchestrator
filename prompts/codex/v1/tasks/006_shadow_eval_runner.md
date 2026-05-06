# Task 006 — Shadow eval runner

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

Add a shadow eval runner for proposed changes.

## Requirements

- It must not change production defaults.
- It must compare baseline vs proposal metrics.
- It must produce `ShadowEvalResult` JSON.
- It must fail closed on missing fixtures/gold labels.

