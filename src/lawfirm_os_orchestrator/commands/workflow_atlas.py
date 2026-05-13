from __future__ import annotations

from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.domain.models import LakeReceipt
from lawfirm_os_orchestrator.lake.clients import build_lake_client
from lawfirm_os_orchestrator.ledger.writer import JsonlLedgerWriter
from lawfirm_os_orchestrator.substrate.reader import PathSubstrateClient
from lawfirm_os_orchestrator.util.hashing import sha256_json
from lawfirm_os_orchestrator.util.ids import new_id, new_span_id, new_trace_id
from lawfirm_os_orchestrator.util.time import utc_now
from lawfirm_os_orchestrator.workflow_atlas.diagram import render_mermaid
from lawfirm_os_orchestrator.workflow_atlas.exception_lake_bridge import (
    build_lake_signal,
    build_synthetic_exception_input,
    workflow_escalation_classification,
)
from lawfirm_os_orchestrator.workflow_atlas.extractor import build_ontology_delta, extract_workflow_fragment, read_intake_file
from lawfirm_os_orchestrator.workflow_atlas.integrity import build_integrity_report
from lawfirm_os_orchestrator.workflow_atlas.musk_algorithm import review_with_musk_algorithm
from lawfirm_os_orchestrator.workflow_atlas.packet import build_meeting_prep_packet, write_outputs
from lawfirm_os_orchestrator.workflow_atlas.scoring import score_priority

EXIT_INPUT_POLICY = 2
EXIT_SUBSTRATE = 3
EXIT_ARTIFACT = 5
EXIT_LAKE = 6


def _ledger_record(ids: dict[str, str], step_index: int, step_type: str, step_status: str, **extra: Any) -> dict[str, Any]:
    return {
        "ledger_version": "1",
        "run_id": ids["run_id"],
        "lineage_root_id": ids["lineage_root_id"],
        "trace_id": ids["trace_id"],
        "span_id": new_span_id(),
        "correlation_id": ids["correlation_id"],
        "environment": "local",
        "command_name": "workflow-atlas prepare-meeting",
        "step_index": step_index,
        "step_type": step_type,
        "step_status": step_status,
        "synthetic_or_redacted": True,
        "timestamp": utc_now(),
        **extra,
    }


def _run_prepare_meeting(args) -> tuple[int, dict[str, Any]]:
    topic = args.topic
    out_root = Path(args.out_dir)
    ledger = JsonlLedgerWriter(Path(args.ledger_dir) / "workflow_atlas.jsonl")
    ids = {
        "run_id": new_id("run"),
        "lineage_root_id": new_id("lineage"),
        "trace_id": new_trace_id(),
        "correlation_id": new_id("workflow_atlas"),
    }

    try:
        sessions = [read_intake_file(Path(path), topic) for path in args.intake]
    except Exception as exc:
        return EXIT_INPUT_POLICY, {"status": "failed_intake", "error": str(exc)}

    try:
        snapshot = PathSubstrateClient(Path(args.substrate)).load_snapshot()
    except Exception as exc:
        return EXIT_SUBSTRATE, {"status": "substrate_failed", "error": str(exc)}

    try:
        ledger.append(_ledger_record(ids, 0, "run_started", "started", topic=topic, intake_count=len(sessions)))
        fragment = extract_workflow_fragment(topic, sessions)
        ledger.append(_ledger_record(ids, 1, "workflow_extract", "success", workflow_fragment_id=fragment.workflow_fragment_id, systems=fragment.systems))
        diagram = render_mermaid(fragment)
        ontology = build_ontology_delta(fragment)
        integrity = build_integrity_report(sessions, fragment)
        priority = score_priority(fragment, integrity)
        musk = review_with_musk_algorithm(fragment)
        lake_signal = build_lake_signal(fragment, integrity, priority)
        ledger.append(_ledger_record(ids, 2, "integrity_and_priority", "success", integrity_score=integrity.confidence_score, priority_score=priority.priority_score))

        run_dir = out_root / ids["run_id"]
        lake_receipt: LakeReceipt
        lake_client = build_lake_client(args.lake_mode)
        event = build_synthetic_exception_input(fragment, sessions, priority)
        classification = workflow_escalation_classification(fragment, priority)
        candidate_packet = {
            "schema_type": "workflow-atlas-runtime-candidate-packet",
            "schema_version": "v1",
            "run_id": ids["run_id"],
            "lineage_root_id": ids["lineage_root_id"],
            "trace_id": ids["trace_id"],
            "evidence_id": new_id("workflow_evidence"),
            "workflow_fragment_id": fragment.workflow_fragment_id,
            "manifest_id": snapshot.manifest.manifest_id,
            "manifest_hash": snapshot.manifest_hash,
            "candidate_only": True,
            "no_canonical_mutation": True,
        }
        candidate_packet["packet_hash"] = sha256_json(candidate_packet)
        lake_receipt = lake_client.handoff(
            candidate_packet,
            run_dir,
            event=event,
            snapshot=snapshot,
            classification=classification,
        )
        ledger.append(_ledger_record(ids, 3, "exception_lake_handoff", "success" if lake_receipt.status != "rejected" else "failed", lake_mode=args.lake_mode, handoff_status=lake_receipt.status))

        packet = build_meeting_prep_packet(
            topic=topic,
            fragment=fragment,
            diagram_relpath="workflow_diagram.mmd",
            ontology=ontology,
            integrity=integrity,
            priority=priority,
            musk=musk,
            lake_signal_ref="exception_lake_signal.json",
        )
        write_outputs(
            out_dir=run_dir,
            fragment=fragment,
            diagram=diagram,
            ontology=ontology,
            integrity=integrity,
            priority=priority,
            musk=musk,
            lake_signal=lake_signal,
            lake_receipt=lake_receipt.model_dump(),
            packet=packet,
        )
        ledger.append(_ledger_record(ids, 4, "meeting_prep_packet_build", "success", prep_packet_id=packet.prep_packet_id))
        ledger.append(_ledger_record(ids, 5, "run_completed", "success", output_dir=str(run_dir)))
    except Exception as exc:
        return EXIT_ARTIFACT, {"status": "artifact_failed", "error": str(exc)}

    summary = {
        "status": "ok" if lake_receipt.status != "rejected" or args.lake_mode != "runtime-safe" else "lake_rejected",
        "run_id": ids["run_id"],
        "workflow_fragment_id": fragment.workflow_fragment_id,
        "prep_packet_id": packet.prep_packet_id,
        "output_dir": str(run_dir),
        "diagram_path": str(run_dir / "workflow_diagram.mmd"),
        "meeting_prep_packet_path": str(run_dir / "meeting_prep_packet.md"),
        "integrity_confidence": integrity.confidence_score,
        "priority_score": priority.priority_score,
        "recommended_next_step": priority.recommended_next_step,
        "lake": lake_receipt.model_dump(),
        "candidate_only": True,
        "no_canonical_mutation": True,
    }
    if lake_receipt.status == "rejected" and args.lake_mode == "runtime-safe":
        return EXIT_LAKE, summary
    return 0, summary


def run(args) -> tuple[int, dict[str, Any]]:
    if args.workflow_atlas_command == "prepare-meeting":
        return _run_prepare_meeting(args)
    return 2, {"status": "unknown_workflow_atlas_command", "command": args.workflow_atlas_command}
