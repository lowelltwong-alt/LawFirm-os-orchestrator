from __future__ import annotations

from typing import Any

from lawfirm_os_orchestrator.learning.models import AlgorithmInsight

FORMULA = "credibility * relevance * expected_lift * verifiability / risk / implementation_cost"


def calculate_upgrade_priority(
    *,
    credibility: float,
    relevance: float,
    expected_lift: float,
    verifiability: float,
    risk: float,
    implementation_cost: float,
) -> float:
    for name, value in {
        "credibility": credibility,
        "relevance": relevance,
        "expected_lift": expected_lift,
        "verifiability": verifiability,
    }.items():
        if value < 0.0 or value > 1.0:
            raise ValueError(f"{name} must be between 0.0 and 1.0")
    for name, value in {"risk": risk, "implementation_cost": implementation_cost}.items():
        if value <= 0.0 or value > 1.0:
            raise ValueError(f"{name} must be greater than 0.0 and at most 1.0")
    return round((credibility * relevance * expected_lift * verifiability) / risk / implementation_cost, 6)


def score_algorithm_insight(insight: AlgorithmInsight) -> dict[str, Any]:
    score = calculate_upgrade_priority(
        credibility=insight.credibility,
        relevance=insight.relevance,
        expected_lift=insight.expected_lift,
        verifiability=insight.verifiability,
        risk=insight.risk,
        implementation_cost=insight.implementation_cost,
    )
    return {
        "schema_version": "1.0",
        "algorithm_insight_id": insight.algorithm_insight_id,
        "formula": FORMULA,
        "upgrade_priority": score,
        "target_surface": insight.target_surface.value,
        "affected_metric": insight.affected_metric,
        "inputs": {
            "credibility": insight.credibility,
            "relevance": insight.relevance,
            "expected_lift": insight.expected_lift,
            "verifiability": insight.verifiability,
            "risk": insight.risk,
            "implementation_cost": insight.implementation_cost,
        },
        "semantics": insight.semantics,
        "may_execute": insight.may_execute,
        "may_apply_patch": insight.may_apply_patch,
        "may_push_git": insight.may_push_git,
        "may_write_sibling_repo": insight.may_write_sibling_repo,
        "may_mutate_canon": insight.may_mutate_canon,
    }
