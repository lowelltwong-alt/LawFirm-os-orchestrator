from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from lawfirm_os_orchestrator.learning.codex_tasks import render_codex_task_markdown, write_codex_task_artifacts
from lawfirm_os_orchestrator.learning.models import CodexTaskDraft
from lawfirm_os_orchestrator.util.json_io import read_json

ROOT = Path(__file__).resolve().parents[1]


def test_codex_task_artifacts_are_inert_local_files(tmp_path):
    result = write_codex_task_artifacts(
        request_path=ROOT / "examples" / "codex_task_drafts" / "validator_task_draft_request.json",
        output_dir=tmp_path / "draft",
    )

    assert result["local_artifact_only"] is True
    assert result["runs_codex"] is False
    assert result["runs_git"] is False
    assert result["applies_patch"] is False
    for path in result["files"].values():
        assert Path(str(path)).exists()

    draft_json = read_json(Path(str(result["files"]["codex_task_draft_json"])))
    assert draft_json["boundary_flags"]["may_execute"] is False
    assert draft_json["draft"]["codex_level"] == "High"


def test_codex_task_markdown_includes_required_sections():
    raw = read_json(ROOT / "examples" / "codex_task_drafts" / "validator_task_draft_request.json")
    draft = CodexTaskDraft.model_validate(raw["codex_task_draft"])
    markdown = render_codex_task_markdown(draft)

    assert "Codex level: High" in markdown
    assert "Allowed paths:" in markdown
    assert "Forbidden paths:" in markdown
    assert "Validation plan:" in markdown
    assert "Stop conditions:" in markdown
    assert "Expected artifacts:" in markdown
    assert "No push." in markdown
    assert "No real client or matter data." in markdown
    assert "No Semantic Substrate writes." in markdown


def test_codex_task_draft_rejects_execution_semantics():
    raw = read_json(ROOT / "examples" / "codex_task_drafts" / "validator_task_draft_request.json")
    raw["codex_task_draft"]["validation_commands"] = ["git push origin main"]
    with pytest.raises(ValidationError, match="forbidden execution language"):
        CodexTaskDraft.model_validate(raw["codex_task_draft"])


def test_render_codex_task_script_outputs_json(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/render_codex_task.py",
            "--input",
            "examples/codex_task_drafts/validator_task_draft_request.json",
            "--out",
            str(tmp_path / "draft"),
            "--stdout",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    output = json.loads(completed.stdout)
    assert output["local_artifact_only"] is True
    assert output["runs_codex"] is False
    assert Path(output["files"]["codex_task_draft_markdown"]).exists()
