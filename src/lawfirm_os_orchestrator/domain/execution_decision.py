"""ExecutionDecision (PR-04). Substrate schema: execution-decision-v1."""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Any

from lawfirm_os_orchestrator.util.hashing import canonical_json


SCHEMA_VERSION = "execution_decision.v1"
DECISIONS = {"allowed", "denied", "requires_approval"}


@dataclass(frozen=True)
class PolicyRef:
    policy_id: str
    policy_version: str | None = None


@dataclass(frozen=True)
class ExecutionDecision:
    schema_version: str
    execution_decision_id: str
    execution_request_hash: str
    context_bundle_hash: str
    contract_surface_sha256: str
    run_id: str
    decided_at: str
    decision: str
    reason_code: str
    evaluator: str
    policy_ref: PolicyRef
    execution_decision_hash: str
    requires_human_approval: bool = False
    denial_explanation_hash: str | None = None

    def to_payload(self) -> dict[str, Any]:
        d = asdict(self)
        if d["denial_explanation_hash"] is None:
            d.pop("denial_explanation_hash")
        if d["policy_ref"].get("policy_version") is None:
            d["policy_ref"].pop("policy_version", None)
        return d


def execution_decision_hash(payload: dict[str, Any]) -> str:
    clean = {k: v for k, v in payload.items() if k != "execution_decision_hash"}
    return hashlib.sha256(canonical_json(clean)).hexdigest()


def build_execution_decision(
    *,
    execution_decision_id: str,
    execution_request_hash: str,
    context_bundle_hash: str,
    contract_surface_sha256: str,
    run_id: str,
    decided_at: str,
    decision: str,
    reason_code: str,
    evaluator: str,
    policy_ref: PolicyRef,
    requires_human_approval: bool = False,
    denial_explanation_hash: str | None = None,
) -> ExecutionDecision:
    if decision not in DECISIONS:
        raise ValueError(f"unknown decision: {decision}")
    if decision == "denied" and not denial_explanation_hash:
        raise ValueError("denied decisions require denial_explanation_hash")
    if decision == "requires_approval" and not requires_human_approval:
        raise ValueError("requires_approval decisions must set requires_human_approval=True")
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "execution_decision_id": execution_decision_id,
        "execution_request_hash": execution_request_hash,
        "context_bundle_hash": context_bundle_hash,
        "contract_surface_sha256": contract_surface_sha256,
        "run_id": run_id,
        "decided_at": decided_at,
        "decision": decision,
        "reason_code": reason_code,
        "evaluator": evaluator,
        "policy_ref": {"policy_id": policy_ref.policy_id, **({"policy_version": policy_ref.policy_version} if policy_ref.policy_version else {})},
        "requires_human_approval": requires_human_approval,
    }
    if denial_explanation_hash:
        payload["denial_explanation_hash"] = denial_explanation_hash
    digest = execution_decision_hash(payload)
    return ExecutionDecision(
        schema_version=SCHEMA_VERSION,
        execution_decision_id=execution_decision_id,
        execution_request_hash=execution_request_hash,
        context_bundle_hash=context_bundle_hash,
        contract_surface_sha256=contract_surface_sha256,
        run_id=run_id,
        decided_at=decided_at,
        decision=decision,
        reason_code=reason_code,
        evaluator=evaluator,
        policy_ref=policy_ref,
        execution_decision_hash=digest,
        requires_human_approval=requires_human_approval,
        denial_explanation_hash=denial_explanation_hash,
    )
