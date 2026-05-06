from __future__ import annotations

from lawfirm_os_orchestrator.domain.models import ClassificationResult, SyntheticExceptionInput, ValidationResult
from lawfirm_os_orchestrator.substrate.reader import SubstrateSnapshot


def preflight_policy(event: SyntheticExceptionInput) -> ValidationResult:
    # Pydantic already enforces the hard checks; this record exists for evidence.
    return ValidationResult(validator="synthetic_only_policy", status="pass", reason="synthetic input accepted")


def validate_classification(result: ClassificationResult, snapshot: SubstrateSnapshot) -> list[ValidationResult]:
    validations: list[ValidationResult] = []
    if result.route_id not in snapshot.allowed_route_ids:
        validations.append(ValidationResult(validator="route_registry_check", status="fail", reason=f"unknown route_id: {result.route_id}"))
    else:
        validations.append(ValidationResult(validator="route_registry_check", status="pass"))

    expected_event_class = snapshot.event_class_for_route(result.route_id)
    if result.event_class not in snapshot.allowed_event_classes:
        validations.append(ValidationResult(validator="event_class_registry_check", status="fail", reason=f"unknown event_class: {result.event_class}"))
    elif expected_event_class and result.event_class != expected_event_class:
        validations.append(ValidationResult(validator="route_event_pair_check", status="fail", reason="route_id and event_class pairing is not allowed"))
    else:
        validations.append(ValidationResult(validator="route_event_pair_check", status="pass"))

    if not result.supporting_claim_refs:
        validations.append(ValidationResult(validator="evidence_completeness", status="fail", reason="missing supporting claim refs"))
    else:
        validations.append(ValidationResult(validator="evidence_completeness", status="pass"))
    return validations


def fail_reasons(validations: list[ValidationResult]) -> list[str]:
    return [v.reason or v.validator for v in validations if v.status == "fail"]
