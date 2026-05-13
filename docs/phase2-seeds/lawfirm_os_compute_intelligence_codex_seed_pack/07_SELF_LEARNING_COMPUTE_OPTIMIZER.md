# Self-Learning Compute Optimizer

## Purpose

The self-learning compute optimizer recommends better allocation of tokens/compute over time based on realized outcomes.

It must learn from append-only evidence, not from untracked intuition.

## Inputs

- token-spend records;
- run outcomes;
- eval outcomes;
- reviewer edits;
- validation failures;
- latency and cache hit rates;
- Research Radar predictions;
- scenario outcomes;
- rollback and incident records.

## Outputs

- model budget recommendation;
- cache recommendation;
- compression recommendation;
- harness-depth recommendation;
- red-team allocation recommendation;
- exploration budget recommendation;
- Research Radar budget recommendation;
- future-option prep recommendation.

## Prohibited outputs

The optimizer may not:

- modify policy;
- mutate canon;
- restore green authority;
- call external tools;
- push code;
- run live research;
- schedule jobs;
- make external writes.

It produces proposals only.


## Proposal vocabulary

Optimizer outputs must use proposal verbs, for example:

- `propose_increase_for_human_review`
- `propose_decrease_or_redesign_for_human_review`
- `propose_reduce_or_add_validation_for_human_review`
- `propose_hold_for_human_review`

Avoid ambiguous verbs such as `increase`, `decrease`, or `apply`. The optimizer
must not self-modify, alter budgets automatically, restore green, or change
policy.

## Evidence requirements

Future implementation should reject cross-regime evidence unless a matching
`policy_regime_id` is present. It should track sample size, confidence/credible
intervals, and risk budgets before recommending any allocation shift.
