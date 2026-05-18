"""Tests for the PR-04 execution authority + passport + preflight chain."""
from __future__ import annotations

import pytest

from lawfirm_os_orchestrator.authority.execution_authority import (
    AuthorityConfig,
    evaluate,
)
from lawfirm_os_orchestrator.authority.passport_issuer import (
    PassportRefused,
    issue_passport,
)
from lawfirm_os_orchestrator.commands.preflight_execution import (
    PreflightError,
    preflight,
)
from lawfirm_os_orchestrator.context.compiler import compile_context_bundle
from lawfirm_os_orchestrator.domain.context_bundle import (
    ContextBudget,
    ContextBundleTask,
    PolicyRefStub,
    SourceRefStub,
)
from lawfirm_os_orchestrator.domain.execution_request import build_execution_request


CONFIG = AuthorityConfig(
    allowed_tool_ids=frozenset({"synthetic.read_only", "synthetic.write_with_approval"}),
    allowed_route_ids=frozenset({"route.synthetic_read", "route.synthetic_write"}),
    allowed_event_classes=frozenset({"synthetic.read", "synthetic.write", "synthetic.external"}),
    write_actions_with_approval=frozenset({"write_with_approval"}),
)

FIXED_AT = "2026-05-18T00:00:00Z"


def _bundle():
    return compile_context_bundle(
        context_bundle_id="ctx-1",
        run_id="run-1",
        task=ContextBundleTask(task_id="t1", task_kind="synthetic", task_description_hash="a" * 64),
        source_refs=[SourceRefStub(source_ref_id="sref-1", source_id="src-1", content_hash="b" * 64)],
        policy_refs=[PolicyRefStub(policy_ref_id="p1", policy_id="policy-1")],
        tool_refs=[],
        context_budget=ContextBudget(max_input_bytes=1024, max_steps=4),
        generated_at=FIXED_AT,
    )


def _request(
    *,
    action="read_synthetic",
    tool_id="synthetic.read_only",
    route_id="route.synthetic_read",
    event_class="synthetic.read",
    side_effect="read",
):
    bundle = _bundle()
    return build_execution_request(
        execution_request_id="req-1",
        context_bundle_hash=bundle.context_bundle_hash,
        contract_surface_sha256=bundle.contract_surface_sha256,
        run_id=bundle.run_id,
        requested_at=FIXED_AT,
        requested_action=action,
        requested_tool_id=tool_id,
        requested_route_id=route_id,
        requested_event_class=event_class,
        requested_side_effect_class=side_effect,
        request_payload_hash="c" * 64,
    ), bundle


# ---------- evaluator ----------


def test_synthetic_read_only_is_allowed() -> None:
    req, _ = _request()
    decision = evaluate(req, config=CONFIG)
    assert decision.decision == "allowed"
    assert decision.reason_code == "allowed_under_authority_policy"


def test_external_side_effect_is_denied() -> None:
    req, _ = _request(side_effect="external", event_class="synthetic.external")
    decision = evaluate(req, config=CONFIG)
    assert decision.decision == "denied"
    assert decision.reason_code == "external_writes_forbidden_in_mvp"


def test_unknown_tool_is_denied() -> None:
    req, _ = _request(tool_id="rogue.toolbox")
    decision = evaluate(req, config=CONFIG)
    assert decision.decision == "denied"
    assert decision.reason_code == "unknown_tool"


def test_unknown_route_is_denied() -> None:
    req, _ = _request(route_id="route.unknown")
    decision = evaluate(req, config=CONFIG)
    assert decision.decision == "denied"
    assert decision.reason_code == "unknown_route"


def test_unknown_event_class_is_denied() -> None:
    req, _ = _request(event_class="synthetic.unknown")
    decision = evaluate(req, config=CONFIG)
    assert decision.decision == "denied"
    assert decision.reason_code == "unknown_event_class"


def test_semantic_mutation_action_is_denied() -> None:
    req, _ = _request(action="substrate_write")
    decision = evaluate(req, config=CONFIG)
    assert decision.decision == "denied"
    assert decision.reason_code == "semantic_mutation_forbidden"


