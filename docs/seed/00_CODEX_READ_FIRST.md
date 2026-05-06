# 00 — Codex Read First

## Codex level

- Whole V1 buildout: **Extra High**
- Individual task files in this pack: mostly **High**, some **Medium**

## Operating rule

Do not turn this repository into a general agent platform. Build a contract-governed execution kernel that produces evidence, measurements, learning proposals, research-derived upgrade hypotheses, and human-reviewable action recommendations.

## Authority split

| Plane | Repo/System | Owns | Must not own |
|---|---|---|---|
| Authority | `LawFirm-os-semantic-substrate` | schemas, registries, route IDs, event classes, governance doctrine, promotion decisions | runtime state or ad hoc semantic rewrites |
| Execution | `LawFirm-os-orchestrator` | bounded workflows, model/tool routing, policy gates, ledgers, evidence packets, evals, upgrade proposals | canonical semantics or substrate mutation |
| Evidence | `LawFirm-os-exceptions-lake-runtime` | validated runtime events, audit records, learning candidates, pressure vectors | canonical schemas, route IDs, or promotion authority |

## First V1 principle

Do not build autonomy first. Build evidence, evals, and learning proposals first.

The Orchestrator may generate:

- `DiscoverySignal`
- `AlgorithmInsight`
- `UpgradeHypothesis`
- `ExperimentPlan`
- `ShadowEvalResult`
- `UpgradeProposal`
- `ActionRecommendation`
- `CodexTaskDraft`

It must not automatically apply code patches, mutate substrate canon, or enable runtime ingest by default.

## Required Codex behavior

Before editing files, Codex must state:

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

If the task is too broad, Codex must narrow it to a PR-sized slice instead of improvising.
