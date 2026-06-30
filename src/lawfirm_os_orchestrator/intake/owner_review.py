from __future__ import annotations

from decimal import Decimal, InvalidOperation
import hashlib
import re
from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.ledger.writer import JsonlLedgerWriter
from lawfirm_os_orchestrator.util.hashing import canonical_json, sha256_json
from lawfirm_os_orchestrator.util.json_io import write_json
from lawfirm_os_orchestrator.util.time import utc_now


SCHEMA_VERSION = "intake_owner_review_packet.v0_1"
REQUEST_SCHEMA_VERSION = "intake_owner_review_request.v0_1"
LOCAL_WORKFLOW_LABEL = "orchestrator.local.intake_to_budget_owner_review"
VALID_SHA256 = re.compile(r"^[0-9a-f]{64}$")
MONEY_QUANT = Decimal("0.01")

REQUIRED_HUMAN_PAUSES = (
    "confirm_matter_family",
    "confirm_representation_posture",
    "confirm_principal_party_roles",
    "approve_budget_proposal_before_external_submission",
    "approve_exception_lake_handoff_before_admission",
)

CONFIRMED_STATUSES = {"confirmed", "approved", "human_only", "declined_referred"}
REQUIRED_BUDGET_PRECONDITIONS = (
    "party_count_known",
    "complexity_known",
    "matter_family_confirmed",
    "representation_posture_confirmed",
    "principal_roles_confirmed",
)

REJECTION_BUCKET_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("rate_or_cap_rejection", ("rate", "cap", "hourly", "discount", "maximum")),
    (
        "staffing_or_leverage_rejection",
        ("staffing", "partner", "associate", "leverage", "timekeeper"),
    ),
    ("task_scope_rejection", ("scope", "task", "phase", "utbms", "outside")),
    (
        "expense_documentation_rejection",
        ("expense", "receipt", "documentation", "invoice backup"),
    ),
    (
        "preapproval_missing",
        ("preapproval", "pre-approval", "authorization required", "not approved"),
    ),
    (
        "duplicate_or_format_rejection",
        ("duplicate", "format", "template", "spreadsheet"),
    ),
    ("timing_or_deadline_rejection", ("late", "deadline", "timing", "untimely")),
    ("portal_technical_rejection", ("portal", "technical", "upload", "system error")),
    (
        "identity_or_matter_mismatch",
        ("matter mismatch", "identity", "claim number", "insured", "wrong matter"),
    ),
    (
        "actuals_or_invoice_variance",
        ("actual", "variance", "billed", "over budget", "invoice"),
    ),
)

KNOWN_REJECTION_BUCKETS = tuple(bucket for bucket, _ in REJECTION_BUCKET_KEYWORDS) + (
    "unknown_or_new_rejection_pattern",
)

RAW_OR_REAL_DATA_KEYS = {
    "raw_client_payload",
    "raw_matter_payload",
    "privileged_text",
    "real_client_name",
    "real_matter_number",
    "client_secret",
    "production_transcript",
}

PROHIBITED_NEXT_STEPS = (
    "open_matter",
    "clear_conflicts",
    "submit_budget_to_client_or_carrier",
    "submit_appeal_without_human_authorization",
    "write_exception_lake_record",
    "create_canonical_route_id",
    "create_canonical_event_class",
    "write_semantic_substrate",
)


class IntakeOwnerReviewError(ValueError):
    """Raised when an intake owner-review request violates local boundaries."""


def _money(value: Any, field: str) -> Decimal:
    if value is None or value == "":
        return Decimal("0.00")
    try:
        return Decimal(str(value)).quantize(MONEY_QUANT)
    except (InvalidOperation, ValueError) as exc:
        raise IntakeOwnerReviewError(f"{field} must be a decimal money value") from exc


