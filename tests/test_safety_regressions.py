from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from lawfirm_os_orchestrator.cli import build_parser
from lawfirm_os_orchestrator.commands.classify_exception import EXIT_ARTIFACT, EXIT_INPUT_POLICY, EXIT_LAKE, run
from lawfirm_os_orchestrator.discovery.local_import import import_signal
from lawfirm_os_orchestrator.domain.models import ClassificationResult
from lawfirm_os_orchestrator.evals.runner import run_eval_suite
from lawfirm_os_orchestrator.learning.codex_tasks import write_codex_task_artifacts
from lawfirm_os_orchestrator.learning.proposals import build_upgrade_proposal_packet
from lawfirm_os_orchestrator.policy.gate import fail_reasons, validate_classification
from lawfirm_os_orchestrator.substrate.reader import PathSubstrateClient
from lawfirm_os_orchestrator.util.json_io import read_json

ROOT = Path(__file__).resolve().parents[1]


def classify_args(tmp_path: Path, *, input_path: Path | None = None, lake_mode: str = "disabled", ledger_dir: Path | None = None):
    return SimpleNamespace(
        input=str(input_path or ROOT / "examples" / "synthetic_exception_event.json"),
        substrate=str(ROOT / "tests" / "fixtures" / "substrate"),
        ledger_dir=str(ledger_dir or tmp_path / "ledger"),
        packet_out=str(tmp_path / "runs"),
        lake_mode=lake_mode,
        stdout="json",
    )


def test_substrate_client_has_no_write_or_mutation_methods():
    client = PathSubstrateClient(ROOT / "tests" / "fixtures" / "substrate")
    forbidden = [name for name in dir(client) if name.startswith(("write", "update", "delete", "mutate", "create", "save", "append"))]
    assert forbidden == []


def test_cli_lake_mode_defaults_disabled():
    args = build_parser().parse_args(
        [
            "classify-exception",
            "--input",
            "examples/synthetic_exception_event.json",
        ]
    )
    assert args.lake_mode == "disabled"


def test_disabled_lake_mode_does_not_attempt_or_write_lake_files(tmp_path):
    code, summary = run(classify_args(tmp_path))
    packet_dir = Path(summary["evidence_packet_path"])

    assert code == 0
    assert summary["lake"]["mode"] == "disabled"
    assert summary["lake"]["attempted"] is False
    assert summary["lake"]["status"] == "not_attempted"
    assert not (packet_dir / "ingest_request.json").exists()
    assert not (packet_dir / "ingest_receipt.json").exists()


def test_runtime_safe_lake_mode_fails_closed_without_dual_opt_in(monkeypatch, tmp_path):
    monkeypatch.delenv("LAWFIRM_OS_ORCHESTRATOR_ALLOW_RUNTIME_SAFE", raising=False)
    code, summary = run(classify_args(tmp_path, lake_mode="runtime-safe"))

    assert code == EXIT_LAKE
    assert summary["status"] == "lake_rejected"
    assert summary["lake"]["attempted"] is False
    assert any("requires config allow switch" in reason for reason in summary["lake"]["rejection_reasons"])


def test_runtime_safe_lake_mode_stays_unwired_even_with_env_opt_in(monkeypatch, tmp_path):
    monkeypatch.setenv("LAWFIRM_OS_ORCHESTRATOR_ALLOW_RUNTIME_SAFE", "true")
    code, summary = run(classify_args(tmp_path, lake_mode="runtime-safe"))

    assert code == EXIT_LAKE
    assert summary["status"] == "lake_rejected"
    assert summary["lake"]["attempted"] is False
    assert any("intentionally not wired" in reason for reason in summary["lake"]["rejection_reasons"])


def test_real_client_matter_and_non_synthetic_inputs_fail_gate(tmp_path):
    base = read_json(ROOT / "examples" / "synthetic_exception_event.json")
    for key, value in (
        ("contains_real_client_data", True),
        ("contains_real_matter_data", True),
        ("synthetic", False),
    ):
        raw = dict(base)
        raw[key] = value
        path = tmp_path / f"{key}.json"
        path.write_text(json.dumps(raw), encoding="utf-8")
        code, summary = run(classify_args(tmp_path, input_path=path))
        assert code == EXIT_INPUT_POLICY
        assert summary["status"] == "failed_validation"


