# SPDX-License-Identifier: MIT
"""Local-only reference game-state classifier for scenario planning.

Version: compute-intelligence-seed-v2
Provenance: lawfirm_os_compute_intelligence_codex_seed_pack v2.

Returns continuous game-state scores plus a dominant state. This avoids cliff-edge
single-label collapse. Outputs are decision support only.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

__all__ = ["Authority", "GameState", "GameInputs", "classify_game_state"]

Authority = Literal["decision_support", "advisory", "proposal"]
AUTHORITY: Authority = "decision_support"

GameState = Literal[
    "first_mover_race",
    "waiting_game",
    "coordination_game",
    "arms_race",
    "reputation_ruin_game",
    "adversarial_game",
    "option_portfolio_game",
]


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _sigmoid(value: float, center: float, width: float = 0.10) -> float:
    return 1.0 / (1.0 + math.exp(-(value - center) / width))


@dataclass(frozen=True)
class GameInputs:
    first_mover_advantage: float
    cost_decline_expected: float
    competitor_adoption_probability: float
    reputation_tail_risk: float
    adversarial_pressure: float
    standards_dependency: float
    fallback_reuse_value: float
    authority: Authority = AUTHORITY


def classify_game_state(x: GameInputs) -> dict:
    """Return score vector and dominant game state.

    Legal-domain prior: waiting/option-portfolio postures are favored unless
    first-mover advantage is unusually strong and reputation/privilege tail risk
    is low enough to justify speed. First-mover race is never an authority grant.
    """
    fm = _clamp(x.first_mover_advantage)
    cost = _clamp(x.cost_decline_expected)
    comp = _clamp(x.competitor_adoption_probability)
    rep = _clamp(x.reputation_tail_risk)
    adv = _clamp(x.adversarial_pressure)
    std = _clamp(x.standards_dependency)
    reuse = _clamp(x.fallback_reuse_value)

    scores: dict[GameState, float] = {
        "reputation_ruin_game": _sigmoid(rep, 0.62, 0.08),
        "adversarial_game": _sigmoid(adv, 0.65, 0.10),
        "coordination_game": _sigmoid(std, 0.65, 0.10),
        "first_mover_race": _clamp(_sigmoid(fm, 0.82, 0.08) * _sigmoid(comp, 0.65, 0.10) * (1.0 - rep)),
        "arms_race": _clamp(_sigmoid(comp, 0.78, 0.08) * _sigmoid(fm, 0.55, 0.12) * (1.0 - 0.5 * rep)),
        "waiting_game": _clamp(_sigmoid(cost, 0.60, 0.12) * (1.0 - fm) * (1.0 - adv)),
        "option_portfolio_game": _clamp(0.35 + 0.35 * reuse + 0.20 * cost + 0.10 * (1.0 - rep)),
    }
    dominant_state = max(scores.items(), key=lambda item: item[1])[0]
    recommended_posture = {
        "reputation_ruin_game": "prioritize_validation_and_reputation_protection_for_human_review",
        "adversarial_game": "prioritize_red_team_and_security_review",
        "coordination_game": "monitor_standards_and_prepare_compatible_options",
        "first_mover_race": "stage_reversible_readiness_only_until_human_approval",
        "arms_race": "avoid_speed_only_race_preserve_evidence_and_guardrails",
        "waiting_game": "monitor_and_wait_while_preserving_option_value",
        "option_portfolio_game": "stage_low_cost_reusable_options",
    }[dominant_state]
    return {
        "authority": AUTHORITY,
        "dominant_state": dominant_state,
        "scores": scores,
        "recommended_posture": recommended_posture,
        "authority_note": "game_state_is_decision_support_only_and_does_not_grant_authority",
        "calibration_note": "thresholds_are_seed_defaults_pending_exception_lake_evidence_calibration",
    }
