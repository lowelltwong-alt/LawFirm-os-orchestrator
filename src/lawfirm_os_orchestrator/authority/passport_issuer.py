"""Passport issuer (PR-04). Only emits a passport when the decision is allowed.

Denied and requires_approval decisions DO NOT receive a passport. The caller is
expected to record the Decision and (when required) drive the approval flow.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from lawfirm_os_orchestrator.domain.execution_decision import ExecutionDecision
from lawfirm_os_orchestrator.domain.execution_passport import (
    ExecutionPassport,
    build_execution_passport,
)
from lawfirm_os_orchestrator.domain.execution_request import ExecutionRequest


DEFAULT_PASSPORT_TTL = timedelta(minutes=15)


class PassportRefused(RuntimeError):
    """Raised when a passport is requested for a decision that did not allow."""


def _iso_utc_now() -> datetime:
    return datetime.now(tz=UTC)


def issue_passport(
    *,
    decision: ExecutionDecision,
    request: ExecutionRequest,
    execution_passport_id: str | None = None,
    granted_at: datetime | None = None,
    ttl: timedelta = DEFAULT_PASSPORT_TTL,
    issuer: str = "orchestrator.passport_issuer.v1",
) -> ExecutionPassport:
    if decision.decision != "allowed":
        raise PassportRefused(
            f"cannot issue passport: decision is {decision.decision!r}; passport may only be issued for an allowed decision"
        )
    granted = granted_at or _iso_utc_now()
    expires = granted + ttl
    return build_execution_passport(
        execution_passport_id=execution_passport_id or f"passport-{granted.isoformat().replace('+00:00','Z')}",
        execution_decision_hash=decision.execution_decision_hash,
        execution_request_hash=request.execution_request_hash,
        context_bundle_hash=request.context_bundle_hash,
        contract_surface_sha256=request.contract_surface_sha256,
        run_id=request.run_id,
        granted_at=granted.isoformat().replace("+00:00", "Z"),
        expires_at=expires.isoformat().replace("+00:00", "Z"),
        allowed_action=request.requested_action,
        allowed_tool_id=request.requested_tool_id,
        allowed_route_id=request.requested_route_id,
        allowed_event_class=request.requested_event_class,
        allowed_side_effect_class=request.requested_side_effect_class,
        issuer=issuer,
    )
