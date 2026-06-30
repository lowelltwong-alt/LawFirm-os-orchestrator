from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.intake.owner_review import (
    LOCAL_WORKFLOW_LABEL as OWNER_WORKFLOW_LABEL,
    RAW_OR_REAL_DATA_KEYS,
    SCHEMA_VERSION as OWNER_PACKET_SCHEMA_VERSION,
    VALID_SHA256,
)
from lawfirm_os_orchestrator.ledger.writer import JsonlLedgerWriter
from lawfirm_os_orchestrator.util.hashing import canonical_json, sha256_json
from lawfirm_os_orchestrator.util.json_io import write_json
from lawfirm_os_orchestrator.util.time import utc_now


SCHEMA_VERSION = "intake_lake_admission_review_packet.v0_1"
LOCAL_REVIEW_LABEL = "orchestrator.local.intake_lake_admission_review_packet"

PROHIBITED_ACTIONS = (
    "write_exception_lake_record",
    "write_sqlite_exception_lake",
    "store_raw_legal_payload",
    "ingest_real_data",
    "submit_budget_to_client_or_carrier",
    "submit_appeal_without_human_authorization",
    "create_canonical_route_id",
    "create_canonical_event_class",
    "write_semantic_substrate",
)

REQUIRED_OWNER_DECISIONS = (
    "exception_lake_owner_accepts_or_rejects_candidate_record_families",
    "exception_lake_owner_confirms_source_hash_and_idempotency_strategy",
    "exception_lake_owner_confirms_append_only_supersession_strategy",
    "semantic_substrate_owner_reviews_any_future_route_or_event_mapping",
    "human_owner_confirms_no_budget_submission_or_appeal_submission_authority",
)

CONTRACT_REFS_BY_RECORD_FAMILY = {
    "intake_proposal_packet": "exception-lake://candidate/evidence/intake-proposal-correction-escalation.v0_1",
    "intake_escalation_or_blocker": "exception-lake://candidate/evidence/intake-proposal-correction-escalation.v0_1",
    "budget_actual_comparison": "exception-lake://candidate/evidence/budget-template-change-actual-variance.v0_1",
    "budget_actual_variance_driver_candidate": "exception-lake://candidate/evidence/budget-template-change-actual-variance.v0_1",
    "carrier_rejection_notice": "exception-lake://candidate/admission/carrier-rejection-notice.v0_1",
    "carrier_rejection_reconciliation": "exception-lake://candidate/admission/carrier-rejection-reconciliation.v0_1",
    "carrier_rejection_review_outcome": "exception-lake://candidate/admission/carrier-rejection-review-outcome.v0_1",
    "carrier_fix_or_appeal_action": "exception-lake://candidate/admission/carrier-appeal-submission.v0_1",
    "carrier_appeal_result": "exception-lake://candidate/admission/carrier-appeal-result.v0_1",
    "carrier_financial_outcome": "exception-lake://candidate/admission/carrier-financial-outcome.v0_1",
    "carrier_rejection_learning_candidate": "exception-lake://candidate/admission/carrier-rejection-learning.v0_1",
}


class IntakeLakeAdmissionReviewError(ValueError):
    """Raised when an intake packet is not safe to package for Lake review."""


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise IntakeLakeAdmissionReviewError(f"{label} must be an object")
    return value


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise IntakeLakeAdmissionReviewError(f"{label} must be a list")
    return value


def _contains_forbidden_key(value: Any, path: str = "$") -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in RAW_OR_REAL_DATA_KEYS:
                return f"{path}.{key}"
            found = _contains_forbidden_key(child, f"{path}.{key}")
            if found:
                return found
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found = _contains_forbidden_key(child, f"{path}[{index}]")
            if found:
                return found
    return None


def _hash_without_field(payload: dict[str, Any], field: str) -> str:
    clean = {key: value for key, value in payload.items() if key != field}
    return hashlib.sha256(canonical_json(clean)).hexdigest()


def _packet_hash(packet: dict[str, Any]) -> str:
    return _hash_without_field(packet, "packet_hash")


def _candidate_summary_hash(summary: dict[str, Any]) -> str:
    return _hash_without_field(summary, "candidate_record_summary_hash")


