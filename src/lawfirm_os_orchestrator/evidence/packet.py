from __future__ import annotations

from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.domain.models import ClassificationResult, SyntheticExceptionInput, ValidationResult
from lawfirm_os_orchestrator.substrate.contract_lock import contract_lock_record
from lawfirm_os_orchestrator.substrate.reader import SubstrateSnapshot
from lawfirm_os_orchestrator.util.hashing import sha256_file, sha256_json
from lawfirm_os_orchestrator.util.json_io import write_json
from lawfirm_os_orchestrator.util.time import utc_now


def packet_content_hash(packet: dict[str, Any]) -> str:
    canonical_packet = dict(packet)
    canonical_packet.pop("packet_hash", None)
    return sha256_json(canonical_packet)


def write_packet_and_manifest(packet_dir: Path, packet: dict[str, Any]) -> dict[str, Any]:
    packet["packet_hash"] = packet_content_hash(packet)
    write_json(packet_dir / "packet.json", packet)
    manifest = {
        "schema_version": "1.0",
        "evidence_id": packet["evidence_id"],
        "packet_hash": packet["packet_hash"],
        "files": {},
        "created_at": utc_now(),
    }
    for child in sorted(packet_dir.iterdir()):
        if child.is_file() and child.name != "manifest.json":
            manifest["files"][child.name] = sha256_file(child)
    write_json(packet_dir / "manifest.json", manifest)
    return manifest


def build_packet(
    packet_dir: Path,
    event: SyntheticExceptionInput,
    snapshot: SubstrateSnapshot,
    classification: ClassificationResult,
    validations: list[ValidationResult],
    ids: dict[str, str],
    policy_gate: ValidationResult,
    model_request: dict[str, Any],
    model_response: dict[str, Any],
) -> dict[str, Any]:
    packet_dir.mkdir(parents=True, exist_ok=True)
    write_json(packet_dir / "input_event.json", event.model_dump())
    write_json(packet_dir / "policy_gate.json", policy_gate.model_dump())
    write_json(packet_dir / "substrate_snapshot.json", {
        "manifest": snapshot.manifest.model_dump(),
        "manifest_hash": snapshot.manifest_hash,
        "route_registry_hash": snapshot.route_registry_hash,
        "allowed_route_ids": snapshot.allowed_route_ids,
        "allowed_event_classes": snapshot.allowed_event_classes,
        "routes": [route.model_dump() for route in snapshot.routes],
        "contract_lock": contract_lock_record(snapshot.contract_lock),
    })
    write_json(packet_dir / "model_request.json", model_request)
    write_json(packet_dir / "model_response.json", model_response)
    write_json(packet_dir / "classification_result.json", classification.model_dump())
    write_json(packet_dir / "validation_results.json", [v.model_dump() for v in validations])

    packet = {
        "schema_version": "1.0",
        "evidence_id": ids["evidence_id"],
        "run_id": ids["run_id"],
        "lineage_root_id": ids["lineage_root_id"],
        "trace_id": ids["trace_id"],
        "span_id": ids["span_id"],
        "correlation_id": event.input_id,
        "manifest_id": snapshot.manifest.manifest_id,
        "manifest_hash": snapshot.manifest_hash,
        "policy_bundle_id": snapshot.manifest.policy_bundle_id,
        "contract_lock": contract_lock_record(snapshot.contract_lock),
        "synthetic": True,
        "route_decision": {"selected_route_id": classification.route_id, "allowed_event_classes": snapshot.allowed_event_classes},
        "proposal": classification.model_dump(),
        "validation_results": [v.model_dump() for v in validations],
        "source_claim_refs": [ref.claim_ref for ref in event.source_claim_refs],
        "message_history": ["cli_input", "manifest_load", "route_validate", "model_call", "output_validate", "evidence_packet_build"],
        "human_review_required": True,
        "created_at": utc_now(),
    }
    write_packet_and_manifest(packet_dir, packet)
    return packet
