# 03 — Learning Loop and Research Radar Spec

## Five governed learning loops

### Loop 1 — Run-level learning

Every run captures input, manifest pin, route candidates, model output, validation result, policy result, evidence completeness, Lake receipt/rejection, reviewer corrections, and defect tags.

### Loop 2 — Pressure-vector learning

Repeated defects become pressure vectors. Pressure vectors identify affected surface, cohort, recurrence, impact, detectability, candidate causes, and smallest plausible intervention.

### Loop 3 — Eval learning

Every proposed change must be shadow-evaluated on fixtures/gold labels before recommendation.

### Loop 4 — Governance/promotion learning

If the issue is orchestrator-local, propose an orchestrator change. If the issue is semantic, produce a substrate change request; do not mutate canon.

### Loop 5 — External discovery learning / Research Radar

External research becomes method evidence. It may inform hypotheses and experiments. It does not become authority.

## Research Radar V1 local mode

Start with curated JSON files, not a web crawler.

### DiscoverySignal

```json
{
  "schema_version": "1.0",
  "signal_type": "external_research_discovery",
  "source_kind": "paper|benchmark|lab_blog|standard|repository|human_note",
  "source_uri": "https://example.org/source",
  "title": "Example discovery",
  "published_at": "2026-05-01",
  "claims": [
    {
      "claim": "A method improves verifier-guided search.",
      "claim_type": "algorithmic_pattern",
      "evidence_strength": "medium_high"
    }
  ],
  "relevance": {
    "orchestrator_surfaces": ["evals", "model_router", "experiment_planner"],
    "possible_upgrade": "Add shadow verifier loop for prompt/validator changes.",
    "risk": "No autonomous code mutation."
  },
  "recommended_action": "create_shadow_experiment"
}
```

### Upgrade priority score

```text
upgrade_priority =
  credibility
  × relevance
  × expected_lift
  × verifiability
  ÷ risk
  ÷ implementation_cost
```

All score inputs must be explicit. No hidden model-only scoring.

## Self-action recommendation boundary

Allowed:

- recommend a Codex task;
- draft patch instructions;
- draft tests;
- draft human review checklist;
- explain expected metric lift.

Forbidden:

- executing the Codex task automatically;
- applying self-patches automatically;
- pushing branches;
- changing substrate canon;
- changing Lake persistence rules;
- enabling real data or runtime ingest.
