from __future__ import annotations

import hashlib
from typing import Any

from lawfirm_os_orchestrator.domain.models import ClassificationResult, SyntheticExceptionInput
from lawfirm_os_orchestrator.substrate.reader import SubstrateSnapshot
from lawfirm_os_orchestrator.util.time import utc_now


SEVERITY_MAP = {
    "low": "low",
    "medium": "moderate",
    "high": "high",
    "critical": "critical",
}


def _exception_id(run_id: str) -> str:
    numeric = int(hashlib.sha256(run_id.encode("utf-8")).hexdigest()[:12], 16) % 1_000_000
    return f"EXC-{numeric:06d}"


def _route_for_classification(snapshot: SubstrateSnapshot, classification: ClassificationResult):
    for route in snapshot.routes:
        if route.route_id == classification.route_id:
            return route
    raise ValueError(f"classification route_id {classification.route_id} is not in substrate route registry")


def build_exception_event_payload(
    *,
    packet: dict[str, Any],
    event: SyntheticExceptionInput,
    classification: ClassificationResult,
    snapshot: SubstrateSnapshot,
) -> dict[str, Any]:
    """Map an orchestrator classification to an Exception Lake exception-event.

    Route-owned values come from the substrate route registry, not from model
    output. The resulting payload is still synthetic-only evidence.
    """

    route = _route_for_classification(snapshot, classification)
    if classification.event_class != route.event_class:
        raise ValueError("classification event_class does not match substrate route registry")
    if not route.allowed_source_layers:
        raise ValueError(f"route {route.route_id} has no allowed_source_layers")
    if not route.allowed_raw_actions:
        raise ValueError(f"route {route.route_id} has no allowed_raw_actions")
    if route.destination_loop is None:
        raise ValueError(f"route {route.route_id} has no destination_loop")

    payload_summary = event.payload.get("summary") if isinstance(event.payload, dict) else None
    summary = payload_summary if isinstance(payload_summary, str) and len(payload_summary) >= 12 else classification.notes
    if not isinstance(summary, str) or len(summary) < 12:
        summary = "Synthetic orchestrator classification event."

    return {
        "exception_id": _exception_id(str(packet["run_id"])),
        "schema_type": "exception-event",
        "schema_version": "v1",
        "event_class": route.event_class,
        "severity": SEVERITY_MAP[classification.severity],
        "event_time": utc_now(),
        "summary": summary,
        "details": "Synthetic orchestrator classification handed to Exception Lake validation.",
        "origin": {
            "layer": route.allowed_source_layers[0],
            "component": "lawfirm-os-orchestrator",
            "run_id": str(packet["run_id"]),
            "artifact_refs": [str(packet.get("evidence_id", "")), str(packet.get("packet_hash", ""))],
        },
        "route": {
            "route_id": route.route_id,
            "destination_loop": route.destination_loop,
            "promotion_gate_required": route.promotion_gate_required,
        },
        "trust_metadata": {
            "authority_zone": "synthetic-lab",
            "trust_level": "high" if classification.confidence >= 0.8 else "moderate",
            "confidence": classification.confidence,
            "reviewer_required": True,
            "review_role": "human_governance_reviewer",
        },
        "evidence_refs": [ref.claim_ref for ref in event.source_claim_refs],
        "canonical_mutation_control": {
            "direct_mutation_attempted": False,
            "allowed_action": route.allowed_raw_actions[0],
            "boundary_note": "promotion_decision_required_for_canonical_change",
        },
    }
