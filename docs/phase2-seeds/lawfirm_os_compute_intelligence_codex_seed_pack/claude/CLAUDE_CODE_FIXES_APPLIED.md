# Claude Code Fixes Applied — Compute Intelligence Seed Pack v2

This file records the controlled fix pass applied to the v2 pack after the Claude Code math review.

## Scope authorized by user

- Apply fixes M-1 through M-4 (hard math defects).
- Apply fixes S-1 through S-4 (schema/code asymmetries).
- Defer observational items O-1 through O-4 to a later pass.
- Place corrected pack in `LawFirm-os-orchestrator/docs/phase2-seeds/lawfirm_os_compute_intelligence_codex_seed_pack/` on a feature branch.
- Commit locally; do not push.

## Hard math fixes

### M-1. `token_shadow_price` weight sum corrected to 1.0
**File:** `reference_algorithms/local_only/token_roi.py`

**Before:** weights summed to 0.95 (opportunity_cost_multiplier=0.10), causing a 3.41% systematic under-expression of the multiplier when all six factors equalled 2.0 (`1.9319x` instead of `2.0x`).

**After:** opportunity_cost_multiplier raised to 0.15 so weights sum to 1.0. Added a runtime `assert` enforcing the invariant.

```python
weights = {
    "scarcity_multiplier": 0.15,
    "latency_multiplier": 0.15,
    "context_window_multiplier": 0.15,
    "risk_multiplier": 0.20,
    "stakes_multiplier": 0.20,
    "opportunity_cost_multiplier": 0.15,   # was 0.10
}
assert abs(sum(weights.values()) - 1.0) < 1e-9
```

### M-2. `token_roi_example.json` rafvpt rounded correctly
**File:** `examples/token_roi_example.json`

`rafvpt: 0.87` → `rafvpt: 0.88`. The correct value is `clamp((0.57 × 0.65) / 0.42, 0, 2) = 0.8821…`, which rounds to `0.88` at two decimals.

### M-3. Orphaned `A2` grade removed from PR09 doc
**File:** `docs/phase2-seeds/PR09_COMPUTE_INTELLIGENCE_TOKEN_ROI_SEED.md`

`compute_roi_grade()` returns A1/B1/C1/D1/R1 — there is no path that produces A2. Doc previously listed A2 as a distinct grade. Doc now lists only the five grades the algorithm actually produces and explicitly defers the two-axis grade ("high future-option value despite high compute") until PR11 calibration provides a stable future-option signal.

### M-4. `token_budget_reference` now expressible in scenario JSON
**File:** `schemas/scenario-simulation-request.schema.json`

The simulator divides `prep_cost_tokens` by `Scenario.token_budget_reference` (default `10_000_000`) but the schema's `additionalProperties: false` previously prevented a JSON request from overriding this normalization constant. Added a top-level `token_budget_reference` field (`exclusiveMinimum: 0`, `default: 10000000`) so the request can express an explicit firm-scale token budget. Loaders translating request JSON to a `Scenario` instance should now pass this through.

## Schema/code asymmetry fixes

### S-1. `value_unit` constrained to the only supported unit for v2
**File:** `schemas/token-roi-record.schema.json`

Previously `value_unit` was an enum allowing `normalized_reference_run_utility | dollars | other_documented_unit`, but the algorithm only handles normalized [0,1] inputs. A record declaring `value_unit: dollars` with dollar-denominated components would validate but yield meaningless RAFVPT. Tightened to `const: "normalized_reference_run_utility"` for v2 with mixed-unit support deferred to PR11.

### S-2. `effective_compute_cost` schema minimum aligned to algorithm floor
**File:** `schemas/token-roi-record.schema.json`

Algorithm returns `max(MEANINGFUL_FLOOR=0.1, …)` so values in `[0, 0.0999]` are unreachable. Schema `minimum` raised from `0` to `0.1`.

### S-3. `rafvpt` schema maximum aligned to algorithm clamp
**File:** `schemas/token-roi-record.schema.json`

Algorithm clamps to `[0, 2.0]`. Added `maximum: 2.0` to the schema so records with `rafvpt > 2.0` are rejected at the boundary instead of silently accepted as malformed.

### S-4. Added reference algorithm for PR12 Frontier Readiness
**File:** `reference_algorithms/local_only/frontier_readiness.py` (new, ~150 lines)

PR12 previously documented a `readiness_score_0_to_100 = 100 * benefit_score * penalty_score * time_discount` formula in `docs/phase2-seeds/PR12_FRONTIER_MATH_ALGORITHM_RADAR_SEED.md` and `05_FRONTIER_MATH_RADAR.md`, but shipped no Python reference (unlike PR09/PR10/PR11). Added a small `frontier_readiness.py` matching the documented formula:

- benefit weighted geometric mean over (`relevance_to_os`, `probability_of_arrival`, `first_mover_advantage`, `prep_reuse_value`, `integration_speed_advantage`) with weights summing to 1.0
- penalty weighted geometric mean over (`1 − normalized_prep_cost`, `1 − uncertainty_level`, `1 − downside_risk`, `1 − reputation_tail_risk`) with weights summing to 1.0; reputation tail risk weighted highest (`0.35`) per the legal-domain prior
- `time_discount = math.exp(-time_horizon_days / 180)`
- `MEANINGFUL_FLOOR = 0.01` to avoid `log(0)`
- Grade bands match the doc (`monitor | prep_stage_1 | prep_stage_2 | committed_prep_candidate | human_decision_required`)
- `critical_privilege_or_reputation_signal=True` short-circuits to `human_decision_required` regardless of score
- Outputs are decision support only; no authority grants

The radar-item schema (`schemas/frontier-math-radar-item.schema.json`) was deliberately left unchanged. It carries radar metadata, not scoring inputs. A future PR can add a separate `frontier-readiness-request.schema.json` if needed; for v2 seed scope the algorithm interface is sufficient.

## Deferred items (not in this pass)

| Item | Reason for deferral |
|---|---|
| O-1: `pow(2.718281828, x)` → `math.exp(x)` in monte_carlo_scenario.py | ~10⁻⁹ precision delta only; cosmetic. |
| O-2: Bootstrap CI default 200 → 1000 samples | Stable enough at 200 for current synthetic use; expose as parameter in a later PR. |
| O-3: Define `RAFVPT_CEILING = 2.0` module constant in token_roi.py | Schema already documents the bound; coupling is visible. |
| O-4: `_bootstrap_ci` empty-list defensive guard | Pre-condition `iterations >= 10000` prevents reaching this branch. |

## Verifications run

- `python scripts/check_seed_pack_safety.py .` — passes (no forbidden live-automation patterns introduced by the fixes).
- Math verification of `token_shadow_price`: with all-2x multipliers, post-fix result is `2.0000` (within `1e-9`), up from `1.9319` pre-fix.
- Math verification of example: post-fix `rafvpt = 0.88` matches algorithm output rounded to 2dp.
- Weight invariants asserted in code: `token_roi.py` and `frontier_readiness.py` both `assert sum(weights) == 1.0`.

## Provenance

- Source pack: `lawfirm_os_compute_intelligence_codex_seed_pack v2` (delivered as `lawfirm_os_compute_intelligence_codex_seed_pack_v2 (1).zip`).
- Fix pass author: Claude Code, under user-authorized scope `1(b) + 2(b)` (place into orchestrator on feature branch, fix M-1..M-4 and S-1..S-4).
- Pack `seed_pack_version: v2-patched` in `compute-intelligence-seed-index.json` was already set by ChatGPT v2; this Claude-Code pass adds these corrections on top.
