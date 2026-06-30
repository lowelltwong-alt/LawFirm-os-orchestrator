#!/usr/bin/env python3
"""Validate the candidate Orchestrator intake adoption review docket."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "registry" / "intake-orchestrator-adoption-review-registry.json"
EXPECTED_SOURCE_PROPOSAL_IDS = {
    "orchestrator.workflow-human-pauses-evidence-packet.v0_1",
    "orchestrator.carrier-rejection-capture-appeal.v0_1",
}
REQUIRED_PROHIBITED_ACTIONS = {
    "canonical_route_id_creation",
    "canonical_event_class_creation",
    "semantic_substrate_write",
    "exception_lake_write",
    "production_connector_write",
    "real_data_ingestion",
    "appeal_submission_without_human_authorization",
}
REQUIRED_WORKFLOW_GATES = {
    "source_inventory_gate",
    "human_confirmation_pause",
    "budget_precondition_gate",
    "evidence_packet_assembly_gate",
    "run_ledger_integrity_gate",
    "lake_handoff_gate",
}
REQUIRED_CARRIER_GATES = {
    "source_authenticity_gate",
    "response_state_reconciliation_gate",
    "human_rejection_review_pause",
    "appeal_authorization_gate",
    "appeal_result_capture_gate",
    "budget_actuals_comparison_gate",
    "lake_handoff_gate",
}
REQUIRED_CARRIER_BUCKETS = {
    "rate_or_cap_rejection",
    "staffing_or_leverage_rejection",
    "task_scope_rejection",
    "expense_documentation_rejection",
    "preapproval_missing",
    "duplicate_or_format_rejection",
    "timing_or_deadline_rejection",
    "portal_technical_rejection",
    "identity_or_matter_mismatch",
    "actuals_or_invoice_variance",
    "unknown_or_new_rejection_pattern",
}
REQUIRED_LEARNING_INPUTS = {
    "carrier_rejection_notice",
    "human_rejection_review_outcome",
    "appeal_result",
    "financial_outcome",
    "budget_actual_variance",
    "new_rejection_pattern_candidate",
}


class IntakeOrchestratorAdoptionReviewError(ValueError):
    """Raised when the candidate review docket violates Orchestrator boundaries."""


def _rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IntakeOrchestratorAdoptionReviewError(
            f"{_rel(path)} unreadable: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise IntakeOrchestratorAdoptionReviewError(
            f"{_rel(path)} must be a JSON object"
        )
    return data


def _require_bool(data: dict[str, Any], key: str, expected: bool, label: str) -> None:
    if data.get(key) is not expected:
        raise IntakeOrchestratorAdoptionReviewError(f"{label}.{key} must be {expected}")


def _require_string_list(data: dict[str, Any], key: str, label: str) -> list[str]:
    value = data.get(key)
    if not isinstance(value, list) or not value:
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.{key} must be a non-empty list"
        )
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.{key} must contain only non-empty strings"
        )
    return value


def _validate_top_level(data: dict[str, Any], label: str) -> None:
    expected = {
        "schema_version": "intake_orchestrator_adoption_review_registry.v0_1",
        "object_type": "intake_orchestrator_adoption_review_registry",
        "status": "candidate_review_only",
        "owner_repo": "LawFirm-os-orchestrator",
        "source_repo": "LawFirm-os-intake",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise IntakeOrchestratorAdoptionReviewError(
                f"{label}.{key} must be {value!r}"
            )

    _require_bool(data, "contains_real_firm_data", False, label)
    _require_bool(data, "non_authoritative", True, label)
    _require_bool(data, "direct_promotion_performed", False, label)
    _require_bool(data, "external_writes_performed", False, label)
    _require_bool(data, "no_canonical_route_or_event_class_authority", True, label)
    _require_bool(data, "no_runtime_connector_authority", True, label)
    _require_bool(data, "no_exception_lake_write_authority", True, label)

    generated = set(_require_string_list(data, "generated_from_proposal_ids", label))
    if generated != EXPECTED_SOURCE_PROPOSAL_IDS:
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.generated_from_proposal_ids must be {sorted(EXPECTED_SOURCE_PROPOSAL_IDS)}"
        )


def _validate_lake_policy(item: dict[str, Any], label: str) -> None:
    policy = item.get("exception_lake_handoff_policy")
    if not isinstance(policy, dict):
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.exception_lake_handoff_policy must be an object"
        )
    if policy.get("current_mode") != "disabled_or_validate_only":
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.current_mode must stay guarded"
        )
    if policy.get("canonical_route_id_assignment") != "none":
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label} must not assign a canonical route_id"
        )
    if policy.get("canonical_event_class_assignment") != "none":
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label} must not assign a canonical event_class"
        )
    if policy.get("lake_write_authority_now") is not False:
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.lake_write_authority_now must be false"
        )


def _validate_common_item(item: dict[str, Any], label: str) -> None:
    if item.get("target_repo") != "LawFirm-os-orchestrator":
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.target_repo must be Orchestrator"
        )
    if item.get("authority_plane") != "execution":
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.authority_plane must be execution"
        )
    if item.get("adoption_status") != "owner_review_required":
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.adoption_status must be owner_review_required"
        )

    local_label = item.get("local_workflow_label")
    if not isinstance(local_label, str) or not local_label.startswith(
        "orchestrator.local."
    ):
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.local_workflow_label must be a local Orchestrator label"
        )
    if local_label.startswith("route."):
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.local_workflow_label must not look like a canonical route_id"
        )

    proposed_refs = _require_string_list(item, "proposed_contract_refs", label)
    invalid_refs = [
        ref for ref in proposed_refs if not ref.startswith("orchestrator://candidate/")
    ]
    if invalid_refs:
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.proposed_contract_refs must stay candidate-only: {invalid_refs}"
        )

    prohibited = set(_require_string_list(item, "prohibited_actions", label))
    missing_prohibited = sorted(REQUIRED_PROHIBITED_ACTIONS - prohibited)
    if missing_prohibited:
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.prohibited_actions missing {missing_prohibited}"
        )

    _require_bool(item, "non_authoritative", True, label)
    _require_bool(item, "direct_promotion_performed", False, label)
    _require_bool(item, "external_writes_performed", False, label)
    _validate_lake_policy(item, label)


def _validate_workflow_item(item: dict[str, Any], label: str) -> None:
    gates = set(_require_string_list(item, "required_orchestrator_gates", label))
    missing_gates = sorted(REQUIRED_WORKFLOW_GATES - gates)
    if missing_gates:
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.required_orchestrator_gates missing {missing_gates}"
        )
    pauses = set(_require_string_list(item, "required_human_pauses", label))
    if "confirm_principal_party_roles" not in pauses:
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label} must require principal party role confirmation"
        )


def _validate_carrier_item(item: dict[str, Any], label: str) -> None:
    gates = set(_require_string_list(item, "required_orchestrator_gates", label))
    missing_gates = sorted(REQUIRED_CARRIER_GATES - gates)
    if missing_gates:
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.required_orchestrator_gates missing {missing_gates}"
        )

    channels = item.get("capture_channels")
    if not isinstance(channels, list) or not channels:
        raise IntakeOrchestratorAdoptionReviewError(f"{label}.capture_channels missing")
    channel_names = {
        entry.get("channel") for entry in channels if isinstance(entry, dict)
    }
    if channel_names != {"email", "carrier_portal"}:
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.capture_channels must include email and carrier_portal"
        )
    if any(
        entry.get("enabled_now") is not False
        for entry in channels
        if isinstance(entry, dict)
    ):
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.capture_channels must not enable production capture now"
        )

    buckets = set(
        _require_string_list(item, "candidate_rejection_classification_buckets", label)
    )
    missing_buckets = sorted(REQUIRED_CARRIER_BUCKETS - buckets)
    if missing_buckets:
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.candidate_rejection_classification_buckets missing {missing_buckets}"
        )

    states = set(
        _require_string_list(item, "required_response_state_ledger_states", label)
    )
    if "appeal_result_received" not in states:
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label} must capture appeal result receipt"
        )
    if "closed_financial_outcome_recorded" not in states:
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label} must capture final financial outcome"
        )

    learning_inputs = set(_require_string_list(item, "learning_loop_inputs", label))
    missing_inputs = sorted(REQUIRED_LEARNING_INPUTS - learning_inputs)
    if missing_inputs:
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.learning_loop_inputs missing {missing_inputs}"
        )

    actuals_inputs = set(
        _require_string_list(item, "budget_actuals_comparison_inputs", label)
    )
    if (
        not {"budget_phase", "actual_billed_amount", "variance_driver_candidate"}
        <= actuals_inputs
    ):
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.budget_actuals_comparison_inputs must support phase actuals"
        )


def validate_intake_orchestrator_adoption_review(
    path: Path = REGISTRY,
) -> dict[str, Any]:
    data = _read_json(path)
    label = _rel(path)
    _validate_top_level(data, label)

    items = data.get("review_items")
    if not isinstance(items, list) or len(items) != len(EXPECTED_SOURCE_PROPOSAL_IDS):
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.review_items must contain exactly {len(EXPECTED_SOURCE_PROPOSAL_IDS)} items"
        )

    seen = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise IntakeOrchestratorAdoptionReviewError(
                f"{label}.review_items[{index}] must be an object"
            )
        item_label = f"{label}.review_items[{index}]"
        proposal_id = item.get("source_proposal_id")
        if proposal_id not in EXPECTED_SOURCE_PROPOSAL_IDS:
            raise IntakeOrchestratorAdoptionReviewError(
                f"{item_label}.source_proposal_id is not expected: {proposal_id!r}"
            )
        seen.add(proposal_id)
        _validate_common_item(item, item_label)
        if proposal_id == "orchestrator.workflow-human-pauses-evidence-packet.v0_1":
            _validate_workflow_item(item, item_label)
        elif proposal_id == "orchestrator.carrier-rejection-capture-appeal.v0_1":
            _validate_carrier_item(item, item_label)

    if seen != EXPECTED_SOURCE_PROPOSAL_IDS:
        raise IntakeOrchestratorAdoptionReviewError(
            f"{label}.review_items missing {sorted(EXPECTED_SOURCE_PROPOSAL_IDS - seen)}"
        )
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    args = parser.parse_args(argv)

    try:
        validate_intake_orchestrator_adoption_review(args.registry)
    except IntakeOrchestratorAdoptionReviewError as exc:
        print(
            f"Intake Orchestrator adoption review validation failed: {exc}",
            file=sys.stderr,
        )
        return 1
    print("Intake Orchestrator adoption review validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
