from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from lawfirm_os_orchestrator.substrate.contract_lock import (
    archive_tree_sha256,
    contract_lock_record,
    validate_contract_checkout,
)

ROOT = Path(__file__).resolve().parents[1]


def _write_lock(path: Path, *, contract_sha: str = "1" * 40, archive_hash: str | None = None) -> None:
    document = {
        "contract_repo": "LawFirm-os-semantic-substrate",
        "contract_ref_type": "git_sha",
        "contract_sha": contract_sha,
        "generated_at": "2026-05-07T00:00:00Z",
        "generated_by": "test",
        "archive_tree_sha256": archive_hash,
        "manifest_first_loading": {
            "preferred_path": "manifests/contract_manifest.v1.json",
            "fallback_allowed_when_manifest_absent": False,
            "policy_bundle_id_required": True,
        },
    }
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def test_git_checkout_validates_against_locked_sha(tmp_path: Path) -> None:
    substrate = tmp_path / "LawFirm-os-semantic-substrate"
    shutil.copytree(ROOT / "tests" / "fixtures" / "substrate", substrate)
    git_dir = substrate / ".git"
    (git_dir / "refs" / "heads").mkdir(parents=True)
    (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (git_dir / "refs" / "heads" / "main").write_text("1" * 40 + "\n", encoding="utf-8")
    lock_path = tmp_path / "contracts.lock.json"
    _write_lock(lock_path)

    lock = validate_contract_checkout(substrate_root=substrate, lock_path=lock_path)

    assert lock.validated_ref_type == "git_sha"
    assert lock.validated_ref == "1" * 40
    assert contract_lock_record(lock)["validated_ref"] == "1" * 40


def test_archive_tree_requires_explicit_matching_hash(tmp_path: Path) -> None:
    substrate = tmp_path / "LawFirm-os-semantic-substrate"
    shutil.copytree(ROOT / "tests" / "fixtures" / "substrate", substrate)
    expected_hash = archive_tree_sha256(substrate)
    lock_path = tmp_path / "contracts.lock.json"
    _write_lock(lock_path, archive_hash=expected_hash)

    lock = validate_contract_checkout(substrate_root=substrate, lock_path=lock_path)

    assert lock.validated_ref_type == "archive_tree_sha256"
    assert lock.validated_ref == expected_hash


def test_archive_tree_fails_closed_on_drift(tmp_path: Path) -> None:
    substrate = tmp_path / "LawFirm-os-semantic-substrate"
    shutil.copytree(ROOT / "tests" / "fixtures" / "substrate", substrate)
    lock_path = tmp_path / "contracts.lock.json"
    _write_lock(lock_path, archive_hash="0" * 64)

    with pytest.raises(ValueError, match="archive tree hash"):
        validate_contract_checkout(substrate_root=substrate, lock_path=lock_path)