def _source_lookup(owner_packet: dict[str, Any]) -> dict[str, str]:
    inventory = _require_mapping(
        owner_packet.get("source_inventory"), "source_inventory"
    )
    sources = _require_list(inventory.get("sources", []), "source_inventory.sources")
    lookup: dict[str, str] = {}
    for raw_source in sources:
        source = _require_mapping(raw_source, "source_inventory.sources[]")
        source_ref_id = str(source.get("source_ref_id", "")).strip()
        sha256 = str(source.get("sha256", "")).strip()
        if source_ref_id:
            lookup[source_ref_id] = sha256
    return lookup


def _validate_owner_packet_boundary(owner_packet: dict[str, Any]) -> None:
    for required_key in ("packet_id", "status", "packet_hash", "source_inventory"):
        if required_key not in owner_packet:
            raise IntakeLakeAdmissionReviewError(
                f"owner packet missing required key: {required_key}"
            )
    if not str(owner_packet.get("packet_id", "")).strip():
        raise IntakeLakeAdmissionReviewError("owner packet packet_id must be non-empty")
    if owner_packet.get("schema_version") != OWNER_PACKET_SCHEMA_VERSION:
        raise IntakeLakeAdmissionReviewError(
            f"owner packet schema_version must be {OWNER_PACKET_SCHEMA_VERSION!r}"
        )
    if owner_packet.get("workflow_label") != OWNER_WORKFLOW_LABEL:
        raise IntakeLakeAdmissionReviewError(
            f"owner packet workflow_label must be {OWNER_WORKFLOW_LABEL!r}"
        )
    if owner_packet.get("source_repo") != "LawFirm-os-orchestrator":
        raise IntakeLakeAdmissionReviewError(
            "owner packet source_repo must be LawFirm-os-orchestrator"
        )
    if owner_packet.get("source_vertical_repo") != "LawFirm-os-intake":
        raise IntakeLakeAdmissionReviewError(
            "owner packet source_vertical_repo must be LawFirm-os-intake"
        )
    if owner_packet.get("synthetic") is not True:
        raise IntakeLakeAdmissionReviewError("owner packet synthetic must be true")
    for flag in (
        "contains_real_firm_data",
        "contains_real_client_data",
        "contains_real_matter_data",
        "contains_privileged_data",
    ):
        if owner_packet.get(flag) is True:
            raise IntakeLakeAdmissionReviewError(f"owner packet {flag} must be false")
    if owner_packet.get("non_authoritative") is not True:
        raise IntakeLakeAdmissionReviewError("owner packet must be non_authoritative")
    if owner_packet.get("not_authorized_for_client_submission") is not True:
        raise IntakeLakeAdmissionReviewError(
            "owner packet must not be authorized for client submission"
        )

    forbidden = _contains_forbidden_key(owner_packet)
    if forbidden:
        raise IntakeLakeAdmissionReviewError(
            f"forbidden raw/real data field is not allowed in owner packet: {forbidden}"
        )

    declared_hash = str(owner_packet.get("packet_hash", "")).strip()
    if not VALID_SHA256.match(declared_hash):
        raise IntakeLakeAdmissionReviewError(
            "owner packet packet_hash must be a bare 64-character sha256"
        )
    expected_hash = _hash_without_field(owner_packet, "packet_hash")
    if declared_hash != expected_hash:
        raise IntakeLakeAdmissionReviewError(
            "owner packet packet_hash does not match canonical content"
        )

    preview = _require_mapping(
        owner_packet.get("exception_lake_handoff_preview"),
        "exception_lake_handoff_preview",
    )
    if preview.get("handoff_allowed") is not False:
        raise IntakeLakeAdmissionReviewError(
            "owner packet Lake handoff must not be allowed"
        )
    if preview.get("lake_write_authority_now") is not False:
        raise IntakeLakeAdmissionReviewError(
            "owner packet Lake write authority must be false"
        )
    if preview.get("canonical_route_id_assignment") != "none":
        raise IntakeLakeAdmissionReviewError(
            "owner packet must not assign a canonical route_id"
        )
    if preview.get("canonical_event_class_assignment") != "none":
        raise IntakeLakeAdmissionReviewError(
            "owner packet must not assign a canonical event_class"
        )


def validate_owner_packet_for_lake_review(owner_packet: dict[str, Any]) -> None:
    _validate_owner_packet_boundary(owner_packet)


