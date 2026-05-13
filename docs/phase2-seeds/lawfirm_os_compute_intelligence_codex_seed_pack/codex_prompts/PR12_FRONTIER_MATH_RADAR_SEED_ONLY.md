# PR12 Seed — Frontier Math / Algorithmic Breakthrough Radar

## Status

Seed only. Not implemented.

## Purpose

Prepare LawFirm OS to notice and evaluate frontier math or algorithmic breakthroughs that could materially improve retrieval, reasoning, planning, compression, verification, or optimization.

## Relevant breakthrough classes

- retrieval/ranking algorithms
- proof/citation verification methods
- search/planning algorithms
- compression/context selection
- eval reliability/statistical testing
- privacy-preserving learning
- graph reasoning
- scheduling/portfolio optimization
- formal policy verification
- probabilistic calibration

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

## Future CLI idea

```bash
python -m lawfirm_os_orchestrator score-frontier-readiness --radar-item PATH --out PATH --stdout json
```

## Prohibitions

No live radar automation.
No claiming a breakthrough is real without later external verification.
No authority changes.
No automatic green restoration.
