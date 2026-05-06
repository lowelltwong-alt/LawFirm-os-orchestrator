from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from lawfirm_os_orchestrator.learning.models import AlgorithmInsight
from lawfirm_os_orchestrator.learning.scoring import calculate_upgrade_priority, score_algorithm_insight


def insight(**overrides) -> AlgorithmInsight:
    data = {
        "source_ref": "discovery_signal:evaluator-guided-search-example",
        "claim": "Evaluator-guided search can rank proposal-only validator changes.",
        "method_category": "evaluator_guided_search",
        "target_surface": "validators",
        "affected_metric": "first_pass_validation_rate",
        "credibility": 0.8,
        "relevance": 0.9,
        "expected_lift": 0.25,
        "verifiability": 0.85,
        "risk": 0.4,
        "implementation_cost": 0.5,
    }
    data.update(overrides)
    return AlgorithmInsight.model_validate(data)


def test_upgrade_priority_is_monotonic_for_expected_lift():
    low = score_algorithm_insight(insight(expected_lift=0.1))["upgrade_priority"]
    high = score_algorithm_insight(insight(expected_lift=0.3))["upgrade_priority"]
    assert high > low


def test_upgrade_priority_rejects_divide_by_zero_inputs():
    with pytest.raises(ValueError, match="risk"):
        calculate_upgrade_priority(
            credibility=0.8,
            relevance=0.9,
            expected_lift=0.2,
            verifiability=0.7,
            risk=0.0,
            implementation_cost=0.5,
        )
    with pytest.raises(ValueError, match="implementation_cost"):
        calculate_upgrade_priority(
            credibility=0.8,
            relevance=0.9,
            expected_lift=0.2,
            verifiability=0.7,
            risk=0.4,
            implementation_cost=0.0,
        )


def test_algorithm_insight_rejects_forbidden_target_surface():
    with pytest.raises(ValidationError):
        insight(target_surface="canonical_route_ids")


def test_algorithm_scoring_is_deterministic_and_proposal_only():
    candidate = insight()
    first = score_algorithm_insight(candidate)
    second = score_algorithm_insight(candidate)
    assert first == second
    assert first["formula"] == "credibility * relevance * expected_lift * verifiability / risk / implementation_cost"
    assert first["semantics"] == "proposal_only"
    assert first["may_execute"] is False
    assert first["may_apply_patch"] is False
    assert first["may_push_git"] is False
    assert first["may_write_sibling_repo"] is False
    assert first["may_mutate_canon"] is False


def test_algorithm_insight_example_validates():
    raw = json.loads(open("examples/research_signals/algorithm_insight_example.json", encoding="utf-8").read())
    candidate = AlgorithmInsight.model_validate(raw)
    scored = score_algorithm_insight(candidate)
    assert scored["target_surface"] == "validators"
    assert scored["affected_metric"] == "first_pass_validation_rate"
    assert scored["upgrade_priority"] > 0