def _candidate_record(
    *,
    owner_packet: dict[str, Any],
    record_family: str,
    local_record_label: str,
    evidence_ref: str,
    source_ref_ids: list[str] | None = None,
    detail: dict[str, Any] | None = None,
    blockers: list[str] | None = None,
) -> dict[str, Any]:
    source_ref_ids = sorted(set(source_ref_ids or []))
    source_hashes_by_ref = _source_lookup(owner_packet)
    source_hashes = [
        source_hashes_by_ref[source_ref_id]
        for source_ref_id in source_ref_ids
        if source_hashes_by_ref.get(source_ref_id)
    ]
    basis = {
        "owner_packet_hash": owner_packet["packet_hash"],
        "record_family": record_family,
        "local_record_label": local_record_label,
        "evidence_ref": evidence_ref,
        "source_ref_ids": source_ref_ids,
    }
    summary: dict[str, Any] = {
        "record_family": record_family,
        "local_record_label": local_record_label,
        "proposed_contract_ref": CONTRACT_REFS_BY_RECORD_FAMILY[record_family],
        "candidate_only": True,
        "owner_review_required": True,
        "admission_status": "not_admitted",
        "source_ref_ids": source_ref_ids,
        "source_hashes": sorted(set(source_hashes)),
        "source_hash_status": "present"
        if len(source_hashes) == len(source_ref_ids)
        else "blocked",
        "evidence_ref": evidence_ref,
        "idempotency_key": hashlib.sha256(canonical_json(basis)).hexdigest(),
        "record_hash_required_before_admission": True,
        "record_hash_status": "not_minted_until_exception_lake_owner_contract_acceptance",
        "previous_record_hash_or_null": None,
        "contract_surface_sha256": None,
        "detail": detail or {},
        "blockers": blockers or [],
    }
    summary["candidate_record_summary_hash"] = _candidate_summary_hash(summary)
    return summary


def _owner_gate_records(owner_packet: dict[str, Any]) -> list[dict[str, Any]]:
    records = [
        _candidate_record(
            owner_packet=owner_packet,
            record_family="intake_proposal_packet",
            local_record_label="owner_review_packet_summary",
            evidence_ref=f"owner_packet:{owner_packet['packet_id']}",
            source_ref_ids=[
                source["source_ref_id"]
                for source in owner_packet["source_inventory"]["sources"]
            ],
            detail={
                "owner_packet_status": owner_packet["status"],
                "owner_blocker_count": len(owner_packet.get("blockers") or []),
            },
            blockers=list(owner_packet.get("blockers") or []),
        )
    ]

    for blocker in owner_packet.get("blockers") or []:
        records.append(
            _candidate_record(
                owner_packet=owner_packet,
                record_family="intake_escalation_or_blocker",
                local_record_label="owner_review_blocker",
                evidence_ref=f"owner_packet_blocker:{blocker}",
                detail={"blocker": blocker},
                blockers=[blocker],
            )
        )
    return records


def _budget_actual_records(owner_packet: dict[str, Any]) -> list[dict[str, Any]]:
    actuals = _require_mapping(
        owner_packet.get("budget_actuals_variance_report", {}),
        "budget_actuals_variance_report",
    )
    lines = _require_list(
        actuals.get("lines", []), "budget_actuals_variance_report.lines"
    )
    if not lines:
        return []

    records = [
        _candidate_record(
            owner_packet=owner_packet,
            record_family="budget_actual_comparison",
            local_record_label="budget_actuals_phase_and_task_comparison",
            evidence_ref=f"owner_packet:{owner_packet['packet_id']}#budget_actuals",
            detail={
                "line_count": len(lines),
                "phase_count": len(actuals.get("phase_totals") or {}),
                "totals": dict(actuals.get("totals") or {}),
            },
        )
    ]
    for line in lines:
        line_id = str(line.get("line_id", "")).strip()
        driver = str(line.get("variance_driver_candidate", "unknown")).strip()
        records.append(
            _candidate_record(
                owner_packet=owner_packet,
                record_family="budget_actual_variance_driver_candidate",
                local_record_label="budget_actual_variance_driver_candidate",
                evidence_ref=f"budget_actual_line:{line_id}",
                detail={
                    "line_id": line_id,
                    "budget_phase": line.get("budget_phase"),
                    "budget_task_code": line.get("budget_task_code"),
                    "variance_driver_candidate": driver or "unknown",
                    "variance_to_proposed": line.get("variance_to_proposed"),
                    "variance_to_carrier_compliant_projection": line.get(
                        "variance_to_carrier_compliant_projection"
                    ),
                },
            )
        )
    return records


