from __future__ import annotations

from lawfirm_os_orchestrator.domain.models import ClassificationResult, SyntheticExceptionInput
from lawfirm_os_orchestrator.substrate.reader import SubstrateSnapshot


class MockClassificationAdapter:
    name = "mock"

    def classify(self, event: SyntheticExceptionInput, snapshot: SubstrateSnapshot) -> ClassificationResult:
        route_id = event.route_hint if event.route_hint in snapshot.allowed_route_ids else snapshot.allowed_route_ids[0]
        event_class = snapshot.event_class_for_route(route_id) or snapshot.allowed_event_classes[0]
        return ClassificationResult(
            route_id=route_id,
            event_class=event_class,
            severity="medium",
            reason_codes=["synthetic_fixture_classification"],
            supporting_claim_refs=[ref.claim_ref for ref in event.source_claim_refs],
            confidence=0.90,
            notes="Deterministic mock classification; proposal only.",
        )
