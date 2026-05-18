"""ExecutionResult (PR-04). Substrate schema: execution-result-v1."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from lawfirm_os_orchestrator.util.hashing import canonical_json


SCHEMA_VERSION = "execution_result.v1"
STATUSES = {"succeeded", "failed", "denied", "quarantined"}


@dataclass(frozen=True)
class ExecutionResult:
    schema_version: str
    execution_result_id: str
    execution_request_hash: str
    execution_decision_hash: str
    context_bundle_hash: str
    contract_surface_sha256: str
    run_id: str
    started_at: str
    ended_at: str
    status: str
    execution_result_hash: str
    execution_passport_hash: str | None = None
    result_payload_hash: str | None = None
    error_reason_code: str | None = None


def execution_result_hash(payload: dict[str, Any]) -> str:
    clean = {k: v for k, v in payload.items() if k != "execution_result_hash"}
    return hashlib.sha256(canonical_json(clean)).hexdigest()


def build_execution_result(
    *,
    execution_result_id: str,
    execution_request_hash: str,
    execution_decision_hash: str,
    context_bundle_hash: str,
    contract_surface_sha256: str,
    run_id: str,
    started_at: str,
    ended_at: str,
    status: str,
    execution_passport_hash: str | None = None,
    result_payload_hash: str | None = None,
    error_reason_code: str | None = None,
) -> ExecutionResult:
    if status not in STATUSES:
        raise ValueError(f"unknown status: {status}")
    if status == "succeeded" and not (execution_passport_hash and result_payload_hash):
        raise ValueError("succeeded results require execution_passport_hash and result_payload_hash")
    if status == "failed" and not (execution_passport_hash and error_reason_code):
        raise ValueError("failed results require execution_passport_hash and error_reason_code")
    if status == "denied" and not error_reason_code:
        raise ValueError("denied results require error_reason_code")
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "execution_result_id": execution_result_id,
        "execution_request_hash": execution_request_hash,
        "execution_decision_hash": execution_decision_hash,
        "context_bundle_hash": context_bundle_hash,
        "contract_surface_sha256": contract_surface_sha256,
        "run_id": run_id,
        "started_at": started_at,
        "ended_at": ended_at,
        "status": status,
    }
    if execution_passport_hash:
        payload["execution_passport_hash"] = execution_passport_hash
    if result_payload_hash:
        payload["result_payload_hash"] = result_payload_hash
    if error_reason_code:
        payload["error_reason_code"] = error_reason_code
    digest = execution_result_hash(payload)
    return ExecutionResult(
        schema_version=SCHEMA_VERSION,
        execution_result_id=execution_result_id,
        execution_request_hash=execution_request_hash,
        execution_decision_hash=execution_decision_hash,
        context_bundle_hash=context_bundle_hash,
        contract_surface_sha256=contract_surface_sha256,
        run_id=run_id,
        started_at=started_at,
        ended_at=ended_at,
        status=status,
        execution_passport_hash=execution_passport_hash,
        result_payload_hash=result_payload_hash,
        error_reason_code=error_reason_code,
        execution_result_hash=digest,
    )
