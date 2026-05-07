from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.util.json_io import read_json

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_LOCK_PATH = REPO_ROOT / "contracts.lock.json"
TEST_FIXTURE_SUBSTRATE_ROOT = (REPO_ROOT / "tests" / "fixtures" / "substrate").resolve()


@dataclass(frozen=True)
class ContractLock:
    contract_repo: str
    contract_ref_type: str
    contract_sha: str
    preferred_manifest_path: str
    fallback_allowed_when_manifest_absent: bool
    policy_bundle_id_required: bool


def load_contract_lock(path: Path = DEFAULT_CONTRACT_LOCK_PATH) -> ContractLock:
    raw: dict[str, Any] = read_json(path)
    manifest_loading = raw.get("manifest_first_loading", {})
    lock = ContractLock(
        contract_repo=str(raw.get("contract_repo", "")),
        contract_ref_type=str(raw.get("contract_ref_type", "")),
        contract_sha=str(raw.get("contract_sha", "")),
        preferred_manifest_path=str(manifest_loading.get("preferred_path", "")),
        fallback_allowed_when_manifest_absent=bool(manifest_loading.get("fallback_allowed_when_manifest_absent", True)),
        policy_bundle_id_required=bool(manifest_loading.get("policy_bundle_id_required", False)),
    )
    missing = [field for field, value in lock.__dict__.items() if value in ("", None)]
    if missing:
        raise ValueError(f"contracts.lock.json is missing required fields: {missing}")
    if lock.contract_ref_type != "git_sha":
        raise ValueError(f"unsupported contract_ref_type: {lock.contract_ref_type}")
    if len(lock.contract_sha) != 40:
        raise ValueError("contracts.lock.json contract_sha must be a full 40-character git SHA")
    if lock.fallback_allowed_when_manifest_absent:
        raise ValueError("contracts.lock.json must fail closed when the manifest is absent")
    if not lock.policy_bundle_id_required:
        raise ValueError("contracts.lock.json must require policy_bundle_id")
    return lock


def _git_dir(root: Path) -> Path | None:
    marker = root / ".git"
    if marker.is_dir():
        return marker
    if marker.is_file():
        text = marker.read_text(encoding="utf-8").strip()
        prefix = "gitdir:"
        if text.lower().startswith(prefix):
            git_path = Path(text[len(prefix) :].strip())
            return git_path if git_path.is_absolute() else (root / git_path).resolve()
    return None


def _read_packed_ref(git_dir: Path, ref: str) -> str | None:
    packed = git_dir / "packed-refs"
    if not packed.exists():
        return None
    for line in packed.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith(("#", "^")):
            continue
        try:
            sha, name = line.split(" ", 1)
        except ValueError:
            continue
        if name == ref:
            return sha
    return None


def resolve_git_head(root: Path) -> str | None:
    git_dir = _git_dir(root)
    if git_dir is None:
        return None
    head_path = git_dir / "HEAD"
    if not head_path.exists():
        return None
    head = head_path.read_text(encoding="utf-8").strip()
    ref_prefix = "ref:"
    if not head.startswith(ref_prefix):
        return head
    ref = head[len(ref_prefix) :].strip()
    ref_path = git_dir / ref
    if ref_path.exists():
        return ref_path.read_text(encoding="utf-8").strip()
    return _read_packed_ref(git_dir, ref)


def validate_contract_checkout(
    *,
    substrate_root: Path,
    lock_path: Path = DEFAULT_CONTRACT_LOCK_PATH,
    allow_test_fixture: bool = True,
) -> ContractLock:
    lock = load_contract_lock(lock_path)
    root = substrate_root.resolve()
    if root == TEST_FIXTURE_SUBSTRATE_ROOT and allow_test_fixture:
        return lock
    if root.name != lock.contract_repo:
        raise ValueError(f"substrate path {root} does not match locked contract repo {lock.contract_repo}")
    head = resolve_git_head(root)
    if head is None:
        raise ValueError(f"substrate path {root} is not a readable git checkout for locked contracts")
    if head != lock.contract_sha:
        raise ValueError(f"substrate git SHA {head} does not match contracts.lock.json SHA {lock.contract_sha}")
    return lock
