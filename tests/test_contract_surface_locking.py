from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from lawfirm_os_orchestrator.substrate.contract_lock import validate_contract_checkout  # noqa: E402


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _init_substrate_repo(substrate: Path) -> str:
    _git(substrate, "init")
    _git(substrate, "config", "user.email", "fixture@example.invalid")
    _git(substrate, "config", "user.name", "fixture")
    _git(substrate, "config", "core.longpaths", "true")
    _git(substrate, "add", ".")
    _git(substrate, "commit", "-m", "fixture")
    return _git(substrate, "rev-parse", "HEAD")


def test_contract_surface_lock_ignores_excluded_decision_records(tmp_path: Path) -> None:
    substrate = tmp_path / "LawFirm-os-semantic-substrate"
    substrate.mkdir()
    (substrate / "registry").mkdir()
    (substrate / "schemas").mkdir()
    (substrate / "governance").mkdir()
    (substrate / "schemas" / "x.schema.json").write_text('{"type":"object"}\n', encoding="utf-8")
    (substrate / "registry" / "schema-registry.json").write_text('{"schemas":[]}\n', encoding="utf-8")
    (substrate / "governance" / "EXAMPLE_BOUNDARY.md").write_text("# Boundary\n", encoding="utf-8")
    registry = {
        "schema_version": "contract_surface_registry.v1",
        "registry_id": "contract-surface-registry.v1",
        "default_surface_id": "lawfirm_os_semantic_substrate.consumer_contract_surface.v1",
        "hash_algorithm": "lawfirm_os_contract_surface_sha256.v1",
        "surfaces": [
            {
                "surface_id": "lawfirm_os_semantic_substrate.consumer_contract_surface.v1",
                "description": "test",
                "owning_repo": "LawFirm-os-semantic-substrate",
                "owning_plane": "semantic_substrate",
                "hash_algorithm": "lawfirm_os_contract_surface_sha256.v1",
                "include_patterns": ["schemas/*.schema.json", "registry/schema-registry.json", "governance/*BOUNDARY*.md", "registry/contract-surface-registry.json"],
                "exclude_patterns": ["registry/managed-patch-decisions/**"],
                "consumer_repos": ["LawFirm-os-orchestrator"],
                "unknown_path_policy": "ignore_unless_included",
                "contract_authority_notes": []
            }
        ]
    }
    (substrate / "registry" / "contract-surface-registry.json").write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    # Commit only the included surface files, then compute the expected hash from the committed tree.
    initial_commit = _init_substrate_repo(substrate)
    from lawfirm_os_orchestrator.substrate import contract_lock as cl
    expected = cl._compute_contract_surface_hash(
        substrate,
        surface_id="lawfirm_os_semantic_substrate.consumer_contract_surface.v1",
        registry_path="registry/contract-surface-registry.json",
        commit_ref=initial_commit,
    )

    # Add and COMMIT an excluded managed-patch decision record. The committed surface hash must
    # not change, because managed-patch decisions are excluded from the contract surface.
    decision = substrate / "registry" / "managed-patch-decisions" / "x" / "decision.json"
    decision.parent.mkdir(parents=True)
    decision.write_text('{"audit":"excluded"}\n', encoding="utf-8")
    _git(substrate, "add", ".")
    _git(substrate, "commit", "-m", "audit decision")
    head_after_decision = _git(substrate, "rev-parse", "HEAD")
    observed_after_decision = cl._compute_contract_surface_hash(
        substrate,
        surface_id="lawfirm_os_semantic_substrate.consumer_contract_surface.v1",
        registry_path="registry/contract-surface-registry.json",
        commit_ref=head_after_decision,
    )
    assert observed_after_decision == expected, "managed-patch decisions must not change the contract surface hash"

    lock_path = tmp_path / "contracts.lock.json"
    lock_path.write_text(json.dumps({
        "contract_repo": "LawFirm-os-semantic-substrate",
        "contract_ref_type": "git_sha",
        "contract_sha": head_after_decision,
        "substrate_repo_commit_sha": head_after_decision,
        "contract_surface_lock": {
            "surface_id": "lawfirm_os_semantic_substrate.consumer_contract_surface.v1",
            "surface_sha256": expected,
            "surface_registry_path": "registry/contract-surface-registry.json",
            "hash_algorithm": "lawfirm_os_contract_surface_sha256.v1",
            "computed_from_repo": "LawFirm-os-semantic-substrate",
            "computed_from_commit": head_after_decision,
        },
        "manifest_first_loading": {"preferred_path": "manifests/contract_manifest.v1.json", "fallback_allowed_when_manifest_absent": False, "policy_bundle_id_required": True}
    }, indent=2) + "\n", encoding="utf-8")

    validated = validate_contract_checkout(substrate_root=substrate, lock_path=lock_path, allow_test_fixture=False)
    assert validated.validated_ref_type == "contract_surface_sha256"
    assert validated.validated_ref == expected
