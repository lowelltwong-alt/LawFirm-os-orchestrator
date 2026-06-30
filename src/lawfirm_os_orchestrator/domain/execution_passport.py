"""ExecutionPassport (PR-04). Substrate schema: execution-passport-v1."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from lawfirm_os_orchestrator.util.hashing import canonical_json


SCHEMA_VERSION = "execution_passport.v1"


@dataclass(frozen=True)
class ExecutionPassport:
    schema_version: str
    execution_passport_id: str
    execution_decision_hash: str
    execution_request_hash: str
    context_bundle_hash: str
    contract_surface_sha256: str
    run_id: str
    granted_at: str
    expires_at: str
    allowed_action: str
    allowed_tool_id: str
    allowed_route_id: str
    allowed_event_class: str
    allowed_side_effect_class: str
    single_use: bool
    execution_passport_hash: str
    issuer: str | None = None


def execution_passport_hash(payload: dict[str, Any]) -> str:
    clean = {k: v for k, v in payload.items() if k != "execution_passport_hash"}
    return hashlib.sha256(canonical_json(clean)).hexdigest()


def build_execution_passport(
    *,
    execution_passport_id: str,
    execution_decision_hash: str,
    execution_request_hash: str,
    context_bundle_hash: str,
    contract_surface_sha256: str,
    run_id: str,
    granted_at: str,
    expires_at: str,
    allowed_action: str,
    allowed_tool_id: str,
    allowed_route_id: str,
    allowed_event_class: str,
    allowed_side_effect_class: str,
    issuer: str | None = None,
) -> ExecutionPassport:
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "execution_passport_id": execution_passport_id,
        "execution_decision_hash": execution_decision_hash,
        "execution_request_hash": execution_request_hash,
        "context_bundle_hash": context_bundle_hash,
        "contract_surface_sha256": contract_surface_sha256,
        "run_id": run_id,
        "granted_at": granted_at,
        "expires_at": expires_at,
        "allowed_action": allowed_action,
        "allowed_tool_id": allowed_tool_id,
        "allowed_route_id": allowed_route_id,
        "allowed_event_class": allowed_event_class,
        "allowed_side_effect_class": allowed_side_effect_class,
        "single_use": True,
    }
    if issuer:
        payload["issuer"] = issuer
    digest = execution_passport_hash(payload)
    return ExecutionPassport(
        schema_version=SCHEMA_VERSION,
        execution_passport_id=execution_passport_id,
        execution_decision_hash=execution_decision_hash,
        execution_request_hash=execution_request_hash,
        context_bundle_hash=context_bundle_hash,
        contract_surface_sha256=contract_surface_sha256,
        run_id=run_id,
        granted_at=granted_at,
        expires_at=expires_at,
        allowed_action=allowed_action,
        allowed_tool_id=allowed_tool_id,
        allowed_route_id=allowed_route_id,
        allowed_event_class=allowed_event_class,
        allowed_side_effect_class=allowed_side_effect_class,
        single_use=True,
        execution_passport_hash=digest,
        issuer=issuer,
    )
