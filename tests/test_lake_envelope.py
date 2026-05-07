from __future__ import annotations

from pathlib import Path

import pytest

from lawfirm_os_orchestrator.domain.models import ClassificationResult, SyntheticExceptionInput
from lawfirm_os_orchestrator.lake.envelope import build_exception_event_payload
from lawfirm_os_orchestrator.substrate.reader import PathSubstrateClient
from lawfirm_os_orchestrator.util.json_io import read_json

ROOT = Path(__file__).resolve().parents[1]


def _event() -> SyntheticExceptionInput:
    return SyntheticExceptionInput.model_validate(read_json(ROOT / "examples" / "synthetic_exception_event.json"))


def _snapshot():
    return PathSubstrateClient(ROOT / "tests" / "fixtures" / "substrate").load_snapshot()


def test_lake_envelope_uses_substrate_route_owned_fields() -> None:
    snapshot = _snapshot()
    event = _event()
    classification = ClassificationResult(
        route_id="route.workflow_escalation.v1",
        event_class="workflow_escalation",
        supporting_claim_refs=[ref.claim_ref for ref in event.source_claim_refs],
        confidence=0.9,
    )
    packet = {"run_id": "run_test", "evidence_id": "evidence_test", "packet_hash": "sha256:abc"}

    payload = build_exception_event_payload(
        packet=packet,
        event=event,
        classification=classification,
        snapshot=snapshot,
    )

    assert payload["schema_type"] == "exception-event"
    assert payload["schema_version"] == "v1"
    assert payload["event_class"] == "workflow_escalation"
    assert payload["severity"] == "moderate"
    assert payload["origin"]["layer"] == "workflow"
    assert payload["route"] == {
        "route_id": "route.workflow_escalation.v1",
        "destination_loop": "workflow_redesign",
        "promotion_gate_required": True,
    }
    assert payload["canonical_mutation_control"]["direct_mutation_attempted"] is False
    assert payload["canonical_mutation_control"]["allowed_action"] == "route_for_review"
    assert payload["evidence_refs"] == ["synthetic://document/email-001"]


def test_lake_envelope_fails_closed_on_route_event_mismatch() -> None:
    snapshot = _snapshot()
    event = _event()
    classification = ClassificationResult(
        route_id="route.workflow_escalation.v1",
        event_class="retrieval_miss",
        supporting_claim_refs=[ref.claim_ref for ref in event.source_claim_refs],
        confidence=0.9,
    )

    with pytest.raises(ValueError, match="event_class does not match"):
        build_exception_event_payload(
            packet={"run_id": "run_test"},
            event=event,
            classification=classification,
            snapshot=snapshot,
        )
