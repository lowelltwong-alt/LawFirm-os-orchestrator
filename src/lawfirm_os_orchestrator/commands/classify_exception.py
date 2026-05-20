from __future__ import annotations

from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.domain.models import SyntheticExceptionInput
from lawfirm_os_orchestrator.evidence.packet import build_packet, write_packet_and_manifest
from lawfirm_os_orchestrator.lake.clients import build_lake_client
from lawfirm_os_orchestrator.ledger.writer import JsonlLedgerWriter
from lawfirm_os_orchestrator.model_router.mock import MockClassificationAdapter
from lawfirm_os_orchestrator.policy.agent_hostile_controls import (
    DEFAULT_AGENT_CONTROL_SOURCE,
    DEFAULT_CLASSIFIER_TOOL_ID,
    DEFAULT_CLASSIFY_PROMPT_REF,
    DEFAULT_TENANT_ID,
    PolicyDenied,
    agent_identity_gate,
    blast_radius_from_actor,
    build_agent_identity,
    load_revocation_state,
    prompt_integrity_gate,
    prompt_integrity_proof,
    resolve_agent_control_registry_source,
    revocation_gate,
    revocation_snapshot,
    tool_authority_gate,
)
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
EXIT_POLICY = 7


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
        "contract_ref_type": snapshot.contract_lock.validated_ref_type,
        "contract_ref": snapshot.contract_lock.validated_ref,
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

    tool_id = getattr(args, "tool_id", DEFAULT_CLASSIFIER_TOOL_ID)
    prompt_ref = getattr(args, "prompt_ref", DEFAULT_CLASSIFY_PROMPT_REF)
    source_arg = getattr(args, "agent_control_source", None)
    if source_arg is None and any(
        getattr(args, legacy_name, None)
        for legacy_name in ("prompt_registry", "tool_manifest", "revocation_registry")
    ):
        source_arg = "local_fixture"
    try:
        agent_control_source = resolve_agent_control_registry_source(
            source=source_arg or DEFAULT_AGENT_CONTROL_SOURCE,
            substrate_root=getattr(args, "agent_control_substrate", None),
            prompt_registry=getattr(args, "prompt_registry", None),
            tool_manifest=getattr(args, "tool_manifest", None),
            revocation_registry=getattr(args, "revocation_registry", None),
        )
    except Exception as exc:
        return EXIT_POLICY, {
            "status": "policy_denied",
            "gate": "AgentControlRegistrySource",
            "reason_code": "tool_manifest_invalid",
            "error": str(exc),
        }
    prompt_registry = agent_control_source.prompt_registry_path
    revocation_registry = agent_control_source.revocation_registry_path
    tool_manifest = agent_control_source.tool_registry_path
    agent_control_provenance = agent_control_source.provenance(
        contract_sha=(
            getattr(args, "agent_control_contract_sha", None)
            or snapshot.contract_lock.validated_ref
            or snapshot.contract_lock.contract_sha
        ),
    )
    actor = build_agent_identity(
        run_id=ids["run_id"],
        event=event,
        snapshot=snapshot,
        agent_id=getattr(args, "agent_id", None),
        delegating_user_id=getattr(args, "delegating_user_id", None),
        tenant_id=getattr(args, "tenant_id", DEFAULT_TENANT_ID),
        tool_id=tool_id,
    )
    authz_decisions = []
    revocation_state = load_revocation_state(revocation_registry, actor)
    prompt = None
    try:
        authz_decisions.append(agent_identity_gate(ids["run_id"], actor))
        authz_decisions.append(
            revocation_gate(
                run_id=ids["run_id"],
                actor=actor,
                state=revocation_state,
                route_id=event.route_hint,
                tool_id=tool_id,
                evidence_ref=str(revocation_registry) if revocation_registry else None,
            )
        )
        authz_decisions.append(
            tool_authority_gate(
                run_id=ids["run_id"],
                actor=actor,
                tool_manifest_path=tool_manifest,
                tool_id=tool_id,
            )
        )
        prompt_decision, prompt = prompt_integrity_gate(
            run_id=ids["run_id"],
            actor=actor,
            prompt_registry_path=prompt_registry,
            prompt_ref=prompt_ref,
        )
        authz_decisions.append(prompt_decision)
    except PolicyDenied as exc:
        return EXIT_POLICY, {
            "status": "policy_denied",
            "gate": exc.decision.gate,
            "reason_code": exc.decision.reason_code,
            "decision": exc.decision.model_dump(mode="json"),
        }

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
            "agent_instance_id": actor.agent_instance_id,
            "tool_id": tool_id,
            "prompt_ref": prompt_ref,
            "prompt_sha256": prompt.prompt_sha256 if prompt else None,
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
        packet = build_packet(
            packet_dir,
            event,
            snapshot,
            classification,
            validations,
            ids,
            policy_gate,
            model_request,
            model_response,
            agent_identity=actor.model_dump(mode="json"),
            authz_decisions=[decision.model_dump(mode="json") for decision in authz_decisions],
            prompt_integrity=prompt_integrity_proof(prompt),
            revocation_snapshot=revocation_snapshot(
                revocation_state,
                route_id=classification.route_id,
                tool_id=tool_id,
            ),
            blast_radius=blast_radius_from_actor(actor),
            agent_control_provenance=agent_control_provenance,
        )
        lake_client = build_lake_client(args.lake_mode)
        receipt = lake_client.handoff(
            packet,
            packet_dir,
            event=event,
            snapshot=snapshot,
            classification=classification,
        )
        packet["lake_handoff"] = receipt.model_dump()
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
        write_packet_and_manifest(packet_dir, packet)
        ledger.append(_ledger_record(ids, snapshot, 4, "evidence_packet_build", "success", evidence_id=ids["evidence_id"]))
        ledger.append(_ledger_record(ids, snapshot, 5, "run_completed", "success", evidence_id=ids["evidence_id"], lake_mode=args.lake_mode, handoff_attempted=receipt.attempted))
        if receipt.status == "rejected" and args.lake_mode == "runtime-safe":
            return EXIT_LAKE, summary
        return 0, summary
    except Exception as exc:
        return EXIT_ARTIFACT, {"status": "artifact_failed", "error": str(exc)}
