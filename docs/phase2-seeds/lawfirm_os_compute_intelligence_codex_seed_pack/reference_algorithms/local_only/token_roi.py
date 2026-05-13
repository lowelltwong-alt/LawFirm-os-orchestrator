# SPDX-License-Identifier: MIT
"""Local-only reference algorithms for LawFirm OS compute ROI.

Version: compute-intelligence-seed-v2
Provenance: lawfirm_os_compute_intelligence_codex_seed_pack v2.

This module is documentation/reference code only. It performs no network calls,
no model calls, no filesystem writes, and grants no authority. All outputs are
proposal/decision-support artifacts and MUST NOT override RYG authority.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal, Mapping

__all__ = [
    "Authority",
    "EffectiveComputeCostInput",
    "TokenShadowPriceInput",
    "ValueComponents",
    "ComputeRoiResult",
    "clamp",
    "effective_compute_cost",
    "token_shadow_price",
    "risk_adjusted_future_value_per_token",
    "compute_roi_grade",
    "compute_roi_result",
]

Authority = Literal["decision_support", "advisory", "proposal"]
AUTHORITY: Authority = "decision_support"
MEANINGFUL_FLOOR = 0.1
DEFAULT_MULTIPLIER_CEILING = 8.0


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Clamp a value to a closed interval."""
    return max(low, min(high, value))


def _require_non_negative(name: str, value: float) -> float:
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
    return value


def _require_multiplier(name: str, value: float) -> float:
    if value < MEANINGFUL_FLOOR:
        raise ValueError(f"{name} must be >= {MEANINGFUL_FLOOR}; reject missing/invalid inputs instead of using epsilon")
    return value


@dataclass(frozen=True)
class EffectiveComputeCostInput:
    """Cost components in a documented common unit.

    For PR09 seeds, the recommended common unit is normalized utility/cost points
    relative to a reference run. Production implementations may convert this to
    dollars, but should preserve the same-unit invariant.
    """

    dollar_cost: float = 0.0
    latency_cost: float = 0.0
    human_review_cost: float = 0.0
    context_pollution_cost: float = 0.0
    opportunity_cost: float = 0.0
    risk_cost: float = 0.0
    cache_reuse_credit: float = 0.0
    learning_credit: float = 0.0
    future_option_credit: float = 0.0
    authority: Authority = AUTHORITY


@dataclass(frozen=True)
class TokenShadowPriceInput:
    """Token shadow price parameters.

    Multipliers are interpreted as relative pressure factors. Weighted log-space
    aggregation prevents the 6-way multiplier explosion that a raw product causes.
    Weights sum to 1.0 by default.
    """

    dollar_price: float
    scarcity_multiplier: float = 1.0
    latency_multiplier: float = 1.0
    context_window_multiplier: float = 1.0
    risk_multiplier: float = 1.0
    stakes_multiplier: float = 1.0
    opportunity_cost_multiplier: float = 1.0
    cache_reuse_multiplier: float = 1.0
    ceiling_multiplier: float = DEFAULT_MULTIPLIER_CEILING
    authority: Authority = AUTHORITY


@dataclass(frozen=True)
class ValueComponents:
    """Normalized 0..1 value components relative to a reference run.

    The normalized contract avoids fixed ROI thresholds over unit-dependent raw
    dollars/utility values. Rolling percentile grading is still preferred after
    enough Exception Lake evidence exists.
    """

    present_value: float = 0.0
    future_option_value: float = 0.0
    strategic_position_value: float = 0.0
    learning_value: float = 0.0
    reputation_protection_value: float = 0.0
    confidence: float = 0.5
    authority: Authority = AUTHORITY


@dataclass(frozen=True)
class ComputeRoiResult:
    authority: Authority
    normalized_value: float
    normalized_effective_cost: float
    rafvpt: float
    grade: str
    note: str


def effective_compute_cost(x: EffectiveComputeCostInput) -> float:
    components = [
        _require_non_negative("dollar_cost", x.dollar_cost),
        _require_non_negative("latency_cost", x.latency_cost),
        _require_non_negative("human_review_cost", x.human_review_cost),
        _require_non_negative("context_pollution_cost", x.context_pollution_cost),
        _require_non_negative("opportunity_cost", x.opportunity_cost),
        _require_non_negative("risk_cost", x.risk_cost),
    ]
    credits = [
        _require_non_negative("cache_reuse_credit", x.cache_reuse_credit),
        _require_non_negative("learning_credit", x.learning_credit),
        _require_non_negative("future_option_credit", x.future_option_credit),
    ]
    return max(MEANINGFUL_FLOOR, sum(components) - sum(credits))