def test_write_without_approval_is_denied() -> None:
    req, _ = _request(
        action="write_arbitrary",
        tool_id="synthetic.write_with_approval",
        route_id="route.synthetic_write",
        event_class="synthetic.write",
        side_effect="write",
    )
    decision = evaluate(req, config=CONFIG)
    assert decision.decision == "denied"
    assert decision.reason_code == "write_requires_explicit_approval_policy"


def test_write_with_approval_returns_requires_approval() -> None:
    req, _ = _request(
        action="write_with_approval",
        tool_id="synthetic.write_with_approval",
        route_id="route.synthetic_write",
        event_class="synthetic.write",
        side_effect="write",
    )
    decision = evaluate(req, config=CONFIG)
    assert decision.decision == "requires_approval"
    assert decision.requires_human_approval is True


# ---------- passport issuer ----------


def test_passport_issued_for_allowed_decision() -> None:
    req, bundle = _request()
    decision = evaluate(req, config=CONFIG)
    passport = issue_passport(decision=decision, request=req)
    assert len(passport.execution_passport_hash) == 64
    assert passport.execution_decision_hash == decision.execution_decision_hash
    assert passport.execution_request_hash == req.execution_request_hash
    assert passport.context_bundle_hash == bundle.context_bundle_hash
    assert passport.single_use is True


def test_passport_refused_for_denied_decision() -> None:
    req, _ = _request(tool_id="rogue.toolbox")
    decision = evaluate(req, config=CONFIG)
    with pytest.raises(PassportRefused):
        issue_passport(decision=decision, request=req)


def test_passport_refused_for_requires_approval_decision() -> None:
    req, _ = _request(
        action="write_with_approval",
        tool_id="synthetic.write_with_approval",
        route_id="route.synthetic_write",
        event_class="synthetic.write",
        side_effect="write",
    )
    decision = evaluate(req, config=CONFIG)
    with pytest.raises(PassportRefused):
        issue_passport(decision=decision, request=req)


# ---------- preflight chain ----------


def test_preflight_emits_decision_and_passport_for_allowed_read() -> None:
    req, bundle = _request()
    result = preflight(context_bundle=bundle, request=req, config=CONFIG)
    assert result.decision.decision == "allowed"
    assert result.passport is not None
    assert result.passport.execution_passport_hash


def test_preflight_emits_decision_but_no_passport_for_denied() -> None:
    req, bundle = _request(side_effect="external", event_class="synthetic.external")
    result = preflight(context_bundle=bundle, request=req, config=CONFIG)
    assert result.decision.decision == "denied"
    assert result.passport is None


def test_preflight_rejects_request_with_mismatched_bundle_hash() -> None:
    req, bundle = _request()
    tampered = build_execution_request(
        execution_request_id=req.execution_request_id,
        context_bundle_hash="0" * 64,  # mismatched
        contract_surface_sha256=req.contract_surface_sha256,
        run_id=req.run_id,
        requested_at=req.requested_at,
        requested_action=req.requested_action,
        requested_tool_id=req.requested_tool_id,
        requested_route_id=req.requested_route_id,
        requested_event_class=req.requested_event_class,
        requested_side_effect_class=req.requested_side_effect_class,
        request_payload_hash=req.request_payload_hash,
    )
    with pytest.raises(PreflightError, match="context_bundle_hash"):
        preflight(context_bundle=bundle, request=tampered, config=CONFIG)


def test_preflight_rejects_request_with_mismatched_contract_surface() -> None:
    req, bundle = _request()
    tampered = build_execution_request(
        execution_request_id=req.execution_request_id,
        context_bundle_hash=req.context_bundle_hash,
        contract_surface_sha256="d" * 64,  # mismatched
        run_id=req.run_id,
        requested_at=req.requested_at,
        requested_action=req.requested_action,
        requested_tool_id=req.requested_tool_id,
        requested_route_id=req.requested_route_id,
        requested_event_class=req.requested_event_class,
        requested_side_effect_class=req.requested_side_effect_class,
        request_payload_hash=req.request_payload_hash,
    )
    with pytest.raises(PreflightError, match="contract_surface_sha256"):
        preflight(context_bundle=bundle, request=tampered, config=CONFIG)
