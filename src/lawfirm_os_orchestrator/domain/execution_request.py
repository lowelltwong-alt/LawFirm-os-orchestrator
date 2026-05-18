"""ExecutionRequest (PR-04). Substrate schema: execution-request-v1."""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Any

from lawfirm_os_orchestrator.util.hashing import canonical_json


SCHEMA_VERSION = "execution_request.v1"
SIDE_EFFECT_CLASSES = {"none", "read", "write", "external"}


@dataclass(frozen=True)
class ExecutionRequest:
    schema_version: str
    execution_request_id: str
    context_bundle_hash: str
    contract_surface_sha256: str
    run_id: str
    requested_at: str
    requested_action: str
    requested_tool_id: str
    requested_route_id: str
    requested_event_class: str
    requested_side_effect_class: str
    request_payload_hash: str
    execution_request_hash: str
    requester: str | None = None

    def to_payload(self) -> dict[str, Any]:
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}


def execution_request_hash(payload: dict[str, Any]) -> str:
    """Bare-hex SHA-256 of canonical-JSON payload with execution_request_hash excluded."""
    clean = {k: v for k, v in payload.items() if k != "execution_request_hash"}
    return hashlib.sha256(canonical_json(clean)).hexdigest()


def build_execution_request(
    *,
    execution_request_id: str,
    context_bundle_hash: str,
    contract_surface_sha256: str,
    run_id: str,
    requested_at: str,
    requested_action: str,
    requested_tool_id: str,
    requested_route_id: str,
    requested_event_class: str,
    requested_side_effect_class: str,
    request_payload_hash: str,
    requester: str | None = None,
) -> ExecutionRequest:
    if requested_side_effect_class not in SIDE_EFFECT_CLASSES:
        raise ValueError(f"unknown side_effect_class: {requested_side_effect_class}")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "execution_request_id": execution_request_id,
        "context_bundle_hash": context_bundle_hash,
        "contract_surface_sha256": contract_surface_sha256,
        "run_id": run_id,
        "requested_at": requested_at,
        "requested_action": requested_action,
        "requested_tool_id": requested_tool_id,
        "requested_route_id": requested_route_id,
        "requested_event_class": requested_event_class,
        "requested_side_effect_class": requested_side_effect_class,
        "request_payload_hash": request_payload_hash,
    }
    if requester:
        payload["requester"] = requester
    digest = execution_request_hash(payload)
    return ExecutionRequest(
        schema_version=SCHEMA_VERSION,
        execution_request_id=execution_request_id,
        context_bundle_hash=context_bundle_hash,
        contract_surface_sha256=contract_surface_sha256,
        run_id=run_id,
        requested_at=requested_at,
        requested_action=requested_action,
        requested_tool_id=requested_tool_id,
        requested_route_id=requested_route_id,
        requested_event_class=requested_event_class,
        requested_side_effect_class=requested_side_effect_class,
        request_payload_hash=request_payload_hash,
        execution_request_hash=digest,
        requester=requester,
    )
