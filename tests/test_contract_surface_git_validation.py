from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from lawfirm_os_orchestrator.substrate.contract_lock import (
    HASH_ALGORITHM,
    _compute_contract_surface_hash,
    validate_contract_checkout,
)

SEMANTIC_SUBSTRATE = REPO_ROOT.parent / "LawFirm-os-semantic-substrate"
SEMANTIC_SUBSTRATE_SCRIPTS = SEMANTIC_SUBSTRATE / "scripts"

_SURFACE_ID = "lawfirm_os_semantic_substrate.consumer_contract_surface.v1"
_REGISTRY = "registry/contract-surface-registry.json"


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _init_repo_from_substrate(target: Path) -> str:
    target.mkdir(parents=True, exist_ok=True)
    for rel in ("schemas", "registry", "governance", "manifests"):
        src = SEMANTIC_SUBSTRATE / rel
        if src.exists():
            shutil.copytree(src, target / rel)
    _git(target, "init")
    _git(target, "config", "user.email", "fixture@example.invalid")
    _git(target, "config", "user.name", "fixture")
    _git(target, "config", "core.longpaths", "true")
    _git(target, "add", ".")
    _git(target, "commit", "-m", "fixture")
    return _git(target, "rev-parse", "HEAD")


def _write_surface_lock(path: Path, *, contract_sha: str, surface_sha256: str) -> None:
    lock = {
        "contract_repo": "LawFirm-os-semantic-substrate",
        "contract_ref_type": "git_sha",
        "contract_sha": contract_sha,
        "substrate_repo_commit_sha": contract_sha,
        "generated_at": "2026-05-17T00:00:00Z",
        "generated_by": "test",
        "manifest_first_loading": {
            "preferred_path": "manifests/contract_manifest.v1.json",
            "fallback_allowed_when_manifest_absent": False,
            "policy_bundle_id_required": True,
        },
        "contract_surface_lock": {
            "surface_id": _SURFACE_ID,
            "surface_sha256": surface_sha256,
            "surface_registry_path": _REGISTRY,
            "hash_algorithm": HASH_ALGORITHM,
            "computed_from_repo": "LawFirm-os-semantic-substrate",
            "computed_from_commit": contract_sha,
        },
    }
    path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")


@pytest.fixture
def fixture_substrate_repo(tmp_path: Path):
    if not SEMANTIC_SUBSTRATE.is_dir():
        pytest.skip("Sibling LawFirm-os-semantic-substrate not found")
    root = tmp_path / "LawFirm-os-semantic-substrate"
    commit = _init_repo_from_substrate(root)
    return root, commit


def test_committed_tree_surface_matches_canonical_script(fixture_substrate_repo) -> None:
    if not SEMANTIC_SUBSTRATE_SCRIPTS.is_dir():
        pytest.skip("Sibling LawFirm-os-semantic-substrate/scripts not found")
    root, commit = fixture_substrate_repo
    env = {**os.environ, "PYTHONPATH": str(SEMANTIC_SUBSTRATE_SCRIPTS)}
    proc = subprocess.run(
        [
            sys.executable,
            str(SEMANTIC_SUBSTRATE_SCRIPTS / "compute_contract_surface_hash.py"),
            "--substrate",
            str(root),
            "--ref",
            commit,
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    canonical = json.loads(proc.stdout)
    observed = _compute_contract_surface_hash(
        root,
        surface_id=_SURFACE_ID,
        registry_path=_REGISTRY,
        commit_ref=commit,
    )
    assert observed == canonical["surface_sha256"]


def test_working_tree_crlf_does_not_affect_committed_surface_hash(fixture_substrate_repo, tmp_path: Path) -> None:
    root, commit = fixture_substrate_repo
    expected = _compute_contract_surface_hash(
        root,
        surface_id=_SURFACE_ID,
        registry_path=_REGISTRY,
        commit_ref=commit,
    )
    victim = next((root / "schemas").glob("*.schema.json"), None)
    assert victim is not None
    original_bytes = victim.read_bytes()
    try:
        crlf = original_bytes.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        victim.write_bytes(crlf)
        observed = _compute_contract_surface_hash(
            root,
            surface_id=_SURFACE_ID,
            registry_path=_REGISTRY,
            commit_ref=commit,
        )
        assert observed == expected, (
            "Validator must hash committed git-blob bytes (LF) and ignore mutable working-tree bytes (CRLF on Windows)."
        )
    finally:
        victim.write_bytes(original_bytes)


def test_copytree_without_git_fails_closed_even_with_complete_registry(fixture_substrate_repo, tmp_path: Path) -> None:
    """A shutil.copytree of a complete substrate without a .git checkout must not silently pass.

    This is the contract surface hash bug class: the lock claims computed_from_commit, but the
    consumer has no git checkout, so it cannot read committed blob bytes for that commit.
    The validator must refuse to fall back to working-tree filesystem bytes (which on Windows
    may differ from the LF-normalized committed bytes due to core.autocrlf).
    """
    root, commit = fixture_substrate_repo
    expected = _compute_contract_surface_hash(
        root,
        surface_id=_SURFACE_ID,
        registry_path=_REGISTRY,
        commit_ref=commit,
    )
    archive_parent = tmp_path / "archive"
    archive_parent.mkdir()
    archive_root = archive_parent / "LawFirm-os-semantic-substrate"
    archive_root.mkdir()
    for rel in ("schemas", "registry", "governance", "manifests"):
        src = root / rel
        if src.exists():
            shutil.copytree(src, archive_root / rel)
    assert (archive_root / _REGISTRY).exists(), "registry must be present in archive copy"
    assert not (archive_root / ".git").exists(), "archive must not be a git checkout"
    lock_path = tmp_path / "contracts.lock.json"
    _write_surface_lock(lock_path, contract_sha=commit, surface_sha256=expected)
    with pytest.raises(ValueError, match="not a git checkout"):
        validate_contract_checkout(substrate_root=archive_root, lock_path=lock_path, allow_test_fixture=False)


def test_missing_pinned_commit_in_git_checkout_fails_closed(fixture_substrate_repo, tmp_path: Path) -> None:
    """If the local git repo doesn't contain the locked commit, validation must fail-closed."""
    root, _commit = fixture_substrate_repo
    fake_commit = "f" * 40
    lock_path = tmp_path / "contracts.lock.json"
    _write_surface_lock(lock_path, contract_sha=fake_commit, surface_sha256="a" * 64)
    with pytest.raises(ValueError, match="not present in the substrate git object database"):
        validate_contract_checkout(substrate_root=root, lock_path=lock_path, allow_test_fixture=False)


def test_committed_tree_hash_validates_on_real_git_checkout(fixture_substrate_repo, tmp_path: Path) -> None:
    root, commit = fixture_substrate_repo
    expected = _compute_contract_surface_hash(
        root,
        surface_id=_SURFACE_ID,
        registry_path=_REGISTRY,
        commit_ref=commit,
    )
    lock_path = tmp_path / "contracts.lock.json"
    _write_surface_lock(lock_path, contract_sha=commit, surface_sha256=expected)
    validated = validate_contract_checkout(substrate_root=root, lock_path=lock_path, allow_test_fixture=False)
    assert validated.validated_ref_type == "contract_surface_sha256"
    assert validated.validated_ref == expected
