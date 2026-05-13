# Issues Found And Likely Fixes — v2 Patched

## Status

This v2 seed pack incorporates Claude Code's read-only review feedback. The pack
is now suitable for Codex seed-only execution, subject to the same no-live-
automation and no-authority-change boundaries.

## Critical issues fixed before seeding

| Issue | Risk | v2 fix |
|---|---|---|
| Token shadow price multiplier explosion | Multiplicative factors created arbitrary 64x+ blowups | Replaced raw product with weighted log-space aggregation and documented ceiling. |
| Epsilon divisor blowups | Missing cache/cost values could create 1e9 spikes | Replaced epsilon with meaningful floor and value rejection. |
| Unit-dependent RAFVPT thresholds | ROI grades depended on unnormalized units | Schemas and algorithms now require normalized reference-run utility or documented units; percentile grading is supported for future evidence. |
| Monte Carlo non-reproducibility | Same scenario produced different evidence | Added `random_seed`, local RNG, simulator version, and recorded seed. |
| Monte Carlo unused variables | Reputation tail risk and other variables were silently ignored | Simulator consumes all spec'd variables and returns consumed variable list. |
| Mixed units in Monte Carlo | Tokens were subtracted from utility using magic constants | Prep tokens are converted to normalized utility against a documented budget reference; attention cost is normalized. |
| Double-stochastic breakthrough probability | Nested probability sampling inflated variance | Uses probability mode as point estimate; future sensitivity/Beta model is documented. |
| Too-small Monte Carlo tail sample | N=1000 was weak for p05/p95 tail risk | Default/minimum is now 10,000, with bootstrap CI for mean. |
| Game-state cliff edges | Single if/else label collapsed multi-game states | Classifier returns continuous game-state score vector plus dominant state. |
| Breakthrough readiness formula defects | Product/division formula was unbounded and unit-sensitive | Replaced docs with normalized weighted geometric mean + time discount + 0–100 grade bands. |

## High-priority issues fixed or contained

| Issue | v2 fix |
|---|---|
| Loose schemas | Schemas now use `additionalProperties: false` and enumerate key shapes. |
| Validation failed open | Master prompt and validation doc now say missing scripts or non-zero exit stops commit. |
| Optimizer sample-size blindness | Reference optimizer now tracks sample size, Wilson interval, policy regime, and uses proposal-for-human-review actions. |
| Personal path in prompts | Future seed docs refer to repo-relative paths where possible; local paths are not required inside committed seeds. |
| No provenance/version | Reference algorithms include SPDX, version, provenance, `__all__`, and authority fields. |
| Doctrine not code-enforced | Outputs now include `authority` and proposal/decision-support notes; no output is executive authority. |
| No safety script | Added `scripts/check_seed_pack_safety.py` and copy under `docs/phase2-seeds/scripts/`. |

## Medium issues deliberately deferred to implementation PRs

- Correlated scenario variables should use a correlation matrix or copula in PR10.
- Optimizer needs causal attribution before it can make strong recommendations in PR11.
- Portfolio allocation should be projected onto a budget simplex in PR09/PR11.
- ROI and game thresholds must be calibrated against Exception Lake evidence after enough records exist.
- Outcome records should support time decay / half-life in PR11.

## Legal-domain considerations preserved as non-negotiables

- Reputational tail risk is first-class and must dominate speed when high.
- First-mover race is not the default prior for legal AI; option portfolio and waiting games should be default unless evidence is strong.
- Privilege class is explicit in the frontier radar schema.
- Optimizer actions use `propose_*_for_human_review` vocabulary.
- PR09–PR12 should include kill switches/fail-closed modes before implementation.
- Exception Lake evidence must include `policy_regime_id` before learning recommendations are trusted.

## Likely future fixes

1. Add real Exception Lake outcome records before activating PR11.
2. Add calibrated score thresholds after at least 30 comparable evidence records per bucket.
3. Add correlation/sensitivity modeling for PR10.
4. Add `KILL_SWITCH.md` or equivalent per implemented compute module.
5. Add release gates that reject any live automation imports or authority-elevating output.