def token_shadow_price(x: TokenShadowPriceInput | float, **kwargs: float) -> float:
    """Compute a bounded token shadow price using weighted log-space multipliers.

    Backward-compatible call style is supported:
        token_shadow_price(1.0, risk_multiplier=2.0, ...)
    """
    if not isinstance(x, TokenShadowPriceInput):
        x = TokenShadowPriceInput(dollar_price=float(x), **kwargs)

    base = _require_non_negative("dollar_price", x.dollar_price)
    if base == 0:
        return 0.0

    factors = {
        "scarcity_multiplier": _require_multiplier("scarcity_multiplier", x.scarcity_multiplier),
        "latency_multiplier": _require_multiplier("latency_multiplier", x.latency_multiplier),
        "context_window_multiplier": _require_multiplier("context_window_multiplier", x.context_window_multiplier),
        "risk_multiplier": _require_multiplier("risk_multiplier", x.risk_multiplier),
        "stakes_multiplier": _require_multiplier("stakes_multiplier", x.stakes_multiplier),
        "opportunity_cost_multiplier": _require_multiplier("opportunity_cost_multiplier", x.opportunity_cost_multiplier),
    }
    # Weights sum to 1.0 so the result is a proper weighted geometric mean.
    # If you rebalance, keep sum(weights) == 1.0 or document the intentional
    # deviation explicitly.
    weights = {
        "scarcity_multiplier": 0.15,
        "latency_multiplier": 0.15,
        "context_window_multiplier": 0.15,
        "risk_multiplier": 0.20,
        "stakes_multiplier": 0.20,
        "opportunity_cost_multiplier": 0.15,
    }
    assert abs(sum(weights.values()) - 1.0) < 1e-9, "shadow-price weights must sum to 1.0"
    log_pressure = sum(weights[name] * math.log(value) for name, value in factors.items())
    log_cache_credit = math.log(_require_multiplier("cache_reuse_multiplier", x.cache_reuse_multiplier))
    multiplier = math.exp(log_pressure - log_cache_credit)
    multiplier = min(multiplier, _require_multiplier("ceiling_multiplier", x.ceiling_multiplier))
    return base * multiplier


def _value_sum(values: ValueComponents | Mapping[str, float]) -> tuple[float, float]:
    if isinstance(values, ValueComponents):
        components = [
            values.present_value,
            values.future_option_value,
            values.strategic_position_value,
            values.learning_value,
            values.reputation_protection_value,
        ]
        confidence = values.confidence
    else:
        components = [
            float(values.get("present_value", 0.0)),
            float(values.get("future_option_value", 0.0)),
            float(values.get("strategic_position_value", 0.0)),
            float(values.get("learning_value", 0.0)),
            float(values.get("reputation_protection_value", 0.0)),
        ]
        confidence = float(values.get("confidence", 0.5))
    normalized_components = [clamp(c) for c in components]
    return clamp(sum(normalized_components) / len(normalized_components)), clamp(confidence)


def risk_adjusted_future_value_per_token(values: ValueComponents | Mapping[str, float], normalized_effective_cost: float) -> float:
    """Return normalized value per normalized cost.

    Inputs must be in normalized reference-run units. Use rolling-percentile grades
    once enough Exception Lake evidence records exist.
    """
    value, confidence = _value_sum(values)
    cost = _require_multiplier("normalized_effective_cost", normalized_effective_cost)
    return clamp((value * confidence) / cost, 0.0, 2.0)


def compute_roi_grade(rafvpt: float, stakes: str = "medium", risk_color: str = "yellow", percentile_rank: float | None = None) -> str:
    """Grade ROI without granting authority.

    If percentile_rank is supplied, it must be 0..1 against a rolling distribution
    from comparable evidence. Otherwise use conservative seed thresholds over a
    normalized RAFVPT score.
    """
    if risk_color == "red" or stakes in {"critical", "existential"}:
        return "R1"
    score = clamp(percentile_rank) if percentile_rank is not None else clamp(rafvpt / 2.0)
    if score >= 0.80:
        return "A1"
    if score >= 0.60:
        return "B1"
    if score >= 0.40:
        return "C1"
    return "D1"


def compute_roi_result(values: ValueComponents | Mapping[str, float], normalized_effective_cost: float, *, stakes: str = "medium", risk_color: str = "yellow") -> ComputeRoiResult:
    value, confidence = _value_sum(values)
    rafvpt = risk_adjusted_future_value_per_token(values, normalized_effective_cost)
    return ComputeRoiResult(
        authority=AUTHORITY,
        normalized_value=value * confidence,
        normalized_effective_cost=normalized_effective_cost,
        rafvpt=rafvpt,
        grade=compute_roi_grade(rafvpt, stakes=stakes, risk_color=risk_color),
        note="compute_roi_is_decision_support_only_and_must_not_override_ryg_authority",
    )
