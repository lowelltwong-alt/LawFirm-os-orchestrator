from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from lawfirm_os_orchestrator.commands.classify_exception import EXIT_POLICY, run

ROOT = Path(__file__).resolve().parents[1]


def _args(tmp_path: Path, **overrides):
    base = {
        "input": str(ROOT / "examples" / "synthetic_exception_event.json"),
        "substrate": str(ROOT / "tests" / "fixtures" / "substrate"),
        "ledger_dir": str(tmp_path / "ledger"),
        "packet_out": str(tmp_path / "runs"),
        "lake_mode": "disabled",
        "stdout": "json",
        "agent_control_source": "local_fixture",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _prompt_registry(tmp_path: Path, **record_updates) -> Path:
    raw = json.loads((ROOT / "config" / "agent_hostile" / "prompt_registry.json").read_text(encoding="utf-8"))
    raw["prompts"][0].update(record_updates)
    path = tmp_path / "prompt_registry.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    return path


def _sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_prompt_hash_mismatch_blocks_action(tmp_path: Path) -> None:
    path = _prompt_registry(tmp_path, prompt_sha256="sha256:" + "0" * 64)
    code, summary = run(_args(tmp_path, prompt_registry=str(path)))

    assert code == EXIT_POLICY
    assert summary["gate"] == "PromptIntegrityGate"
    assert summary["reason_code"] == "prompt_hash_mismatch"


def test_unapproved_prompt_blocks_action(tmp_path: Path) -> None:
    path = _prompt_registry(tmp_path, approved=False, prompt_sha256="sha256:" + "0" * 64)
    code, summary = run(_args(tmp_path, prompt_registry=str(path)))

    assert code == EXIT_POLICY
    assert summary["gate"] == "PromptIntegrityGate"
    assert summary["reason_code"] == "prompt_not_approved"


def test_prompt_hash_uses_lf_normalized_utf8(tmp_path: Path) -> None:
    prompt_text = "Classify one synthetic exception event.\nReturn a proposal only.\n"
    prompt_path = tmp_path / "classify_exception_system.txt"
    prompt_path.write_bytes(prompt_text.replace("\n", "\r\n").encode("utf-8"))
    path = _prompt_registry(
        tmp_path,
        prompt_file=str(prompt_path),
        prompt_sha256=_sha256_text(prompt_text),
    )
    code, summary = run(_args(tmp_path, prompt_registry=str(path)))

    assert code == 0
    assert summary["status"] == "ok"
