from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import Field

from lawfirm_os_orchestrator.autonomy.autonomy_gate import AutonomyDecision, LocalPhase2Model, RiskColor
from lawfirm_os_orchestrator.harness.agent_committee import AgentReviewPlan, build_agent_review_plan
from lawfirm_os_orchestrator.harness.harness_selector import HarnessPlan
from lawfirm_os_orchestrator.harness.leverage_scorer import OpportunityScorecard, score_leverage
from lawfirm_os_orchestrator.util.ids import new_id
from lawfirm_os_orchestrator.util.json_io import read_json, write_json
from lawfirm_os_orchestrator.util.time import utc_now


class OpportunityInput(LocalPhase2Model):
    opportunity_id: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    source_refs: list[str] = Field(default_factory=list)
    repos_touched: list[str] = Field(min_length=1)
    files_to_add_or_update: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    tests_to_run: list[str] = Field(default_factory=list)
    docs_updates_required: list[str] = Field(default_factory=list)
    expected_output_artifacts: list[str] = Field(default_factory=list)
    implementation_notes: list[str] = Field(default_factory=list)
    stop_conditions: list[str] = Field(default_factory=list)


class CodexTaskPacket(LocalPhase2Model):
    task_packet_id: str = Field(default_factory=lambda: new_id("codex_task_packet"), min_length=1)
    generated_at: str = Field(default_factory=utc_now)
    objective: str = Field(min_length=1)
    source_refs: list[str] = Field(default_factory=list)
    repos_touched: list[str] = Field(min_length=1)
    risk_color: RiskColor
    harness_level: str = Field(min_length=2)
    leverage_score: float = Field(ge=0.0, le=1.0)
    hardness_level: int = Field(ge=0, le=5)
    autonomy_decision_ref: str = Field(min_length=1)
    harness_plan_ref: str = Field(min_length=1)
    allowed_actions: list[str] = Field(min_length=1)
    forbidden_actions: list[str] = Field(min_length=1)
    files_to_add_or_update: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(min_length=1)
    tests_to_run: list[str] = Field(min_length=1)
    rollback_rule: str = Field(min_length=1)
    docs_updates_required: list[str] = Field(default_factory=list)
    safety_invariants: list[str] = Field(min_length=1)
    human_approval_requirements: list[str] = Field(min_length=1)
    expected_output_artifacts: list[str] = Field(default_factory=list)
    implementation_notes: list[str] = Field(default_factory=list)
    stop_conditions: list[str] = Field(min_length=1)
    review_plan: AgentReviewPlan
    runs_codex: Literal[False] = False
    runs_git: Literal[False] = False
    creates_branch: Literal[False] = False
    pushes_git: Literal[False] = False
    applies_patch: Literal[False] = False
    runs_tests: Literal[False] = False
    calls_model: Literal[False] = False
    calls_network: Literal[False] = False
    calls_external_api: Literal[False] = False
    writes_to_semantic_substrate: Literal[False] = False
    lake_writes: Literal[False] = False
    external_writes: Literal[False] = False


BASE_FORBIDDEN_ACTIONS = [
    "execute Codex",
    "execute Git",
    "create branches",
    "push to remotes",
    "apply patches automatically",
    "run tests automatically from packet",
    "call live models",
    "call network or external APIs",
    "write Semantic Substrate",
    "write Exception Lake",
    "restore green authority",
]

BASE_SAFETY_INVARIANTS = [
    "risk color controls authority",
    "hardness controls harness depth only",
    "leverage controls priority only",
    "no real client or matter data",
    "no canonical route_id or event_class invention",
    "no live Research Radar automation",
]


def _payload_section(raw: dict[str, Any], key: str) -> dict[str, Any]:
    value = raw.get(key)
    if isinstance(value, dict):
        return value
    return raw


def _load_autonomy(path: Path) -> AutonomyDecision:
    return AutonomyDecision.model_validate(_payload_section(read_json(path), "autonomy_decision"))


def _load_harness(path: Path) -> HarnessPlan:
    return HarnessPlan.model_validate(_payload_section(read_json(path), "harness_plan"))


def _allowed_actions(risk_color: RiskColor, harness: HarnessPlan) -> list[str]:
    if risk_color == RiskColor.RED:
        return ["prepare proposal-only risk memo", "prepare human decision packet"]
    if risk_color == RiskColor.YELLOW:
        return ["prepare local draft", "prepare test evidence", "prepare review packet", "recommend green-candidate"]
    return ["perform local reversible work inside preapproved lane", *harness.allowed_outputs]


