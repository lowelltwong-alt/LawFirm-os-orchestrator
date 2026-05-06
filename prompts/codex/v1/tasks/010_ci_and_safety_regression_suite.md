# Task 010 — CI and safety regression suite

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

Add CI/test coverage for V1 safety boundaries.

## Tests must prove

- substrate client has no write methods;
- Lake mode defaults disabled;
- runtime-safe requires dual opt-in;
- real-data flags fail;
- unknown route/event fails;
- research signals cannot trigger code execution;
- upgrade proposals cannot apply themselves;
- ledger failures fail the run.

