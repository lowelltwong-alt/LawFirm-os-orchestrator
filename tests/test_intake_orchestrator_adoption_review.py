from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.validate_intake_orchestrator_adoption_review import (
    IntakeOrchestratorAdoptionReviewError,
    validate_intake_orchestrator_adoption_review,
)


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "intake-orchestrator-adoption-review-registry.json"
VALIDATOR = ROOT / "scripts" / "validate_intake_orchestrator_adoption_review.py"


def _registry_payload() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_intake_orchestrator_adoption_review_registry_validates() -> None:
    data = validate_intake_orchestrator_adoption_review()

    assert data["status"] == "candidate_review_only"
    assert data["non_authoritative"] is True
    assert data["no_canonical_route_or_event_class_authority"] is True


def test_intake_orchestrator_adoption_review_validator_cli_passes() -> None:
    completed = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "validation passed" in completed.stdout


def test_review_items_do_not_assign_routes_events_connectors_or_lake_writes() -> None:
    data = _registry_payload()

    for item in data["review_items"]:
        policy = item["exception_lake_handoff_policy"]
        assert item["label_authority"] == "local_operational_label_only"
        assert item["local_workflow_label"].startswith("orchestrator.local.")
        assert policy["canonical_route_id_assignment"] == "none"
        assert policy["canonical_event_class_assignment"] == "none"
        assert policy["lake_write_authority_now"] is False
        assert "production_connector_write" in item["prohibited_actions"]
        assert "exception_lake_write" in item["prohibited_actions"]
        assert item["direct_promotion_performed"] is False


def test_carrier_rejection_review_captures_unknowns_appeals_and_actuals() -> None:
    data = _registry_payload()
    carrier = next(
        item
        for item in data["review_items"]
        if item["source_proposal_id"]
        == "orchestrator.carrier-rejection-capture-appeal.v0_1"
    )

    assert {entry["channel"] for entry in carrier["capture_channels"]} == {
        "email",
        "carrier_portal",
    }
    assert all(entry["enabled_now"] is False for entry in carrier["capture_channels"])
    assert (
        "unknown_or_new_rejection_pattern"
        in carrier["candidate_rejection_classification_buckets"]
    )
    assert "appeal_result" in carrier["learning_loop_inputs"]
    assert "budget_actual_variance" in carrier["learning_loop_inputs"]
    assert "actual_billed_amount" in carrier["budget_actuals_comparison_inputs"]


def test_validator_rejects_missing_prohibited_route_creation(tmp_path: Path) -> None:
    data = _registry_payload()
    data["review_items"][0]["prohibited_actions"].remove("canonical_route_id_creation")
    bad_registry = tmp_path / "bad_registry.json"
    bad_registry.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(
        IntakeOrchestratorAdoptionReviewError,
        match="canonical_route_id_creation",
    ):
        validate_intake_orchestrator_adoption_review(bad_registry)
