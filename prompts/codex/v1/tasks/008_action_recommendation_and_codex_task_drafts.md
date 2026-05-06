# Task 008 — Action recommendations and Codex task drafts

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

Allow the Orchestrator to draft its own future Codex work requests as artifacts.

## Deliverables

- `ActionRecommendation` schema;
- `CodexTaskDraft` schema;
- markdown renderer for Codex task drafts;
- tests proving drafts are not executed.

## Required language in every draft

- Codex level;
- allowed paths;
- forbidden paths;
- validation plan;
- stop conditions.

