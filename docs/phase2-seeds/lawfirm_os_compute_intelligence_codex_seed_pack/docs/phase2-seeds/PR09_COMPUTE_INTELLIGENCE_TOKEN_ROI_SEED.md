# PR09 Seed — Compute Intelligence / Token ROI / Strategic Compute Allocation

## Status

Seed only. Not implemented.

## Purpose

Create a compute intelligence layer that allocates token/compute budgets by value, not by cheapness alone.

## Core rule

```text
Token budgets are not only dollar budgets.
Compute allocation must consider dollars, latency, context-window scarcity, human review burden, risk exposure, stakes, opportunity cost, cache/reuse value, learning value, and future-option value.
```

## Required future objects

- `compute-allocation-policy`
- `token-spend-record`
- `compute-roi-record`
- `effective-compute-cost-record`
- `token-shadow-price-record`
- `future-option-value-record`
- `allocation-recommendation-record`

## Allocation buckets

```json
{
  "production_reliability": 0.35,
  "validation_and_red_team": 0.20,
  "learning_loop": 0.15,
  "research_radar": 0.10,
  "future_option_prep": 0.10,
  "exploration": 0.05,
  "reputation_protection_reserve": 0.05
}
```

These are defaults, not hard rules.
Risk/stakes can shift budget direction but cannot override authority.

## Compute ROI grades

- `A1`: high RAFVPT (top band).
- `B1`: solid RAFVPT (upper-middle band).
- `C1`: marginal RAFVPT (lower-middle band).
- `D1`: weak RAFVPT (bottom band).
- `R1`: high stakes or red risk color; ROI alone insufficient; authority gate required.

A separate two-axis grade for "high future-option value despite high compute"
(previously labelled `A2`) is **deferred** until PR11 calibration adds a stable
future-option signal to Exception Lake outcome records. Until then, future-
option-heavy proposals are flagged through the `value_components` shape, not
through a distinct grade.

## Future CLI idea

```bash
python -m lawfirm_os_orchestrator score-compute-roi --run PATH --context PATH --out PATH --stdout json
```

## Prohibitions

Compute ROI may recommend. It may not authorize.
