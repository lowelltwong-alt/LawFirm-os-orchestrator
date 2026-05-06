# Task 005 — Algorithm insight and upgrade scoring

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

Add `AlgorithmInsight` and transparent `upgrade_priority` scoring.

## Deliverables

- model definitions;
- scoring function;
- tests for monotonicity and divide-by-zero protection;
- example insight for an evaluator-guided search method;
- no auto-patches.

## Formula

```text
upgrade_priority = credibility × relevance × expected_lift × verifiability ÷ risk ÷ implementation_cost
```

