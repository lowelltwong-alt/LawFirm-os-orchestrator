from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from lawfirm_os_orchestrator.learning.models import (
    ExperimentPlan,
    ShadowEvalResult,
    TargetSurface,
    UpgradeProposal,
    boundary_flags,
)
from lawfirm_os_orchestrator.util.ids import new_id
from lawfirm_os_orchestrator.util.json_io import read_json, write_json


class UpgradeProposalPacketRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    proposal_id: str = Field(min_length=1)
    hypothesis_id: str = Field(default_factory=lambda: new_id("upgrade_hypothesis"), min_length=1)
    experiment_plan: ExperimentPlan
    shadow_eval_result: ShadowEvalResult | None = None
    discovery_signal_refs: list[str] = Field(default_factory=list)
    algorithm_insight_refs: list[str] = Field(default_factory=list)
    target_surface: TargetSurface
    affected_metric: str = Field(min_length=1)
    expected_metric_lift: dict[str, float] = Field(min_length=1)
    risks: list[str] = Field(min_length=1)
    implementation_cost: Literal["low", "medium", "high", "critical"]
    evidence_refs: list[str] = Field(min_length=1)
    tests_required: list[str] = Field(min_length=1)
    shadow_eval_result_refs: list[str] = Field(default_factory=list)
    approval_requirement: Literal["human_review_required"] = "human_review_required"
    stop_conditions: list[str] = Field(min_length=1)


def load_upgrade_proposal_packet_request(path: Path) -> UpgradeProposalPacketRequest:
    if not path.exists():
        raise FileNotFoundError(f"Upgrade proposal packet request not found: {path}")
    return UpgradeProposalPacketRequest.model_validate(read_json(path))


def _risk_review_markdown(request: UpgradeProposalPacketRequest, proposal: UpgradeProposal) -> str:
    risks = "\n".join(f"- {risk}" for risk in request.risks)
    stops = "\n".join(f"- {condition}" for condition in request.stop_conditions)
    tests = "\n".join(f"- {command}" for command in request.tests_required)
    return (
        "# Upgrade Proposal Risk Review\n\n"
        f"Proposal ID: `{proposal.upgrade_proposal_id}`\n\n"
        f"Target surface: `{proposal.target_surface.value}`\n\n"
        f"Affected metric: `{request.affected_metric}`\n\n"
        "Semantics: proposal-only local artifact.\n\n"
        "Required approval: human review before any implementation work.\n\n"
        "Implementation status: no automatic implementation is allowed.\n\n"
        "Boundary controls: no code mutation, no Git operations, no Semantic Substrate writes, no Lake writes.\n\n"
        "## Risks\n\n"
        f"{risks}\n\n"
        "## Tests Required\n\n"
        f"{tests}\n\n"
        "## Stop Conditions\n\n"
        f"{stops}\n"
    )


def _codex_task_draft_markdown(request: UpgradeProposalPacketRequest, proposal: UpgradeProposal) -> str:
    tests = "\n".join(f"- {command}" for command in request.tests_required)
    stops = "\n".join(f"- {condition}" for condition in request.stop_conditions)
    return (
        "# Inert Codex Task Draft\n\n"
        "This artifact is for human review. It is not invoked by the Orchestrator.\n\n"
        "Codex level: High\n\n"
        f"Route: consider proposal `{proposal.upgrade_proposal_id}` for `{proposal.target_surface.value}`.\n\n"
        "Mode: local planning or implementation only after separate human approval.\n\n"
        "Allowed paths: to be set by the reviewer.\n\n"
        "Forbidden paths: Semantic Substrate repo, Exception Lake Runtime repo, production connector paths.\n\n"
        "Validation plan:\n\n"
        f"{tests}\n\n"
        "Stop conditions:\n\n"
        f"{stops}\n"
    )


def build_upgrade_proposal_packet(
    *,
    request_path: Path,
    output_root: Path,
) -> dict[str, str | dict[str, object]]:
    request = load_upgrade_proposal_packet_request(request_path)
    proposal = UpgradeProposal(
        upgrade_proposal_id=request.proposal_id,
        hypothesis_id=request.hypothesis_id,
        experiment_plan_id=request.experiment_plan.experiment_plan_id,
        shadow_eval_result_id=(
            request.shadow_eval_result.shadow_eval_result_id if request.shadow_eval_result is not None else None
        ),
        target_surface=request.target_surface,
        expected_metric_lift=request.expected_metric_lift,
        risks=request.risks,
        tests_required=request.tests_required,
    )
    packet_dir = output_root / proposal.upgrade_proposal_id
    packet_dir.mkdir(parents=True, exist_ok=True)

    proposal_json = {
        "schema_version": "1.0",
        "proposal": proposal.model_dump(mode="json"),
        "discovery_signal_refs": request.discovery_signal_refs,
        "algorithm_insight_refs": request.algorithm_insight_refs,
        "affected_metric": request.affected_metric,
        "implementation_cost": request.implementation_cost,
        "approval_requirement": request.approval_requirement,
        "stop_conditions": request.stop_conditions,
        "boundary_flags": boundary_flags(proposal),
        "local_artifact_only": True,
        "automatic_implementation": False,
        "git_operations": False,
        "semantic_substrate_writes": False,
        "lake_writes": False,
    }
    evidence_json = {
        "schema_version": "1.0",
        "evidence_refs": request.evidence_refs,
        "discovery_signal_refs": request.discovery_signal_refs,
        "algorithm_insight_refs": request.algorithm_insight_refs,
        "shadow_eval_result_refs": request.shadow_eval_result_refs,
    }

    write_json(packet_dir / "proposal.json", proposal_json)
    write_json(packet_dir / "evidence_refs.json", evidence_json)
    write_json(packet_dir / "experiment_plan.json", request.experiment_plan.model_dump(mode="json"))
    if request.shadow_eval_result is None:
        write_json(packet_dir / "shadow_eval_result.json", {"schema_version": "1.0", "status": "not_available"})
    else:
        write_json(packet_dir / "shadow_eval_result.json", request.shadow_eval_result.model_dump(mode="json"))
    (packet_dir / "risk_review.md").write_text(_risk_review_markdown(request, proposal), encoding="utf-8")
    (packet_dir / "codex_task_draft.md").write_text(_codex_task_draft_markdown(request, proposal), encoding="utf-8")

    return {
        "schema_version": "1.0",
        "semantics": "proposal_only",
        "proposal_id": proposal.upgrade_proposal_id,
        "packet_dir": str(packet_dir),
        "files": {
            "proposal": str(packet_dir / "proposal.json"),
            "evidence_refs": str(packet_dir / "evidence_refs.json"),
            "experiment_plan": str(packet_dir / "experiment_plan.json"),
            "shadow_eval_result": str(packet_dir / "shadow_eval_result.json"),
            "risk_review": str(packet_dir / "risk_review.md"),
            "codex_task_draft": str(packet_dir / "codex_task_draft.md"),
        },
        "boundary_flags": boundary_flags(proposal),
        "local_artifact_only": True,
        "automatic_implementation": False,
        "git_operations": False,
        "semantic_substrate_writes": False,
        "lake_writes": False,
    }
