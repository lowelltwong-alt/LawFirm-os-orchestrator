from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field, model_validator

from lawfirm_os_orchestrator.domain.models import StrictModel


class AgentIdentity(StrictModel):
    """Execution-plane identity proof for an agent-scoped action."""

    agent_instance_id: str = Field(min_length=1)
    actor_type: Literal["agent"] = "agent"
    agent_type: Literal["classifier", "drafter", "reviewer_helper", "tool_worker"] = "classifier"
    delegating_user_id: str | None = None
    tenant_id: str = Field(min_length=1)
    matter_scope: tuple[str, ...] = ()
    route_scope: tuple[str, ...] = Field(min_length=1)
    tool_scope: tuple[str, ...] = Field(min_length=1)
    data_scope: tuple[str, ...] = Field(min_length=1)
    issued_at: datetime
    expires_at: datetime
    approval_ref: str | None = None

    @model_validator(mode="after")
    def enforce_valid_window(self) -> "AgentIdentity":
        if self.expires_at <= self.issued_at:
            raise ValueError("agent identity expires_at must be after issued_at")
        return self


class RevocationState(StrictModel):
    agent_instance_id: str
    revoked: bool = False
    revoked_at: datetime | None = None
    revoked_by: str | None = None
    reason: str | None = None
    blocked_routes: tuple[str, ...] = ()
    blocked_tools: tuple[str, ...] = ()


class PromptVersionRef(StrictModel):
    prompt_ref: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)
    prompt_sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    approved: bool
    approved_by: str | None = None
    approved_at: datetime | None = None
    policy_bundle_id: str = Field(min_length=1)
    prompt_file: str = Field(min_length=1)


class ToolAuthoritySpec(StrictModel):
    tool_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    risk_class: Literal["read", "transform", "draft", "write", "execute"]
    input_schema_ref: str = Field(min_length=1)
    output_schema_ref: str = Field(min_length=1)
    allowed_actor_types: tuple[Literal["human", "agent", "system"], ...] = Field(min_length=1)
    auth_required: bool
    agent_identity_required: bool
    audit_event_required: bool
    approval_required: bool
    idempotency_required: bool
    data_domains: tuple[str, ...] = Field(min_length=1)
    timeout_seconds: int = Field(gt=0)
    retry_policy_ref: str = Field(min_length=1)


class AuthzDecision(StrictModel):
    decision_id: str
    run_id: str
    gate: str
    result: Literal["pass", "deny"]
    reason_code: str
    actor_id: str
    scope_hash: str
    evaluated_at: datetime
    policy_ref: str
    evidence_ref: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class PolicyDenied(RuntimeError):
    def __init__(self, decision: AuthzDecision):
        self.decision = decision
        super().__init__(f"{decision.gate} denied action: {decision.reason_code}")
