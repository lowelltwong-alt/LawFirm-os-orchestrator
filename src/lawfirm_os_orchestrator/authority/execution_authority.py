"""ExecutionAuthority: deterministic evaluator that maps ExecutionRequest -> ExecutionDecision (PR-04, hardened in PR-05.5).

The evaluator is config-driven. Substrate registries (ai-front-door,
tool-authority) provide the source-of-truth allow-lists in production.
Tests inject an in-memory AuthorityConfig.

Reason codes and the semantic-mutation deny-list are imported from
``lawfirm_os_orchestrator.substrate.reason_codes`` which loads them
fail-closed from substrate's runtime-reason-codes-registry.json. No string
literals for these enums appear in this module.

Decision rules (in order):
  1. unknown tool_id              -> denied (UNKNOWN_TOOL)
  2. unknown route_id             -> denied (UNKNOWN_ROUTE)
  3. unknown event_class          -> denied (UNKNOWN_EVENT_CLASS)
  4. semantic_mutation action     -> denied (SEMANTIC_MUTATION_FORBIDDEN)
  5. side_effect_class=external   -> denied (EXTERNAL_WRITES_FORBIDDEN_IN_MVP)
  6. side_effect_class=write AND requires_approval -> requires_approval (WRITE_REQUIRES_HUMAN_APPROVAL)
  7. side_effect_class=write      -> denied (WRITE_REQUIRES_EXPLICIT_APPROVAL_POLICY)
  8. side_effect_class in {none, read} -> allowed (ALLOWED_UNDER_AUTHORITY_POLICY)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from lawfirm_os_orchestrator.domain.execution_decision import (
    ExecutionDecision,
    PolicyRef,
    build_execution_decision,
)
from lawfirm_os_orchestrator.domain.execution_request import ExecutionRequest
from lawfirm_os_orchestrator.substrate.reason_codes import (
    ALLOWED_UNDER_AUTHORITY_POLICY,
    EXTERNAL_WRITES_FORBIDDEN_IN_MVP,
    SEMANTIC_MUTATION_ACTIONS,
    SEMANTIC_MUTATION_FORBIDDEN,
    UNKNOWN_EVENT_CLASS,
    UNKNOWN_ROUTE,
    UNKNOWN_TOOL,
    WRITE_REQUIRES_EXPLICIT_APPROVAL_POLICY,
    WRITE_REQUIRES_HUMAN_APPROVAL,
)


@dataclass(frozen=True)
class AuthorityConfig:
    allowed_tool_ids: frozenset[str]
    allowed_route_ids: frozenset[str]
    allowed_event_classes: frozenset[str]
    write_actions_with_approval: frozenset[str] = field(default_factory=frozenset)
    policy_id: str = "lawfirm-os-execution-authority.v1"
    policy_version: str = "v1"
    evaluator_id: str = "orchestrator.execution_authority.v1"


def _iso_utc_now() -> str:
    return datetime.now(tz=UTC).isoformat().replace("+00:00", "Z")


def _id_counter() -> str:
    return _iso_utc_now()


def evaluate(
    request: ExecutionRequest,
    *,
    config: AuthorityConfig,
    decided_at: str | None = None,
    execution_decision_id: str | None = None,
    denial_explanation_hash_for: dict[str, str] | None = None,
) -> ExecutionDecision:
    """Pure evaluator. Returns an ExecutionDecision for every request, including denied."""
    denial_hashes = denial_explanation_hash_for or {}
    decided_at = decided_at or _iso_utc_now()
    execution_decision_id = execution_decision_id or f"decision-{_id_counter()}"
    policy_ref = PolicyRef(policy_id=config.policy_id, policy_version=config.policy_version)

    def _deny(reason: str) -> ExecutionDecision:
        explanation = denial_hashes.get(reason, "0" * 64)
        return build_execution_decision(
            execution_decision_id=execution_decision_id,
            execution_request_hash=request.execution_request_hash,
            context_bundle_hash=request.context_bundle_hash,
            contract_surface_sha256=request.contract_surface_sha256,
            run_id=request.run_id,
            decided_at=decided_at,
            decision="denied",
            reason_code=reason,
            evaluator=config.evaluator_id,
            policy_ref=policy_ref,
            denial_explanation_hash=explanation,
        )

    def _allow() -> ExecutionDecision:
        return build_execution_decision(
            execution_decision_id=execution_decision_id,
            execution_request_hash=request.execution_request_hash,
            context_bundle_hash=request.context_bundle_hash,
            contract_surface_sha256=request.contract_surface_sha256,
            run_id=request.run_id,
            decided_at=decided_at,
            decision="allowed",
            reason_code=ALLOWED_UNDER_AUTHORITY_POLICY,
            evaluator=config.evaluator_id,
            policy_ref=policy_ref,
        )

    def _requires_approval(reason: str) -> ExecutionDecision:
        return build_execution_decision(
            execution_decision_id=execution_decision_id,
            execution_request_hash=request.execution_request_hash,
            context_bundle_hash=request.context_bundle_hash,
            contract_surface_sha256=request.contract_surface_sha256,
            run_id=request.run_id,
            decided_at=decided_at,
            decision="requires_approval",
            reason_code=reason,
            evaluator=config.evaluator_id,
            policy_ref=policy_ref,
            requires_human_approval=True,
        )

    if request.requested_tool_id not in config.allowed_tool_ids:
        return _deny(UNKNOWN_TOOL)
    if request.requested_route_id not in config.allowed_route_ids:
        return _deny(UNKNOWN_ROUTE)
    if request.requested_event_class not in config.allowed_event_classes:
        return _deny(UNKNOWN_EVENT_CLASS)
    if request.requested_action in SEMANTIC_MUTATION_ACTIONS:
        return _deny(SEMANTIC_MUTATION_FORBIDDEN)
    if request.requested_side_effect_class == "external":
        return _deny(EXTERNAL_WRITES_FORBIDDEN_IN_MVP)
    if request.requested_side_effect_class == "write":
        if request.requested_action in config.write_actions_with_approval:
            return _requires_approval(WRITE_REQUIRES_HUMAN_APPROVAL)
        return _deny(WRITE_REQUIRES_EXPLICIT_APPROVAL_POLICY)
    # side_effect_class in {none, read}
    return _allow()
