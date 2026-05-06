from __future__ import annotations

from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.domain.models import SyntheticExceptionInput
from lawfirm_os_orchestrator.evidence.packet import build_packet
from lawfirm_os_orchestrator.lake.clients import build_lake_client
from lawfirm_os_orchestrator.ledger.writer import JsonlLedgerWriter
from lawfirm_os_orchestrator.model_router.mock import MockClassificationAdapter
from lawfirm_os_orchestrator.policy.gate import fail_reasons, preflight_policy, validate_classification
from lawfirm_os_orchestrator.substrate.reader import PathSubstrateClient
from lawfirm_os_orchestrator.util.hashing import sha256_file
from lawfirm_os_orchestrator.util.ids import new_id, new_span_id, new_trace_id
from lawfirm_os_orchestrator.util.json_io import read_json, write_json
from lawfirm_os_orchestrator.util.time import utc_now

EXIT_INPUT_POLICY = 2
EXIT_SUBSTRATE = 3
EXIT_MODEL = 4
EXIT_ARTIFACT = 5
EXIT_LAKE = 6


def _ledger_record(ids: dict[str, str], snapshot: Any, step_index: int, step_type: str, step_status: str, **extra: Any) -> dict[str, Any]:
    return {
        "ledger_version": "1",
        "run_id": ids["run_id"],
        "lineage_root_id": ids["lineage_root_id"],
        "trace_id": ids["trace_id"],
        "span_id": new_span_id(),
        "correlation_id": ids["correlation_id"],
        "manifest_id": snapshot.manifest.manifest_id,
        "manifest_hash": snapshot.manifest_hash,
        "policy_bundle_id": snapshot.manifest.policy_bundle_id,
        "environment": "local",
        "command_name": "classify-exception",
        "step_index": step_index,
        "step_type": step_type,
        "step_status": step_status,
        "synthetic": True,
        "retry_count": 0,
        "timestamp": utc_now(),
        **extra,
    }


def run(args) -> tuple[int, dict[str, Any]]:
    input_path = Path(args.input)
    substrate_root = Path(args.substrate)
    ledger_path = Path(args.ledger_dir) / "classify_exception.jsonl"
    packet_root = Path(args.packet_out)

    ids = {
        "run_id": new_id("run"),
        "lineage_root_id": new_id("lineage"),
        "trace_id": new_trace_id(),
        "span_id": new_span_id(),
        "evidence_id": new_id("evidence"),
        "correlation_id": "unset",
    }

    try:
        event = SyntheticExceptionInput.model_validate(read_json(input_path))
        ids["correlation_id"] = event.input_id
    except Exception as exc:
        return EXIT_INPUT_POLICY, {"status": "failed_validation", "error": str(exc)}

    try:
        snapshot = PathSubstrateClient(substrate_root).load_snapshot()
    except Exception as exc:
        return EXIT_SUBSTRATE, {"status": "substrate_failed", "error": str(exc)}

    ledger = JsonlLedgerWriter(ledger_path)
    try:
        policy_gate = preflight_policy(event)
        ledger.append(_ledger_record(ids, snapshot, 0, "run_started", "started", source_claim_refs=[r.claim_ref for r in event.source_claim_refs]))
        ledger.append(_ledger_record(ids, snapshot, 1, "policy_gate", "success"))
    except Exception as exc:
        return EXIT_ARTIFACT, {"status": "artifact_failed", "error": f"ledger write failed: {exc}"}

    try:
        adapter = MockClassificationAdapter()
        model_request = {
            "adapter": adapter.name,
            "allowed_route_ids": snapshot.allowed_route_ids,
            "allowed_event_classes": snapshot.allowed_event_classes,
            "input_hash": sha256_file(input_path),
        }
        classification = adapter.classify(event, snapshot)
        model_response = classification.model_dump()
        validations = validate_classification(classification, snapshot)
        failures = fail_reasons(validations)
        ledger.append(_ledger_record(ids, snapshot, 2, "model_call", "success", selected_route_id=classification.route_id, event_class_proposed=classification.event_class))
        ledger.append(_ledger_record(ids, snapshot, 3, "output_validate", "failed" if failures else "success", selected_route_id=classification.route_id, event_class_proposed=classification.event_class))
        if failures:
            return EXIT_MODEL, {"status": "failed_validation", "reasons": failures}
    except Exception as exc:
        return EXIT_MODEL, {"status": "model_failed", "error": str(exc)}

    packet_dir = packet_root / ids["run_id"] / "evidence"
    try:
        packet = build_packet(packet_dir, event, snapshot, classification, validations, ids, policy_gate, model_request, model_response)
        lake_client = build_lake_client(args.lake_mode)
        receipt = lake_client.handoff(packet, packet_dir)
        packet["lake_handoff"] = receipt.model_dump()
        write_json(packet_dir / "packet.json", packet)
        summary = {
            "run_id": ids["run_id"],
            "status": "ok" if receipt.status != "rejected" else "lake_rejected",
            "route_id": classification.route_id,
            "event_class": classification.event_class,
            "confidence": classification.confidence,
            "needs_human_review": True,
            "ledger_path": str(ledger_path),
            "evidence_packet_path": str(packet_dir),
            "manifest_id": snapshot.manifest.manifest_id,
            "manifest_hash": snapshot.manifest_hash,
            "lake": receipt.model_dump(),
        }
        write_json(packet_dir / "stdout_summary.json", summary)
        ledger.append(_ledger_record(ids, snapshot, 4, "evidence_packet_build", "success", evidence_id=ids["evidence_id"]))
        ledger.append(_ledger_record(ids, snapshot, 5, "run_completed", "success", evidence_id=ids["evidence_id"], lake_mode=args.lake_mode, handoff_attempted=receipt.attempted))
        if receipt.status == "rejected" and args.lake_mode == "runtime-safe":
            return EXIT_LAKE, summary
        return 0, summary
    except Exception as exc:
        return EXIT_ARTIFACT, {"status": "artifact_failed", "error": str(exc)}
