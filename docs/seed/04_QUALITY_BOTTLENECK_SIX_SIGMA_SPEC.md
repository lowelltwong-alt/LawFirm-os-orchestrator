# 04 — Quality, Bottleneck, and Six Sigma Spec

## Primary throughput unit

```text
accepted, contract-locked proposed exception packets per reviewer hour
```

Do not optimize for:

- number of agents;
- number of model calls;
- prompt length;
- dashboard count;
- raw event count;
- autonomous action count.

## First bottleneck

Trusted review capacity at the governance boundary.

The Orchestrator should reduce reviewer rework by producing packets that are:

- contract-pinned;
- route-valid;
- event-class-valid;
- schema-valid;
- evidence-sufficient;
- provenance-complete;
- approval-ready;
- Lake-admissible when Lake mode is enabled.

## DMAIC mapping

| DMAIC | Orchestrator interpretation |
|---|---|
| Define | Define CTQs, stop conditions, risk tiers, packet acceptance criteria |
| Measure | Ledger every controlled step and metric |
| Analyze | Pareto defects by route/event/prompt/model/validator |
| Improve | Propose prompt/validator/router/evidence-template changes |
| Control | Shadow eval, approval, versioning, rollback |

## CTQs

- Contract conformance
- Evidence completeness
- Controlled autonomy
- Provenance completeness
- Human-governed finality
- Security/privacy containment
- Cost/time discipline
- Recovery and replayability

## Defect taxonomy

- semantic defect;
- structural defect;
- provenance defect;
- lineage defect;
- governance defect;
- privacy defect;
- temporal/stale-contract defect;
- duplication defect;
- retry/budget defect;
- tool defect;
- model defect;
- audit defect.

## Control gates

Every command must pass:

1. input/schema gate;
2. synthetic-only gate;
3. manifest/contract gate;
4. route/event allowlist gate;
5. model-output schema gate;
6. evidence completeness gate;
7. ledger append gate;
8. Lake mode gate;
9. human approval gate where required.