def _carrier_records(owner_packet: dict[str, Any]) -> list[dict[str, Any]]:
    report = _require_mapping(
        owner_packet.get("carrier_rejection_report", {}), "carrier_rejection_report"
    )
    notices = _require_list(
        report.get("notices", []), "carrier_rejection_report.notices"
    )
    records: list[dict[str, Any]] = []
    for notice in notices:
        notice_id = str(notice.get("notice_id", "")).strip()
        source_ref_id = str(notice.get("source_ref_id", "")).strip()
        source_ref_ids = [source_ref_id] if source_ref_id else []
        bucket = str(notice.get("classification_bucket", "")).strip()
        states = list(notice.get("response_state_ledger_states") or [])
        notice_blockers: list[str] = []
        if notice.get("source_status") != "matched":
            notice_blockers.append(f"{notice_id}:missing_source_ref")
        if notice.get("appeal_requested") and not notice.get("appeal_authorized"):
            notice_blockers.append(f"{notice_id}:appeal_requires_human_authorization")

        records.append(
            _candidate_record(
                owner_packet=owner_packet,
                record_family="carrier_rejection_notice",
                local_record_label="carrier_rejection_notice_candidate",
                evidence_ref=f"carrier_rejection_notice:{notice_id}",
                source_ref_ids=source_ref_ids,
                detail={
                    "notice_id": notice_id,
                    "channel": notice.get("channel"),
                    "classification_bucket": bucket,
                    "classification_status": notice.get("classification_status"),
                },
                blockers=notice_blockers,
            )
        )
        if "reconciled_to_budget_or_invoice" in states:
            records.append(
                _candidate_record(
                    owner_packet=owner_packet,
                    record_family="carrier_rejection_reconciliation",
                    local_record_label="carrier_rejection_budget_or_invoice_reconciliation_candidate",
                    evidence_ref=f"carrier_rejection_notice:{notice_id}#reconciliation",
                    source_ref_ids=source_ref_ids,
                    detail={"notice_id": notice_id, "states": states},
                )
            )
        if "human_review_required" in states:
            records.append(
                _candidate_record(
                    owner_packet=owner_packet,
                    record_family="carrier_rejection_review_outcome",
                    local_record_label="carrier_rejection_human_review_outcome_missing",
                    evidence_ref=f"carrier_rejection_notice:{notice_id}#human_review",
                    source_ref_ids=source_ref_ids,
                    detail={
                        "notice_id": notice_id,
                        "required_state": "human_review_required",
                    },
                    blockers=[f"{notice_id}:human_review_outcome_required"],
                )
            )
        if notice.get("appeal_requested"):
            records.append(
                _candidate_record(
                    owner_packet=owner_packet,
                    record_family="carrier_fix_or_appeal_action",
                    local_record_label="carrier_fix_or_appeal_action_candidate",
                    evidence_ref=f"carrier_rejection_notice:{notice_id}#appeal",
                    source_ref_ids=source_ref_ids,
                    detail={
                        "notice_id": notice_id,
                        "appeal_authorized": notice.get("appeal_authorized"),
                        "human_authorization_ref": notice.get(
                            "human_authorization_ref"
                        ),
                    },
                    blockers=(
                        []
                        if notice.get("appeal_authorized")
                        else [f"{notice_id}:appeal_authorization_required"]
                    ),
                )
            )
        if notice.get("appeal_results_appended"):
            records.append(
                _candidate_record(
                    owner_packet=owner_packet,
                    record_family="carrier_appeal_result",
                    local_record_label="carrier_appeal_result_candidate",
                    evidence_ref=f"carrier_rejection_notice:{notice_id}#appeal_result",
                    source_ref_ids=source_ref_ids,
                    detail={
                        "notice_id": notice_id,
                        "result_count": len(
                            notice.get("appeal_results_appended") or []
                        ),
                    },
                )
            )
        if notice.get("financial_outcome"):
            records.append(
                _candidate_record(
                    owner_packet=owner_packet,
                    record_family="carrier_financial_outcome",
                    local_record_label="carrier_financial_outcome_candidate",
                    evidence_ref=f"carrier_rejection_notice:{notice_id}#financial_outcome",
                    source_ref_ids=source_ref_ids,
                    detail={
                        "notice_id": notice_id,
                        "financial_outcome": notice.get("financial_outcome"),
                    },
                )
            )
        records.append(
            _candidate_record(
                owner_packet=owner_packet,
                record_family="carrier_rejection_learning_candidate",
                local_record_label="carrier_rejection_learning_candidate",
                evidence_ref=f"carrier_rejection_notice:{notice_id}#learning",
                source_ref_ids=source_ref_ids,
                detail={
                    "notice_id": notice_id,
                    "classification_bucket": bucket,
                    "unknown_or_new_pattern": bucket
                    == "unknown_or_new_rejection_pattern",
                },
            )
        )
    return records


