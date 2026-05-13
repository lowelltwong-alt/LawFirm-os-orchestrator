# Frontier Math / Algorithmic Breakthrough Radar

## Purpose

Frontier Math Radar monitors potential math, algorithmic, and AI capability breakthroughs that could change LawFirm OS strategy.

This is a seed concept only. It must not add live research automation.

## What counts as relevant frontier math

A math or algorithmic improvement is relevant only if it can plausibly improve one of:

- legal retrieval quality;
- proof/citation verification;
- planning/search over workflows;
- token compression;
- eval reliability;
- error bounds;
- ranking/triage optimization;
- privacy-preserving learning;
- graph reasoning over matters/workflows;
- scheduling/portfolio optimization;
- formal verification of policy constraints.

## Breakthrough readiness score

The seed readiness score is **not** a raw product/division formula. Inputs must be
normalized 0..1 with explicit semantics, where higher means better except for
`normalized_prep_cost`, `uncertainty_level`, and `downside_risk`, which are
converted to bounded penalties.

```text
benefit_score = weighted_geometric_mean(
  relevance_to_os,
  probability_of_arrival,
  first_mover_advantage,
  prep_reuse_value,
  integration_speed_advantage
)

penalty_score = weighted_geometric_mean(
  1 - normalized_prep_cost,
  1 - uncertainty_level,
  1 - downside_risk,
  1 - reputation_tail_risk
)

time_discount = exp(-time_horizon_days / 180)

readiness_score_0_to_100 = 100 * benefit_score * penalty_score * time_discount
```

Categorical grades:

- `monitor`: 0–24
- `prep_stage_1`: 25–49
- `prep_stage_2`: 50–69
- `committed_prep_candidate`: 70–84
- `human_decision_required`: 85–100 or any critical reputation/privilege signal

This score is decision support only. It does not claim a breakthrough occurred,
does not authorize production change, and does not override RYG authority.

## Prep policy

A high score does not authorize production change.
It can authorize staged local preparation:

- watchlist;
- seed docs;
- synthetic eval design;
- interface design;
- reversible prototype;
- scenario simulation.

Human approval remains required for authority changes.
