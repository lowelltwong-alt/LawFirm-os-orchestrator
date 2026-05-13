# PR11 Seed — Self-Learning Compute Optimizer

## Status

Seed only. Not implemented.

## Purpose

Use append-only evidence from Exception Lake to recommend better token/compute allocation over time.

## Learning inputs

- token-spend records
- run outcomes
- validation failures
- reviewer edits
- high-confidence errors
- rollback records
- Research Radar signal outcomes
- scenario predictions and realized outcomes
- cache hit rate
- latency
- cost

## Future algorithms

- contextual bandit for budget allocation recommendations
- Bayesian update for scenario probabilities
- regret tracking for model/harness choices
- cache/reuse value estimator
- stop-loss detector for noisy expensive runs

## Future CLI idea

```bash
python -m lawfirm_os_orchestrator recommend-compute-allocation --evidence PATH --out PATH --stdout json
```

## Prohibitions

The optimizer may not:

- self-modify;
- mutate canon;
- restore green;
- execute external actions;
- call models/network;
- push code.

It produces recommendations only.