def _candidate_records(owner_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        *_owner_gate_records(owner_packet),
        *_budget_actual_records(owner_packet),
        *_carrier_records(owner_packet),
    ]


def _source_inventory_summary(owner_packet: dict[str, Any]) -> dict[str, Any]:
    inventory = _require_mapping(
        owner_packet.get("source_inventory"), "source_inventory"
    )
    sources = _require_list(inventory.get("sources", []), "source_inventory.sources")
    source_hashes = [
        str(source.get("sha256", "")).strip()
        for source in sources
        if isinstance(source, dict)
    ]
    invalid_hashes = [
        source_hash
        for source_hash in source_hashes
        if not VALID_SHA256.match(source_hash)
    ]
    return {
        "status": inventory.get("status"),
        "source_count": inventory.get("source_count", len(sources)),
        "source_ref_ids": [
            str(source.get("source_ref_id", "")).strip()
            for source in sources
            if isinstance(source, dict)
        ],
        "source_hashes": source_hashes,
        "duplicate_source_ref_ids": list(
            inventory.get("duplicate_source_ref_ids") or []
        ),
        "duplicate_hashes": list(inventory.get("duplicate_hashes") or []),
        "missing_hash_source_ref_ids": list(
            inventory.get("missing_hash_source_ref_ids") or []
        ),
        "invalid_hash_source_ref_ids": list(
            inventory.get("invalid_hash_source_ref_ids") or []
        ),
        "invalid_hash_values_detected": invalid_hashes,
    }


def _packet_blockers(
    owner_packet: dict[str, Any],
    records: list[dict[str, Any]],
) -> list[str]:
    blockers = ["exception_lake_owner_contract:required"]
    blockers.extend(
        f"owner_packet:{blocker}" for blocker in owner_packet.get("blockers") or []
    )
    if owner_packet.get("source_inventory", {}).get("status") != "passed":
        blockers.append("source_inventory:not_ready_for_lake_admission")
    for record in records:
        blockers.extend(
            f"{record['record_family']}:{blocker}"
            for blocker in record.get("blockers", [])
        )
        if record.get("source_hash_status") != "present":
            blockers.append(f"{record['record_family']}:source_hash_missing")
    return sorted(set(blockers))


def prepare_intake_lake_admission_review_packet(
    owner_packet: dict[str, Any],
) -> dict[str, Any]:
    validate_owner_packet_for_lake_review(owner_packet)
    generated_at = str(owner_packet.get("generated_at") or utc_now())
    records = _candidate_records(owner_packet)
    record_families = sorted({record["record_family"] for record in records})
    blockers = _packet_blockers(owner_packet, records)
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "packet_id": "intake_lake_review_"
        + sha256_json(
            {
                "owner_packet_id": owner_packet["packet_id"],
                "owner_packet_hash": owner_packet["packet_hash"],
            }
        ).removeprefix("sha256:")[:16],
        "generated_at": generated_at,
        "source_repo": "LawFirm-os-orchestrator",
        "source_vertical_repo": "LawFirm-os-intake",
        "target_repo": "LawFirm-os-exceptions-lake-runtime",
        "workflow_label": LOCAL_REVIEW_LABEL,
        "owner_workflow_label": owner_packet["workflow_label"],
        "owner_packet_id": owner_packet["packet_id"],
        "owner_packet_hash": owner_packet["packet_hash"],
        "owner_packet_status": owner_packet["status"],
        "request_id": owner_packet.get("request_id"),
        "synthetic": True,
        "contains_real_firm_data": False,
        "non_authoritative": True,
        "proposed_for_owner_review": True,
        "not_authorized_for_client_submission": True,
        "status": "blocked_pending_exception_lake_owner_review",
        "admission_controls": {
            "append_only_required": True,
            "supersession_instead_of_update_required": True,
            "idempotency_key_required": True,
            "source_hash_required": True,
            "record_hash_required_before_admission": True,
            "orchestrator_packet_required": True,
            "raw_payload_storage_allowed": False,
            "sqlite_write_authorized_now": False,
            "real_data_authorized_now": False,
            "external_write_authorized_now": False,
            "lake_write_authority_now": False,
            "lake_handoff_allowed": False,
            "canonical_route_id_assignment": "none",
            "canonical_event_class_assignment": "none",
        },
        "idempotency_basis": {
            "owner_packet_id": owner_packet["packet_id"],
            "owner_packet_hash": owner_packet["packet_hash"],
            "request_id": owner_packet.get("request_id"),
            "workflow_label": owner_packet["workflow_label"],
            "source_ref_ids": _source_inventory_summary(owner_packet)["source_ref_ids"],
            "source_hashes": _source_inventory_summary(owner_packet)["source_hashes"],
        },
        "source_inventory_summary": _source_inventory_summary(owner_packet),
        "owner_review_gate_summary": {
            "human_pause_status": owner_packet.get("human_pause_report", {}).get(
                "status"
            ),
            "budget_precondition_status": owner_packet.get(
                "budget_precondition_report", {}
            ).get("status"),
            "carrier_rejection_status": owner_packet.get(
                "carrier_rejection_report", {}
            ).get("status"),
            "budget_actuals_status": owner_packet.get(
                "budget_actuals_variance_report", {}
            ).get("status"),
            "decision_model_status": owner_packet.get("decision_model", {}).get(
                "status"
            ),
            "owner_blockers": list(owner_packet.get("blockers") or []),
        },
        "candidate_admission_record_families": record_families,
        "candidate_record_count": len(records),
        "candidate_record_summaries": records,
        "required_owner_decisions": list(REQUIRED_OWNER_DECISIONS),
        "prohibited_actions": list(PROHIBITED_ACTIONS),
        "blockers": blockers,
    }
    packet["packet_hash"] = _packet_hash(packet)
    return packet


