# SPDX-License-Identifier: MIT
"""Local-only reference scorer for frontier-math / algorithmic breakthrough readiness.

Version: compute-intelligence-seed-v2
Provenance: lawfirm_os_compute_intelligence_codex_seed_pack v2.

Implements the documented seed formula in docs/phase2-seeds/PR12_FRONTIER_MATH_ALGORITHM_RADAR_SEED.md
and 05_FRONTIER_MATH_RADAR.md:

    benefit_score = weighted_geometric_mean(
        relevance_to_os, probability_of_arrival, first_mover_advantage,
        prep_reuse_value, integration_speed_advantage)
    penalty_score = weighted_geometric_mean(
        1 - normalized_prep_cost, 1 - uncertainty_level,
        1 - downside_risk, 1 - reputation_tail_risk)
    time_discount = exp(-time_horizon_days / 180)
    readiness_score_0_to_100 = 100 * benefit_score * penalty_score * time_discount

No network calls, no model calls, no filesystem writes. Outputs are decision
support only and MUST NOT override RYG authority.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

__all__ = [
    "Authority",
    "BenefitInputs",
    "PenaltyInputs",
    "FrontierReadinessResult",
    "BENEFIT_WEIGHTS",
    "PENALTY_WEIGHTS",
    "score_frontier_readiness",
]

Authority = Literal["decision_support", "advisory", "proposal"]
AUTHORITY: Authority = "decision_support"
MEANINGFUL_FLOOR = 0.01
TIME_DISCOUNT_HALFLIFE_DAYS = 180.0

# Benefit weights sum to 1.0. Relevance and probability of arrival dominate
# because they gate whether a breakthrough matters at all; speed/reuse are
# secondary. Adjust only with documented rationale.
BENEFIT_WEIGHTS = {
    "relevance_to_os": 0.30,
    "probability_of_arrival": 0.25,
    "first_mover_advantage": 0.15,
    "prep_reuse_value": 0.15,
    "integration_speed_advantage": 0.15,
}

# Penalty weights sum to 1.0. Reputation tail risk dominates per the legal-
# domain prior (also reflected in monte_carlo_scenario.py downside weighting).
PENALTY_WEIGHTS = {
    "inv_normalized_prep_cost": 0.20,
    "inv_uncertainty_level": 0.25,
    "inv_downside_risk": 0.20,
    "inv_reputation_tail_risk": 0.35,
}

assert abs(sum(BENEFIT_WEIGHTS.values()) - 1.0) < 1e-9, "benefit weights must sum to 1.0"
assert abs(sum(PENALTY_WEIGHTS.values()) - 1.0) < 1e-9, "penalty weights must sum to 1.0"


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _require_unit_interval(name: str, value: float) -> float:
    if value < 0.0 or value > 1.0:
        raise ValueError(f"{name} must be in [0, 1]; got {value}")
    return value


def _weighted_geometric_mean(values: dict[str, float], weights: dict[str, float]) -> float:
    """Return exp(sum(w_i * log(max(v_i, MEANINGFUL_FLOOR)))).

    Floors each input at MEANINGFUL_FLOOR (0.01) to avoid log(0) = -inf. A truly
    zero input means "this dimension blocks readiness" and is represented as
    near-zero (0.01) rather than -infinity.
    """
    if values.keys() != weights.keys():
        raise ValueError(f"values keys {sorted(values)} must match weight keys {sorted(weights)}")
    log_sum = 0.0
    for name, value in values.items():
        floored = max(MEANINGFUL_FLOOR, _require_unit_interval(name, value))
        log_sum += weights[name] * math.log(floored)
    return math.exp(log_sum)


@dataclass(frozen=True)
class BenefitInputs:
    relevance_to_os: float
    probability_of_arrival: float
    first_mover_advantage: float
    prep_reuse_value: float
    integration_speed_advantage: float
    authority: Authority = AUTHORITY


@dataclass(frozen=True)
class PenaltyInputs:
    normalized_prep_cost: float
    uncertainty_level: float
    downside_risk: float
    reputation_tail_risk: float
    authority: Authority = AUTHORITY


@dataclass(frozen=True)
class FrontierReadinessResult:
    authority: Authority
    benefit_score: float
    penalty_score: float
    time_discount: float
    readiness_score_0_to_100: float
    grade: str
    note: str


def _grade(score: float, *, critical_privilege_or_reputation_signal: bool) -> str:
    if critical_privilege_or_reputation_signal:
        return "human_decision_required"
    if score >= 85:
        return "human_decision_required"
    if score >= 70:
        return "committed_prep_candidate"
    if score >= 50:
        return "prep_stage_2"
    if score >= 25:
        return "prep_stage_1"
    return "monitor"


def score_frontier_readiness(
    benefit: BenefitInputs,
    penalty: PenaltyInputs,
    time_horizon_days: int,
    *,
    critical_privilege_or_reputation_signal: bool = False,
) -> FrontierReadinessResult:
    """Compute the 0..100 frontier-readiness score.

    All inputs in `benefit` and `penalty` must be in [0, 1]. `time_horizon_days`
    must be a positive integer. The result is decision support only and never
    authorizes a production change, green restoration, or canon mutation.
    """
    if time_horizon_days < 1:
        raise ValueError("time_horizon_days must be >= 1")

    benefit_values = {
        "relevance_to_os": benefit.relevance_to_os,
        "probability_of_arrival": benefit.probability_of_arrival,
        "first_mover_advantage": benefit.first_mover_advantage,
        "prep_reuse_value": benefit.prep_reuse_value,
        "integration_speed_advantage": benefit.integration_speed_advantage,
    }
    penalty_values = {
        "inv_normalized_prep_cost": 1.0 - _require_unit_interval("normalized_prep_cost", penalty.normalized_prep_cost),
        "inv_uncertainty_level": 1.0 - _require_unit_interval("uncertainty_level", penalty.uncertainty_level),
        "inv_downside_risk": 1.0 - _require_unit_interval("downside_risk", penalty.downside_risk),
        "inv_reputation_tail_risk": 1.0 - _require_unit_interval("reputation_tail_risk", penalty.reputation_tail_risk),
    }
    benefit_score = _weighted_geometric_mean(benefit_values, BENEFIT_WEIGHTS)
    penalty_score = _weighted_geometric_mean(penalty_values, PENALTY_WEIGHTS)
    time_discount = math.exp(-time_horizon_days / TIME_DISCOUNT_HALFLIFE_DAYS)
    readiness = _clamp(100.0 * benefit_score * penalty_score * time_discount, 0.0, 100.0)
    return FrontierReadinessResult(
        authority=AUTHORITY,
        benefit_score=benefit_score,
        penalty_score=penalty_score,
        time_discount=time_discount,
        readiness_score_0_to_100=readiness,
        grade=_grade(readiness, critical_privilege_or_reputation_signal=critical_privilege_or_reputation_signal),
        note="frontier_readiness_is_decision_support_only_and_must_not_override_ryg_authority",
    )
