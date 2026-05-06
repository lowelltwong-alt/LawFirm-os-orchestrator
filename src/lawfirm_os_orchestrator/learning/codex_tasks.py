from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

from lawfirm_os_orchestrator.learning.models import ActionRecommendation, CodexTaskDraft, boundary_flags
from lawfirm_os_orchestrator.learning.recommendations import ActionRecommendationRequest, build_action_recommendation
from lawfirm_os_orchestrator.util.json_io import read_json, write_json


class CodexTaskArtifactRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    action_recommendation: ActionRecommendationRequest
    codex_task_draft: CodexTaskDraft


def load_codex_task_artifact_request(path: Path) -> CodexTaskArtifactRequest:
    if not path.exists():
        raise FileNotFoundError(f"Codex task artifact request not found: {path}")
    return CodexTaskArtifactRequest.model_validate(read_json(path))


def render_codex_task_markdown(draft: CodexTaskDraft) -> str:
    allowed = "\n".join(f"- {path}" for path in draft.allowed_paths)
    forbidden = "\n".join(f"- {path}" for path in draft.forbidden_paths)
    validation = "\n".join(f"- {command}" for command in draft.validation_commands)
    stops = "\n".join(f"- {condition}" for condition in draft.stop_conditions)
    artifacts = "\n".join(f"- {artifact}" for artifact in draft.expected_artifacts)
    controls = "\n".join(
        [
            "- No push.",
            "- No real client or matter data.",
            "- No Semantic Substrate writes.",
            "- No sibling repo edits.",
            "- No automatic patching.",
            "- Local artifacts only.",
        ]
    )
    return (
        "# Codex Task Draft\n\n"
        "This is an inert local artifact for human review.\n\n"
        f"Codex level: {draft.codex_level}\n\n"
        f"Route: {draft.route}\n\n"
        f"Mode: {draft.mode}\n\n"
        "Allowed paths:\n\n"
        f"{allowed}\n\n"
        "Forbidden paths:\n\n"
        f"{forbidden}\n\n"
        "Validation plan:\n\n"
        f"{validation}\n\n"
        "Stop conditions:\n\n"
        f"{stops}\n\n"
        "Expected artifacts:\n\n"
        f"{artifacts}\n\n"
        "Controls:\n\n"
        f"{controls}\n\n"
        "Task prompt:\n\n"
        f"{draft.prompt_markdown}\n"
    )


def write_codex_task_artifacts(
    *,
    request_path: Path,
    output_dir: Path,
) -> dict[str, object]:
    request = load_codex_task_artifact_request(request_path)
    recommendation_payload = build_action_recommendation(request.action_recommendation)
    recommendation = ActionRecommendation.model_validate(recommendation_payload["recommendation"])
    draft = request.codex_task_draft
    if draft.recommendation_id != recommendation.action_recommendation_id:
        draft = draft.model_copy(update={"recommendation_id": recommendation.action_recommendation_id})

    output_dir.mkdir(parents=True, exist_ok=True)
    recommendation_path = output_dir / "action_recommendation.json"
    draft_json_path = output_dir / "codex_task_draft.json"
    draft_markdown_path = output_dir / "codex_task_draft.md"

    write_json(recommendation_path, recommendation_payload)
    write_json(
        draft_json_path,
        {
            "schema_version": "1.0",
            "semantics": "proposal_only",
            "draft": draft.model_dump(mode="json"),
            "boundary_flags": boundary_flags(draft),
            "local_artifact_only": True,
            "runs_codex": False,
            "runs_git": False,
            "applies_patch": False,
        },
    )
    draft_markdown_path.write_text(render_codex_task_markdown(draft), encoding="utf-8")
    return {
        "schema_version": "1.0",
        "semantics": "proposal_only",
        "output_dir": str(output_dir),
        "files": {
            "action_recommendation": str(recommendation_path),
            "codex_task_draft_json": str(draft_json_path),
            "codex_task_draft_markdown": str(draft_markdown_path),
        },
        "boundary_flags": boundary_flags(draft),
        "local_artifact_only": True,
        "runs_codex": False,
        "runs_git": False,
        "applies_patch": False,
    }