def test_unknown_route_and_event_values_fail_closed():
    snapshot = PathSubstrateClient(ROOT / "tests" / "fixtures" / "substrate").load_snapshot()
    result = ClassificationResult(
        route_id="route.unknown.v1",
        event_class="unknown_event",
        supporting_claim_refs=["claim.synthetic"],
        confidence=0.9,
    )
    reasons = fail_reasons(validate_classification(result, snapshot))

    assert any("unknown route_id" in reason for reason in reasons)
    assert any("unknown event_class" in reason for reason in reasons)


def test_research_signal_import_cannot_execute_code_git_patches_or_network(monkeypatch, tmp_path):
    def fail_socket(*args, **kwargs):
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "socket", fail_socket)
    signal = import_signal(ROOT / "examples" / "research_signals" / "example_signal.json", tmp_path / "signals.jsonl")

    assert signal.local_only is True
    assert signal.no_network_required is True
    assert signal.may_execute is False
    assert signal.may_apply_patch is False
    assert signal.may_push_git is False
    assert signal.may_run_git is False
    assert signal.may_edit_code is False


def test_upgrade_proposals_and_codex_task_drafts_are_inert_artifacts(tmp_path):
    proposal = build_upgrade_proposal_packet(
        request_path=ROOT / "examples" / "upgrade_proposals" / "validator_threshold_packet_request.json",
        output_root=tmp_path / "packets",
    )
    task = write_codex_task_artifacts(
        request_path=ROOT / "examples" / "codex_task_drafts" / "validator_task_draft_request.json",
        output_dir=tmp_path / "draft",
    )

    assert proposal["automatic_implementation"] is False
    assert proposal["git_operations"] is False
    assert proposal["semantic_substrate_writes"] is False
    assert proposal["lake_writes"] is False
    assert task["runs_codex"] is False
    assert task["runs_git"] is False
    assert task["applies_patch"] is False
    assert task["boundary_flags"]["may_execute"] is False


def test_eval_suite_remains_deterministic_across_repeated_runs(tmp_path):
    kwargs = {
        "fixture_path": ROOT / "evals" / "fixtures" / "classify_exception_cases.jsonl",
        "gold_path": ROOT / "evals" / "gold" / "classify_exception_gold.jsonl",
        "substrate_root": ROOT / "tests" / "fixtures" / "substrate",
        "artifact_root": tmp_path / "artifacts",
    }
    first = run_eval_suite(**kwargs)
    second = run_eval_suite(**kwargs)

    assert first["metrics"] == second["metrics"]
    assert [case["case_id"] for case in first["cases"]] == [case["case_id"] for case in second["cases"]]


def test_ledger_write_failure_fails_the_run(tmp_path):
    ledger_parent = tmp_path / "ledger-as-file"
    ledger_parent.write_text("not a directory", encoding="utf-8")

    code, summary = run(classify_args(tmp_path, ledger_dir=ledger_parent))

    assert code == EXIT_ARTIFACT
    assert summary["status"] == "artifact_failed"
    assert "ledger write failed" in summary["error"]


def test_safety_check_script_outputs_ok_json():
    completed = subprocess.run(
        [sys.executable, "scripts/check_safety.py", "--stdout", "json"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    output = json.loads(completed.stdout)

    assert output["status"] == "ok"
    assert output["checks"]["substrate_client_has_no_write_methods"] is True
    assert output["checks"]["lake_mode_defaults_disabled"] is True
    assert output["checks"]["local_learning_imports_have_no_network_or_process_modules"] is True


def test_learning_cli_source_does_not_import_process_or_network_modules():
    source = (ROOT / "src" / "lawfirm_os_orchestrator" / "commands" / "learning.py").read_text(encoding="utf-8")

    assert "subprocess" not in source
    assert "socket" not in source
    assert "requests" not in source
    assert "httpx" not in source
    assert "urllib" not in source
    assert "git push" not in source
    assert "git commit" not in source
    assert "git apply" not in source
