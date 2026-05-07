from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from lawfirm_os_orchestrator.util.ids import new_id
from lawfirm_os_orchestrator.util.time import utc_now


class LocalPhase2Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    semantics: Literal["local_orchestrator_record"] = "local_orchestrator_record"
    may_mutate_canon: Literal[False] = False
    may_define_route_id: Literal[False] = False
    may_define_event_class: Literal[False] = False
    may_write_semantic_substrate: Literal[False] = False
    may_write_exception_lake: Literal[False] = False
    may_call_model: Literal[False] = False
    may_call_network: Literal[False] = False
    may_run_git: Literal[False] = False
    may_apply_patch: Literal[False] = False
    may_external_write: Literal[False] = False


class RiskColor(StrEnum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    GREEN_CANDIDATE = "green_candidate"


class AutonomyMode(StrEnum):
    HUMAN_OUT_OF_LOOP = "human_out_of_loop"
    AUTONOMOUS_FLAGGED = "autonomous_flagged"
    HUMAN_IN_LOOP = "human_in_loop"


class DataScope(StrEnum):
    SYNTHETIC = "synthetic"
    METADATA_ONLY = "metadata_only"
    DRAFT = "draft"
    UNKNOWN = "unknown"
    REAL_CLIENT = "real_client"
    REAL_MATTER = "real_matter"
    PRIVILEGED = "privileged"


class ActionType(StrEnum):
    DETERMINISTIC_CHECK = "deterministic_check"
    DOC_CHANGE = "doc_change"
    TEST_CHANGE = "test_change"
    PROMPT_CHANGE = "prompt_change"
    VALIDATOR_CHANGE = "validator_change"
    AUTONOMY_CHANGE = "autonomy_change"
    CODE_CHANGE = "code_change"
    LOCAL_ARTIFACT_GENERATION = "local_artifact_generation"
    CODEX_TASK_PACKET_DRAFT = "codex_task_packet_draft"
    CANON_MUTATION = "canon_mutation"
    EXTERNAL_WRITE = "external_write"
    UNKNOWN = "unknown"


class ActionDescriptor(LocalPhase2Model):
    action_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    action_type: ActionType
    data_scope: DataScope
    local_only: bool
    reversible: bool
    inside_preapproved_lane: bool
    preapproved_lane_id: str | None = None
    source_refs: list[str] = Field(default_factory=list)
    audit_evidence_recording_allowed: bool = True
    bounded_change: bool = False
    needs_review: bool = False
    attempts_green_restoration: bool = False
    contains_real_client_data: bool = False
    contains_real_matter_data: bool = False
    contains_privileged_content: bool = False
    external_side_effect: bool = False
    canon_mutation: bool = False
    creates_new_route_id: bool = False
    creates_new_event_class: bool = False
    client_visible_output: bool = False
    legal_or_billing_finality: bool = False
    contains_secrets: bool = False
    destructive_operation_risk: bool = False
    approval_bypass: bool = False
    live_research_radar_automation: bool = False
    scheduled_job: bool = False
    model_call: bool = False
    external_api_or_network_call: bool = False


class AutonomyDecision(LocalPhase2Model):
    autonomy_decision_id: str = Field(default_factory=lambda: new_id("autonomy_decision"), min_length=1)
    action_id: str = Field(min_length=1)
    risk_color: RiskColor
    autonomy_mode: AutonomyMode
    allowed_actions: list[str] = Field(min_length=1)
    forbidden_actions: list[str] = Field(min_length=1)
    audit_required: bool
    human_required: bool
    human_green_required: bool
    may_restore_green: Literal[False] = False
    reasons: list[str] = Field(min_length=1)
    source_refs: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now)


RED_TRIGGER_FIELDS: tuple[tuple[str, str], ...] = (
    ("contains_real_client_data", "real client data is present"),
    ("contains_real_matter_data", "real matter data is present"),
    ("contains_privileged_content", "privileged content is present"),
    ("external_side_effect", "external side effect is requested"),
    ("canon_mutation", "canonical substrate mutation is requested"),
    ("creates_new_route_id", "new route_id authority is requested"),
    ("creates_new_event_class", "new event_class authority is requested"),
    ("client_visible_output", "client-visible finality is requested"),
    ("legal_or_billing_finality", "legal or billing finality is requested"),
    ("contains_secrets", "secret or credential exposure is possible"),
    ("destructive_operation_risk", "destructive operation risk is present"),
    ("approval_bypass", "approval bypass is requested"),
    ("attempts_green_restoration", "agent attempted to create or restore green authority"),
    ("live_research_radar_automation", "live Research Radar automation is requested"),
    ("scheduled_job", "scheduled job is requested"),
    ("model_call", "unapproved model call is requested"),
    ("external_api_or_network_call", "external API or network call is requested"),
)