def _money_str(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return str(value.quantize(MONEY_QUANT))


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise IntakeOwnerReviewError(f"{label} must be an object")
    return value


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise IntakeOwnerReviewError(f"{label} must be a list")
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


def validate_request_boundary(request: dict[str, Any]) -> None:
    if request.get("schema_version") != REQUEST_SCHEMA_VERSION:
        raise IntakeOwnerReviewError(
            f"schema_version must be {REQUEST_SCHEMA_VERSION!r}"
        )
    if request.get("synthetic") is not True:
        raise IntakeOwnerReviewError("synthetic must be true")
    for flag in (
        "contains_real_firm_data",
        "contains_real_client_data",
        "contains_real_matter_data",
        "contains_privileged_data",
    ):
        if request.get(flag) is True:
            raise IntakeOwnerReviewError(f"{flag} must be false")
    if request.get("workflow_label") != LOCAL_WORKFLOW_LABEL:
        raise IntakeOwnerReviewError(
            f"workflow_label must be local label {LOCAL_WORKFLOW_LABEL!r}"
        )
    forbidden = _contains_forbidden_key(request)
    if forbidden:
        raise IntakeOwnerReviewError(
            f"forbidden raw/real data field is not allowed in request: {forbidden}"
        )
    if request.get("external_submission_requested") is True:
        raise IntakeOwnerReviewError("external submissions are out of scope")
    if request.get("lake_handoff_mode", "disabled") not in {
        "disabled",
        "validate_only",
    }:
        raise IntakeOwnerReviewError(
            "intake owner review can only use disabled or validate_only Lake mode"
        )


def build_source_inventory(source_refs: list[Any]) -> dict[str, Any]:
    refs = [_require_mapping(item, "source_refs[]") for item in source_refs]
    seen_ids: set[str] = set()
    seen_hashes: set[str] = set()
    duplicate_ids: list[str] = []
    duplicate_hashes: list[str] = []
    missing_hashes: list[str] = []
    invalid_hashes: list[str] = []
    normalized: list[dict[str, Any]] = []

    for ref in refs:
        source_id = str(ref.get("source_ref_id", "")).strip()
        sha256 = str(ref.get("sha256", "")).strip()
        if not source_id:
            raise IntakeOwnerReviewError("every source_ref must include source_ref_id")
        if source_id in seen_ids:
            duplicate_ids.append(source_id)
        seen_ids.add(source_id)
        if not sha256:
            missing_hashes.append(source_id)
        elif not VALID_SHA256.match(sha256):
            invalid_hashes.append(source_id)
        elif sha256 in seen_hashes:
            duplicate_hashes.append(sha256)
        seen_hashes.add(sha256)
        normalized.append(
            {
                "source_ref_id": source_id,
                "sha256": sha256,
                "segment_refs": list(ref.get("segment_refs", [])),
                "coverage": ref.get("coverage", "unknown"),
            }
        )

    status = "passed"
    if not normalized or missing_hashes or invalid_hashes:
        status = "blocked"
    elif duplicate_ids or duplicate_hashes:
        status = "needs_review"

    return {
        "status": status,
        "source_count": len(normalized),
        "sources": normalized,
        "duplicate_source_ref_ids": sorted(set(duplicate_ids)),
        "duplicate_hashes": sorted(set(duplicate_hashes)),
        "missing_hash_source_ref_ids": sorted(set(missing_hashes)),
        "invalid_hash_source_ref_ids": sorted(set(invalid_hashes)),
    }


def build_human_pause_report(confirmations: dict[str, Any]) -> dict[str, Any]:
    pauses: list[dict[str, Any]] = []
    blockers: list[str] = []
    for pause_id in REQUIRED_HUMAN_PAUSES:
        entry = confirmations.get(pause_id)
        if not isinstance(entry, dict):
            status = "missing"
            evidence_refs: list[str] = []
            human_review_ref = None
        else:
            status = str(entry.get("status", "missing")).strip()
            evidence_refs = [
                str(ref) for ref in entry.get("evidence_refs", []) if str(ref).strip()
            ]
            human_review_ref = entry.get("human_review_ref")
        gate_status = "passed" if status in CONFIRMED_STATUSES else "blocked"
        if gate_status != "passed":
            blockers.append(f"{pause_id}:{status}")
        pauses.append(
            {
                "pause_id": pause_id,
                "status": status,
                "gate_status": gate_status,
                "human_review_ref": human_review_ref,
                "evidence_refs": evidence_refs,
            }
        )
    return {
        "status": "passed" if not blockers else "blocked",
        "pauses": pauses,
        "blockers": blockers,
    }


def build_budget_precondition_report(preconditions: dict[str, Any]) -> dict[str, Any]:
    missing = [
        key
        for key in REQUIRED_BUDGET_PRECONDITIONS
        if preconditions.get(key) is not True
    ]
    return {
        "status": "passed" if not missing else "blocked",
        "required_preconditions": list(REQUIRED_BUDGET_PRECONDITIONS),
        "missing_preconditions": missing,
    }


def classify_rejection_bucket(notice: dict[str, Any]) -> str:
    explicit_bucket = notice.get("candidate_bucket")
    if explicit_bucket in KNOWN_REJECTION_BUCKETS:
        return str(explicit_bucket)

    signals = " ".join(
        str(value)
        for value in (
            notice.get("reason_summary"),
            notice.get("carrier_reason_code"),
            notice.get("notice_title"),
        )
        if value
    ).lower()
    for bucket, keywords in REJECTION_BUCKET_KEYWORDS:
        if any(keyword in signals for keyword in keywords):
            return bucket
    return "unknown_or_new_rejection_pattern"


def build_carrier_rejection_report(
    notices: list[Any],
    source_inventory: dict[str, Any],
) -> dict[str, Any]:
    source_ids = {source["source_ref_id"] for source in source_inventory["sources"]}
    notice_records: list[dict[str, Any]] = []
    blockers: list[str] = []
    buckets_seen: set[str] = set()

    for index, raw_notice in enumerate(notices):
        notice = _require_mapping(raw_notice, "carrier_rejection_notices[]")
        notice_id = str(notice.get("notice_id") or f"notice-{index + 1}")
        source_ref_id = str(notice.get("source_ref_id", "")).strip()
        bucket = classify_rejection_bucket(notice)
        buckets_seen.add(bucket)
        source_status = "matched" if source_ref_id in source_ids else "missing"
        states = ["received_candidate"]
        if source_status == "matched" and notice.get("matched_budget_line_id"):
            states.append("reconciled_to_budget_or_invoice")
        else:
            states.append("human_review_required")

        appeal = notice.get("appeal") if isinstance(notice.get("appeal"), dict) else {}
        appeal_requested = appeal.get("requested") is True
        authorization_ref = appeal.get("human_authorization_ref")
        appeal_authorized = bool(authorization_ref)
        if appeal_requested:
            states.append(
                "appeal_authorized_by_human"
                if appeal_authorized
                else "appeal_authorization_required"
            )
        appeal_results = _require_list(
            notice.get("appeal_results", []), "appeal_results"
        )
        if appeal_results:
            states.append("appeal_result_received")
        if notice.get("financial_outcome"):
            states.append("closed_financial_outcome_recorded")
        states.append("learning_candidate_prepared")

        if source_status != "matched":
            blockers.append(f"{notice_id}:missing_source_ref")
        if appeal_requested and not appeal_authorized:
            blockers.append(f"{notice_id}:appeal_requires_human_authorization")

        notice_records.append(
            {
                "notice_id": notice_id,
                "channel": notice.get("channel", "unknown"),
                "source_ref_id": source_ref_id,
                "source_status": source_status,
                "classification_bucket": bucket,
                "classification_status": (
                    "needs_human_review"
                    if bucket == "unknown_or_new_rejection_pattern"
                    else "candidate_classified"
                ),
                "response_state_ledger_states": states,
                "appeal_requested": appeal_requested,
                "appeal_authorized": appeal_authorized,
                "human_authorization_ref": authorization_ref,
                "appeal_results_appended": [dict(result) for result in appeal_results],
                "financial_outcome": notice.get("financial_outcome"),
                "learning_candidate_status": "prepared_for_review_only",
            }
        )

    return {
        "status": "passed" if not blockers else "blocked",
        "known_bucket_set": list(KNOWN_REJECTION_BUCKETS),
        "buckets_seen": sorted(buckets_seen),
        "notices": notice_records,
        "blockers": blockers,
    }


def build_budget_actuals_variance_report(lines: list[Any]) -> dict[str, Any]:
    line_records: list[dict[str, Any]] = []
    totals = {
        "proposed_budget_amount": Decimal("0.00"),
        "carrier_compliant_projection_amount": Decimal("0.00"),
        "approved_budget_amount_if_known": Decimal("0.00"),
        "actual_billed_amount": Decimal("0.00"),
        "write_down_or_disallowed_amount": Decimal("0.00"),
    }
    phase_totals: dict[str, dict[str, Decimal]] = {}

    for index, raw_line in enumerate(lines):
        line = _require_mapping(raw_line, "budget_actual_lines[]")
        phase = str(line.get("budget_phase", "unknown")).strip() or "unknown"
        task_code = str(line.get("budget_task_code", "unknown")).strip() or "unknown"
        proposed = _money(line.get("proposed_budget_amount"), "proposed_budget_amount")
        compliant = _money(
            line.get("carrier_compliant_projection_amount"),
            "carrier_compliant_projection_amount",
        )
        approved = (
            _money(
                line.get("approved_budget_amount_if_known"),
                "approved_budget_amount_if_known",
            )
            if line.get("approved_budget_amount_if_known") not in (None, "")
            else None
        )
        actual = _money(line.get("actual_billed_amount"), "actual_billed_amount")
        write_down = _money(
            line.get("write_down_or_disallowed_amount"),
            "write_down_or_disallowed_amount",
        )

        totals["proposed_budget_amount"] += proposed
        totals["carrier_compliant_projection_amount"] += compliant
        if approved is not None:
            totals["approved_budget_amount_if_known"] += approved
        totals["actual_billed_amount"] += actual
        totals["write_down_or_disallowed_amount"] += write_down
        phase_bucket = phase_totals.setdefault(
            phase,
            {
                "proposed_budget_amount": Decimal("0.00"),
                "carrier_compliant_projection_amount": Decimal("0.00"),
                "approved_budget_amount_if_known": Decimal("0.00"),
                "actual_billed_amount": Decimal("0.00"),
                "write_down_or_disallowed_amount": Decimal("0.00"),
            },
        )
        for key, value in (
            ("proposed_budget_amount", proposed),
            ("carrier_compliant_projection_amount", compliant),
            ("actual_billed_amount", actual),
            ("write_down_or_disallowed_amount", write_down),
        ):
            phase_bucket[key] += value
        if approved is not None:
            phase_bucket["approved_budget_amount_if_known"] += approved

        line_records.append(
            {
                "line_id": str(line.get("line_id") or f"line-{index + 1}"),
                "budget_phase": phase,
                "budget_task_code": task_code,
                "proposed_budget_amount": _money_str(proposed),
                "carrier_compliant_projection_amount": _money_str(compliant),
                "approved_budget_amount_if_known": _money_str(approved),
                "actual_billed_amount": _money_str(actual),
                "write_down_or_disallowed_amount": _money_str(write_down),
                "variance_to_proposed": _money_str(actual - proposed),
                "variance_to_carrier_compliant_projection": _money_str(
                    actual - compliant
                ),
                "variance_to_approved_if_known": _money_str(
                    None if approved is None else actual - approved
                ),
                "variance_driver_candidate": line.get(
                    "variance_driver_candidate", "unknown"
                ),
            }
        )

    def serialize_totals(values: dict[str, Decimal]) -> dict[str, str]:
        result = {key: _money_str(value) for key, value in values.items()}
        result["variance_to_proposed"] = _money_str(
            values["actual_billed_amount"] - values["proposed_budget_amount"]
        )
        result["variance_to_carrier_compliant_projection"] = _money_str(
            values["actual_billed_amount"]
            - values["carrier_compliant_projection_amount"]
        )
        result["variance_to_approved_if_known"] = _money_str(
            values["actual_billed_amount"] - values["approved_budget_amount_if_known"]
        )
        return {key: str(value) for key, value in result.items() if value is not None}

    return {
        "status": "passed",
        "lines": line_records,
        "phase_totals": {
            phase: serialize_totals(values)
            for phase, values in sorted(phase_totals.items())
        },
        "totals": serialize_totals(totals),
    }


def _packet_hash(packet: dict[str, Any]) -> str:
    clean = {key: value for key, value in packet.items() if key != "packet_hash"}
    return hashlib.sha256(canonical_json(clean)).hexdigest()


def prepare_intake_owner_review_packet(request: dict[str, Any]) -> dict[str, Any]:
    validate_request_boundary(request)
    generated_at = str(request.get("generated_at") or utc_now())
    request_id = str(request.get("request_id", "intake-owner-review-request"))
    source_inventory = build_source_inventory(
        _require_list(request.get("source_refs", []), "source_refs")
    )
    human_pause_report = build_human_pause_report(
        _require_mapping(request.get("human_confirmations", {}), "human_confirmations")
    )
    budget_precondition_report = build_budget_precondition_report(
        _require_mapping(
            request.get("budget_preconditions", {}), "budget_preconditions"
        )
    )
    carrier_report = build_carrier_rejection_report(
        _require_list(
            request.get("carrier_rejection_notices", []),
            "carrier_rejection_notices",
        ),
        source_inventory,
    )
    actuals_report = build_budget_actuals_variance_report(
        _require_list(request.get("budget_actual_lines", []), "budget_actual_lines")
    )

    blockers: list[str] = []
    if source_inventory["status"] != "passed":
        blockers.append("source_inventory_gate")
    if human_pause_report["status"] != "passed":
        blockers.extend(
            f"human_pause:{item}" for item in human_pause_report["blockers"]
        )
    if budget_precondition_report["status"] != "passed":
        blockers.extend(
            f"budget_precondition:{item}"
            for item in budget_precondition_report["missing_preconditions"]
        )
    if carrier_report["status"] != "passed":
        blockers.extend(
            f"carrier_rejection:{item}" for item in carrier_report["blockers"]
        )

    # There is no promoted intake-to-budget decision model in the current seed registry.
    blockers.append("decision_model:missing_promoted_intake_to_budget_decision_model")

    lake_mode = request.get("lake_handoff_mode", "disabled")
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "packet_id": "intake_owner_packet_"
        + sha256_json(request).removeprefix("sha256:")[:16],
        "request_id": request_id,
        "generated_at": generated_at,
        "source_repo": "LawFirm-os-orchestrator",
        "source_vertical_repo": "LawFirm-os-intake",
        "workflow_label": LOCAL_WORKFLOW_LABEL,
        "synthetic": True,
        "contains_real_firm_data": False,
        "non_authoritative": True,
        "proposed_for_human_review": True,
        "not_authorized_for_client_submission": True,
        "decision_model": {
            "decision_model_id": None,
            "status": "missing_promoted_intake_to_budget_decision_model",
            "effect": "packet_may_be_reviewed_as_owner_docket_evidence_but_not_decision_ready",
        },
        "status": "blocked_pending_owner_review" if blockers else "proposed_for_review",
        "source_inventory": source_inventory,
        "human_pause_report": human_pause_report,
        "budget_precondition_report": budget_precondition_report,
        "carrier_rejection_report": carrier_report,
        "budget_actuals_variance_report": actuals_report,
        "exception_lake_handoff_preview": {
            "current_mode": lake_mode,
            "handoff_allowed": False,
            "lake_write_authority_now": False,
            "canonical_route_id_assignment": "none",
            "canonical_event_class_assignment": "none",
            "reason": "candidate owner-review packet only; Exception Lake owner contract required before admission",
        },
        "prohibited_next_steps": list(PROHIBITED_NEXT_STEPS),
        "blockers": blockers,
    }
    packet["packet_hash"] = _packet_hash(packet)
    return packet


