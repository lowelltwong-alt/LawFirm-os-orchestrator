"""preflight-execution command (PR-04).

Given a ContextBundle and an ExecutionRequest, this command:
  1. Evaluates the request against an AuthorityConfig.
  2. If allowed: issues an ExecutionPassport.
  3. Returns (decision, passport-or-None).

Designed to be wired into classify-exception and action execution wrappers
(deferred wiring noted in PR-04 commit body; this command stands alone for
direct use and for tests).
"""
from __future__ import annotations

from dataclasses import dataclass

from lawfirm_os_orchestrator.authority.execution_authority import (
    AuthorityConfig,
    evaluate,
)
from lawfirm_os_orchestrator.authority.passport_issuer import (
    PassportRefused,
    issue_passport,
)
from lawfirm_os_orchestrator.domain.context_bundle import ContextBundle
from lawfirm_os_orchestrator.domain.execution_decision import ExecutionDecision
from lawfirm_os_orchestrator.domain.execution_passport import ExecutionPassport
from lawfirm_os_orchestrator.domain.execution_request import ExecutionRequest


@dataclass(frozen=True)
class PreflightResult:
    decision: ExecutionDecision
    passport: ExecutionPassport | None


class PreflightError(RuntimeError):
    pass


def preflight(
    *,
    context_bundle: ContextBundle,
    request: ExecutionRequest,
    config: AuthorityConfig,
) -> PreflightResult:
    if request.context_bundle_hash != context_bundle.context_bundle_hash:
        raise PreflightError(
            "request.context_bundle_hash does not match context_bundle.context_bundle_hash; "
            "the request was not produced under the supplied bundle"
        )
    if request.contract_surface_sha256 != context_bundle.contract_surface_sha256:
        raise PreflightError(
            "request.contract_surface_sha256 does not match context_bundle.contract_surface_sha256; "
            "request and bundle were produced under different substrate authority surfaces"
        )
    decision = evaluate(request, config=config)
    if decision.decision == "allowed":
        try:
            passport = issue_passport(decision=decision, request=request)
        except PassportRefused as exc:
            raise PreflightError(str(exc)) from exc
        return PreflightResult(decision=decision, passport=passport)
    return PreflightResult(decision=decision, passport=None)
