# Task 003 — Add learning object models

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

Add strict Pydantic models for governed learning loops.

## Models

- ReviewerLabel
- DefectTag
- LearningCandidate
- PressureVectorRef
- UpgradeHypothesis
- ExperimentPlan
- ShadowEvalResult
- UpgradeProposal
- ActionRecommendation
- CodexTaskDraft

## Requirements

- `extra="forbid"` or equivalent.
- No code path applies patches.
- No substrate/lake writes.
- Serialization round-trip tests.