def _forbidden_actions(risk_color: RiskColor, autonomy: AutonomyDecision, harness: HarnessPlan) -> list[str]:
    forbidden = set(BASE_FORBIDDEN_ACTIONS)
    forbidden.update(autonomy.forbidden_actions)
    forbidden.update(harness.forbidden_outputs)
    if risk_color == RiskColor.RED:
        forbidden.update(["auto-merge", "production release", "canon mutation", "external writes"])
    elif risk_color == RiskColor.YELLOW:
        forbidden.update(["auto-merge", "production release", "canon mutation", "external writes"])
    else:
        forbidden.update(["canon mutation", "external writes", "green restoration by agents"])
    return sorted(forbidden)


def _human_requirements(risk_color: RiskColor, harness: HarnessPlan) -> list[str]:
    requirements = ["humans restore or create green authority"]
    if risk_color == RiskColor.RED:
        requirements.append("human approval required before any execution authority")
    if risk_color == RiskColor.YELLOW:
        requirements.append("human review required before final authority")
    if harness.human_required:
        requirements.append("harness plan requires human decision or review")
    return sorted(set(requirements))


def _defaulted(value: list[str], fallback: list[str]) -> list[str]:
    return value if value else fallback


def build_codex_task_packet(
    *,
    opportunity: OpportunityInput,
    scorecard: OpportunityScorecard,
    autonomy: AutonomyDecision,
    harness: HarnessPlan,
) -> CodexTaskPacket:
    leverage = score_leverage(scorecard)
    source_refs = sorted(set(opportunity.source_refs + autonomy.source_refs + harness.reasons))
    review_plan = build_agent_review_plan(
        risk_color=autonomy.risk_color,
        harness_level=harness.harness_level,
        source_refs=source_refs,
    )
    return CodexTaskPacket(
        objective=opportunity.objective,
        source_refs=source_refs,
        repos_touched=opportunity.repos_touched,
        risk_color=autonomy.risk_color,
        harness_level=harness.harness_level.value,
        leverage_score=leverage.leverage_score,
        hardness_level=harness.hardness_level,
        autonomy_decision_ref=autonomy.autonomy_decision_id,
        harness_plan_ref=harness.harness_plan_id,
        allowed_actions=_allowed_actions(autonomy.risk_color, harness),
        forbidden_actions=_forbidden_actions(autonomy.risk_color, autonomy, harness),
        files_to_add_or_update=opportunity.files_to_add_or_update,
        acceptance_criteria=_defaulted(opportunity.acceptance_criteria, ["human reviewer confirms packet scope"]),
        tests_to_run=_defaulted(opportunity.tests_to_run, ["python -m pytest", "python scripts/check_safety.py --stdout json"]),
        rollback_rule="Stop and revert only the proposed future implementation if validation or authority checks fail.",
        docs_updates_required=opportunity.docs_updates_required,
        safety_invariants=BASE_SAFETY_INVARIANTS,
        human_approval_requirements=_human_requirements(autonomy.risk_color, harness),
        expected_output_artifacts=opportunity.expected_output_artifacts,
        implementation_notes=_defaulted(
            opportunity.implementation_notes,
            ["This packet is inert build guidance and must not execute work."],
        ),
        stop_conditions=_defaulted(
            opportunity.stop_conditions,
            ["stop if task requires real data, external writes, model calls, Git execution, or canon mutation"],
        ),
        review_plan=review_plan,
    )


def write_codex_task_packet(
    *,
    opportunity_path: Path,
    scorecard_path: Path,
    autonomy_path: Path,
    harness_path: Path,
    out_path: Path,
) -> dict[str, Any]:
    opportunity = OpportunityInput.model_validate(read_json(opportunity_path))
    scorecard = OpportunityScorecard.model_validate(read_json(scorecard_path))
    autonomy = _load_autonomy(autonomy_path)
    harness = _load_harness(harness_path)
    packet = build_codex_task_packet(opportunity=opportunity, scorecard=scorecard, autonomy=autonomy, harness=harness)
    payload = {
        "schema_version": "1.0",
        "status": "ok",
        "local_artifact_only": True,
        "task_packet": packet.model_dump(mode="json"),
        "runs_codex": False,
        "runs_git": False,
        "creates_branch": False,
        "pushes_git": False,
        "applies_patch": False,
        "runs_tests": False,
        "calls_model": False,
        "calls_network": False,
        "calls_external_api": False,
        "writes_to_semantic_substrate": False,
        "lake_writes": False,
        "external_writes": False,
    }
    write_json(out_path, payload)
    return payload
