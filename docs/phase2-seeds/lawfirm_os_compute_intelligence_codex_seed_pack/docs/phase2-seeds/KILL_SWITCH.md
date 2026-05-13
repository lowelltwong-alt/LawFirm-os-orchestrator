# Compute Intelligence Kill Switch Seed

## Status

Seed only. Not implemented.

## Purpose

Every future Compute Intelligence implementation must include a simple way to
disable outputs without breaking the rest of LawFirm OS.

## Required future behavior

- If Compute Intelligence is disabled, fall back to prior static allocation.
- If optimizer evidence is missing, corrupted, cross-regime, or stale, fail closed
  to `proposal_not_available` rather than blocking core workflows.
- If Monte Carlo or game-state analysis fails, do not make a recommendation.
- If any output tries to override RYG, restore green, mutate canon, or authorize
  external action, the output is invalid.

## Minimum config flags for future implementation

```yaml
compute_intelligence:
  enabled: false
  allow_optimizer_recommendations: false
  allow_scenario_simulation: false
  allow_research_radar_scoring: false
  require_human_review_for_all_outputs: true
```

## Authority rule

The kill switch does not grant authority. It only disables advisory outputs.
Substrate remains the control plane, Orchestrator remains execution-only, and
Exception Lake remains evidence-only.
