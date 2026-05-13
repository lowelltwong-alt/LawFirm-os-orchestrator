# Workflow Atlas Exception Lake Integration

## Current integration

The seed emits a workflow evidence candidate using existing Orchestrator lake clients.

Default mode is `disabled`.

`dry-run` writes a local handoff receipt without touching runtime storage.

`runtime-safe` uses the existing `RuntimeSafeLakeClient` and still requires its environment allow switch.

## Event class and route

Workflow Atlas uses the current canonical route `route.workflow_escalation.v1` and event class `workflow_escalation`.

No new route ID or event class is invented by the Orchestrator.

## Evidence status states

- `supported`: Lake already has matching exception evidence.
- `missing_or_partial`: Lake evidence is missing or not enough.
- `missing_manual`: Pain likely lives outside instrumentation.
- `not_checked`: Evidence lookup has not happened.

## Scale mechanism

Run multiple intakes by the same job role and downstream roles.

Generate integrity reports and capture gaps.

Use manual-shadow-exception events to capture invisible email/spreadsheet/portal work.

Aggregate reviewed workflow signals into pressure vectors only after validation.