def write_intake_owner_review_artifacts(
    *,
    packet: dict[str, Any],
    out_dir: Path,
    ledger_dir: Path,
) -> dict[str, Any]:
    packet_dir = out_dir / str(packet["packet_id"])
    write_json(packet_dir / "intake_owner_review_packet.json", packet)
    write_json(
        packet_dir / "exception_lake_handoff_preview.json",
        packet["exception_lake_handoff_preview"],
    )
    write_json(
        packet_dir / "budget_actuals_variance_report.json",
        packet["budget_actuals_variance_report"],
    )
    write_json(
        packet_dir / "carrier_rejection_report.json",
        packet["carrier_rejection_report"],
    )
    ledger_path = ledger_dir / "intake_owner_review.jsonl"
    JsonlLedgerWriter(ledger_path).append(
        {
            "ledger_version": "1",
            "command_name": "intake prepare-owner-packet",
            "packet_id": packet["packet_id"],
            "request_id": packet["request_id"],
            "workflow_label": packet["workflow_label"],
            "status": packet["status"],
            "synthetic": True,
            "non_authoritative": True,
            "lake_handoff_allowed": False,
            "timestamp": packet["generated_at"],
            "packet_hash": packet["packet_hash"],
        }
    )
    summary = {
        "status": packet["status"],
        "packet_id": packet["packet_id"],
        "packet_hash": packet["packet_hash"],
        "packet_path": str(packet_dir / "intake_owner_review_packet.json"),
        "ledger_path": str(ledger_path),
        "lake_handoff_allowed": False,
        "not_authorized_for_client_submission": True,
        "blocker_count": len(packet["blockers"]),
    }
    write_json(packet_dir / "stdout_summary.json", summary)
    return summary
