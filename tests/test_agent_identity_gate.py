from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from lawfirm_os_orchestrator.domain.agent_controls import AgentIdentity
from lawfirm_os_orchestrator.policy.agent_hostile_controls import agent_identity_gate


def test_agent_identity_requires_scope() -> None:
    now = datetime.now(tz=UTC)
    with pytest.raises(ValueError, match="route_scope"):
        AgentIdentity(
            agent_instance_id="agent:test",
            tenant_id="tenant.synthetic",
            route_scope=(),
            tool_scope=("orchestrator.tool.synthetic_classify_exception.v1",),
            data_scope=("synthetic_exception_input",),
            issued_at=now,
            expires_at=now + timedelta(hours=1),
        )


def test_agent_identity_gate_records_actor_scope() -> None:
    now = datetime.now(tz=UTC)
    actor = AgentIdentity(
        agent_instance_id="agent:test",
        delegating_user_id="user:reviewer",
        tenant_id="tenant.synthetic",
        route_scope=("route.workflow_escalation.v1",),
        tool_scope=("orchestrator.tool.synthetic_classify_exception.v1",),
        data_scope=("synthetic_exception_input",),
        issued_at=now,
        expires_at=now + timedelta(hours=1),
    )

    decision = agent_identity_gate("run:test", actor)

    assert decision.result == "pass"
    assert decision.details["delegating_user_id"] == "user:reviewer"
    assert decision.details["tenant_id"] == "tenant.synthetic"
    assert decision.details["route_scope"] == ["route.workflow_escalation.v1"]