GREEN_DATA_SCOPES = {DataScope.SYNTHETIC, DataScope.METADATA_ONLY}
YELLOW_DATA_SCOPES = {DataScope.SYNTHETIC, DataScope.METADATA_ONLY, DataScope.DRAFT}
BOUNDED_ACTION_TYPES = {
    ActionType.DOC_CHANGE,
    ActionType.TEST_CHANGE,
    ActionType.PROMPT_CHANGE,
    ActionType.VALIDATOR_CHANGE,
    ActionType.AUTONOMY_CHANGE,
    ActionType.CODE_CHANGE,
    ActionType.LOCAL_ARTIFACT_GENERATION,
    ActionType.CODEX_TASK_PACKET_DRAFT,
    ActionType.DETERMINISTIC_CHECK,
}


def red_trigger_reasons(action: ActionDescriptor) -> list[str]:
    reasons = [reason for field, reason in RED_TRIGGER_FIELDS if bool(getattr(action, field))]
    if action.data_scope in {DataScope.REAL_CLIENT, DataScope.REAL_MATTER, DataScope.PRIVILEGED}:
        reasons.append(f"data_scope is {action.data_scope.value}")
    if action.action_type in {ActionType.CANON_MUTATION, ActionType.EXTERNAL_WRITE}:
        reasons.append(f"action_type is {action.action_type.value}")
    return reasons


def _green_reasons(action: ActionDescriptor) -> list[str]:
    return [
        "synthetic or metadata-only scope",
        "local-only action",
        "reversible action",
        "inside preapproved green lane",
        f"preapproved_lane_id={action.preapproved_lane_id}",
        "no canon, route, event, client, legal, external, model, network, or scheduled-job trigger",
    ]


def _base_forbidden() -> list[str]:
    return [
        "mutate Semantic Substrate",
        "create canonical route_id or event_class",
        "use real client or matter data",
        "use privileged content",
        "perform external writes",
        "call live models or external APIs",
        "schedule background jobs",
        "restore green authority without human approval",
    ]


def _is_green(action: ActionDescriptor) -> bool:
    return (
        action.data_scope in GREEN_DATA_SCOPES
        and action.local_only
        and action.reversible
        and action.inside_preapproved_lane
        and bool(action.preapproved_lane_id)
        and action.audit_evidence_recording_allowed
    )


def _is_yellow(action: ActionDescriptor) -> bool:
    return (
        action.data_scope in YELLOW_DATA_SCOPES
        and action.local_only
        and action.action_type in BOUNDED_ACTION_TYPES
        and (action.bounded_change or action.needs_review or not action.inside_preapproved_lane or not action.reversible)
    )


def classify_autonomy(action: ActionDescriptor) -> AutonomyDecision:
    red_reasons = red_trigger_reasons(action)
    if red_reasons:
        return AutonomyDecision(
            action_id=action.action_id,
            risk_color=RiskColor.RED,
            autonomy_mode=AutonomyMode.HUMAN_IN_LOOP,
            allowed_actions=["prepare proposal-only risk memo", "prepare human decision packet"],
            forbidden_actions=_base_forbidden() + ["execute final authority", "proceed without human approval"],
            audit_required=True,
            human_required=True,
            human_green_required=True,
            reasons=["hard red trigger overrides hardness and leverage", *red_reasons],
            source_refs=action.source_refs,
        )
    if _is_green(action):
        return AutonomyDecision(
            action_id=action.action_id,
            risk_color=RiskColor.GREEN,
            autonomy_mode=AutonomyMode.HUMAN_OUT_OF_LOOP,
            allowed_actions=["perform local reversible action", "write local audit or evidence artifact"],
            forbidden_actions=_base_forbidden(),
            audit_required=True,
            human_required=False,
            human_green_required=False,
            reasons=_green_reasons(action),
            source_refs=action.source_refs,
        )
    if _is_yellow(action):
        return AutonomyDecision(
            action_id=action.action_id,
            risk_color=RiskColor.YELLOW,
            autonomy_mode=AutonomyMode.AUTONOMOUS_FLAGGED,
            allowed_actions=["prepare bounded local draft", "run local tests", "prepare green-candidate recommendation"],
            forbidden_actions=_base_forbidden() + ["finalize authority without review"],
            audit_required=True,
            human_required=True,
            human_green_required=True,
            reasons=[
                "bounded local or draft work needs review or human awareness",
                "may recommend green-candidate but cannot restore green",
            ],
            source_refs=action.source_refs,
        )
    return AutonomyDecision(
        action_id=action.action_id,
        risk_color=RiskColor.RED,
        autonomy_mode=AutonomyMode.HUMAN_IN_LOOP,
        allowed_actions=["prepare proposal-only risk memo"],
        forbidden_actions=_base_forbidden() + ["treat ambiguous work as green"],
        audit_required=True,
        human_required=True,
        human_green_required=True,
        reasons=["action does not satisfy green or yellow conditions and fails closed"],
        source_refs=action.source_refs,
    )
