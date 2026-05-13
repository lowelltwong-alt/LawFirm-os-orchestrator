# SPDX-License-Identifier: MIT
"""Local-only Monte Carlo reference implementation.

Version: compute-intelligence-seed-v2
Provenance: lawfirm_os_compute_intelligence_codex_seed_pack v2.

Uses only Python standard library. No network, no model calls, no writes.
Simulation outputs are decision support only and MUST NOT grant authority.
"""
from __future__ import annotations

import random
import secrets
from dataclasses import dataclass
from statistics import mean, quantiles
from typing import Literal

__all__ = ["Authority", "Triangular", "Scenario", "simulate"]

Authority = Literal["decision_support", "advisory", "proposal"]
AUTHORITY: Authority = "decision_support"
MIN_ITERATIONS_FOR_TAILS = 10_000


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


@dataclass(frozen=True)
class Triangular:
    """Triangular distribution for normalized scenario variables.

    For probability variables, the draw represents a parameter sample. The seed
    simulator uses the distribution mode as the Bernoulli probability by default
    and reports low/mode/high sensitivity separately in future PR10 work.
    """

    low: float
    mode: float
    high: float

    def sample(self, rng: random.Random) -> float:
        return rng.triangular(self.low, self.high, self.mode)

    def point(self) -> float:
        return self.mode


@dataclass(frozen=True)
class Scenario:
    probability_breakthrough: Triangular
    future_token_cost_decline: Triangular
    future_model_capability_gain: Triangular
    competitor_adoption_probability: Triangular
    first_mover_advantage: Triangular
    prep_cost_tokens: Triangular
    prep_cost_attention: Triangular
    fallback_reuse_value: Triangular
    downside_risk: Triangular
    reputation_tail_risk: Triangular
    detection_lag: Triangular
    time_horizon_days: int = 90
    token_budget_reference: float = 10_000_000.0
    authority: Authority = AUTHORITY


def _quantile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("values must not be empty")
    idx = min(len(values) - 1, max(0, round(q * (len(values) - 1))))
    return values[idx]


def _bootstrap_ci(values: list[float], rng: random.Random, samples: int = 200) -> dict[str, float]:
    if len(values) < 2:
        return {"mean_ci_low": values[0], "mean_ci_high": values[0]}
    means = []
    n = len(values)
    for _ in range(samples):
        means.append(mean(values[rng.randrange(n)] for _ in range(n)))
    means.sort()
    return {"mean_ci_low": _quantile(means, 0.025), "mean_ci_high": _quantile(means, 0.975)}


def simulate(s: Scenario, iterations: int = MIN_ITERATIONS_FOR_TAILS, random_seed: int | None = None) -> dict:
    """Simulate a normalized scenario value.

    Value units are normalized utility points relative to a documented budget
    reference. Every spec'd variable is consumed. Reputation tail risk is a first-
    class penalty, not a side input.
    """
    if iterations < MIN_ITERATIONS_FOR_TAILS:
        raise ValueError(f"iterations must be >= {MIN_ITERATIONS_FOR_TAILS} for tail-risk estimates")
    seed = secrets.randbits(32) if random_seed is None else int(random_seed)
    rng = random.Random(seed)
    values: list[float] = []

    for _ in range(iterations):
        # Use mode as point estimate for breakthrough probability to avoid double-stochastic inflation.
        breakthrough = rng.random() < _clamp(s.probability_breakthrough.point())
        first_mover = _clamp(s.first_mover_advantage.sample(rng))
        fallback = _clamp(s.fallback_reuse_value.sample(rng))
        competitor = _clamp(s.competitor_adoption_probability.sample(rng))
        cost_decline = _clamp(s.future_token_cost_decline.sample(rng))
        capability_gain = max(0.0, s.future_model_capability_gain.sample(rng))
        prep_tokens = max(0.0, s.prep_cost_tokens.sample(rng))
        prep_attention = _clamp(s.prep_cost_attention.sample(rng))
        downside = _clamp(s.downside_risk.sample(rng))
        reputation_tail = _clamp(s.reputation_tail_risk.sample(rng))
        detection_lag = _clamp(s.detection_lag.sample(rng))

        time_discount = pow(2.718281828, -max(1, s.time_horizon_days) / 180.0)
        token_cost_utility = (prep_tokens / max(1.0, s.token_budget_reference)) * (1.0 - 0.5 * cost_decline)
        attention_cost_utility = 0.35 * prep_attention
        capability_bonus = 0.25 * _clamp(capability_gain / 2.0)

        first_mover_value = (1.0 if breakthrough else 0.0) * (first_mover * (1.0 + capability_bonus))
        competitor_pressure = competitor * (0.30 if breakthrough else 0.10)
        fallback_value = fallback * (0.55 if not breakthrough else 0.30)
        downside_penalty = 0.55 * downside + 0.95 * reputation_tail + 0.25 * detection_lag

        value = (first_mover_value + competitor_pressure + fallback_value) * time_discount
        value -= token_cost_utility + attention_cost_utility + downside_penalty
        values.append(value)

    values.sort()
    qs = quantiles(values, n=20)
    ci_rng = random.Random(seed + 1)
    ci = _bootstrap_ci(values, ci_rng)
    return {
        "authority": AUTHORITY,
        "iterations": iterations,
        "random_seed": seed,
        "simulator_version": "compute-intelligence-seed-v2",
        "mean_value": mean(values),
        "mean_ci_low": ci["mean_ci_low"],
        "mean_ci_high": ci["mean_ci_high"],
        "p05": qs[0],
        "p50": qs[9],
        "p95": qs[-1],
        "probability_positive": sum(1 for v in values if v > 0) / len(values),
        "authority_note": "simulation_is_decision_support_only",
        "unit_note": "normalized_utility_points_relative_to_token_budget_reference",
        "consumed_variables": [
            "probability_breakthrough",
            "future_token_cost_decline",
            "future_model_capability_gain",
            "competitor_adoption_probability",
            "first_mover_advantage",
            "prep_cost_tokens",
            "prep_cost_attention",
            "fallback_reuse_value",
            "downside_risk",
            "reputation_tail_risk",
            "detection_lag",
            "time_horizon_days",
        ],
    }
