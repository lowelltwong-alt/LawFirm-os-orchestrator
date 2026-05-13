# Algorithm Catalog

This file lists algorithms that may be implemented later, with local-only reference versions included in this pack.

## 1. Effective compute cost

```text
effective_compute_cost =
  dollar_cost
+ latency_cost
+ human_review_cost
+ context_pollution_cost
+ opportunity_cost
+ risk_cost
- cache_reuse_credit
- learning_credit
- future_option_credit
```

## 2. Token shadow price

Use weighted log-space aggregation rather than a raw multiplier product. This
prevents 6-way multiplier explosion and avoids epsilon-divisor blowups.

```text
log_pressure = sum(weight_i * log(multiplier_i))
log_cache_credit = log(max(cache_reuse_multiplier, meaningful_floor))
token_shadow_price = dollar_price * exp(log_pressure - log_cache_credit)
```

All multipliers must be above a meaningful floor such as `0.1`; missing values
should be rejected, not hidden behind machine epsilon.

## 3. Risk-adjusted future value per token

Inputs must be normalized to a documented common unit, preferably 0..1 utility
relative to a reference run until enough Exception Lake evidence exists.

```text
rafvpt =
  normalized_value_components_mean
  * normalized_confidence
  / normalized_effective_compute_cost
```

Absolute grade thresholds are seed defaults only. Future PRs should grade against
rolling percentiles for comparable cohorts.

## 4. Staged option value

Use staged build budgets for uncertain future opportunities:

```text
Stage 0: monitor only
Stage 1: schema/eval/front-door prep
Stage 2: local prototype
Stage 3: harness + red-team + synthetic evals
Stage 4: gated production candidate
Stage 5: human-approved scale
```

## 5. Game-state classifier

Classify the strategic environment:

- first_mover_race;
- waiting_game;
- coordination_game;
- arms_race;
- reputation_ruin_game;
- adversarial_game;
- option_portfolio_game.

## 6. Monte Carlo scenario engine

Simulate distributions over:

- breakthrough probability;
- future token cost decline;
- future model capability gain;
- competitor adoption;
- first-mover advantage;
- fallback reuse value;
- downside/reputation risk;
- detection lag;
- buildout complexity.

## 7. Self-learning compute optimizer

Use append-only Exception Lake evidence to recommend:

- model selection;
- cache strategy;
- compression strategy;
- harness depth;
- red-team budget;
- research radar budget;
- future option preparation budget.

Never self-modify.
Never restore green.
Never mutate canon.