def _markdown(packet: dict[str, Any]) -> str:
    families = "\n".join(
        f"- `{family}`" for family in packet["candidate_admission_record_families"]
    )
    blockers = "\n".join(f"- `{blocker}`" for blocker in packet["blockers"])
    return (
        "# Intake Lake Admission Review Packet\n\n"
        f"Packet: `{packet['packet_id']}`\n\n"
        f"Owner packet: `{packet['owner_packet_id']}`\n\n"
        f"Status: `{packet['status']}`\n\n"
        "## Controls\n\n"
        "- candidate-only and non-authoritative\n"
        "- no Lake write authority\n"
        "- no SQLite write authority\n"
        "- no raw payload storage\n"
        "- no canonical route or event-class assignment\n\n"
        "## Candidate Record Families\n\n"
        f"{families}\n\n"
        "## Blockers\n\n"
        f"{blockers}\n"
    )


def write_intake_lake_admission_review_artifacts(
    *,
    packet: dict[str, Any],
    out_dir: Path,
    ledger_dir: Path,
) -> dict[str, Any]:
    packet_dir = out_dir / str(packet["packet_id"])
    write_json(packet_dir / "intake_lake_admission_review_packet.json", packet)
    write_json(
        packet_dir / "candidate_record_summaries.json",
        packet["candidate_record_summaries"],
    )
    (packet_dir / "intake_lake_admission_review_packet.md").write_text(
        _markdown(packet),
        encoding="utf-8",
    )

    ledger_path = ledger_dir / "intake_lake_admission_review.jsonl"
    JsonlLedgerWriter(ledger_path).append(
        {
            "ledger_version": "1",
            "command_name": "intake build-lake-admission-review-packet",
            "packet_id": packet["packet_id"],
            "packet_hash": packet["packet_hash"],
            "owner_packet_id": packet["owner_packet_id"],
            "owner_packet_hash": packet["owner_packet_hash"],
            "workflow_label": packet["workflow_label"],
            "status": packet["status"],
            "synthetic": True,
            "non_authoritative": True,
            "lake_handoff_allowed": False,
            "sqlite_write_authorized_now": False,
            "timestamp": packet["generated_at"],
        }
    )
    summary = {
        "status": packet["status"],
        "packet_id": packet["packet_id"],
        "packet_hash": packet["packet_hash"],
        "packet_path": str(packet_dir / "intake_lake_admission_review_packet.json"),
        "markdown_path": str(packet_dir / "intake_lake_admission_review_packet.md"),
        "ledger_path": str(ledger_path),
        "lake_handoff_allowed": False,
        "sqlite_write_authorized_now": False,
        "not_authorized_for_client_submission": True,
        "candidate_record_count": packet["candidate_record_count"],
        "blocker_count": len(packet["blockers"]),
    }
    write_json(packet_dir / "stdout_summary.json", summary)
    return summary
