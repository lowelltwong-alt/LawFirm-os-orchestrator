# Task 007 — Upgrade proposal packets

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

Generate reviewable upgrade proposal directories.

## Output shape

```text
.lawfirm-os-orchestrator/upgrade_proposals/<proposal_id>/
├── proposal.json
├── evidence_refs.json
├── experiment_plan.json
├── shadow_eval_result.json
├── risk_review.md
└── codex_task_draft.md
```

## Constraint

The proposal generator may recommend a patch; it must not apply it.

