from __future__ import annotations

import fnmatch
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.util.json_io import read_json

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_LOCK_PATH = REPO_ROOT / "contracts.lock.json"
TEST_FIXTURE_SUBSTRATE_ROOT = (REPO_ROOT / "tests" / "fixtures" / "substrate").resolve()
HASH_ALGORITHM = "lawfirm_os_contract_surface_sha256.v1"


@dataclass(frozen=True)
class ContractLock:
    contract_repo: str
    contract_ref_type: str
    contract_sha: str
    archive_tree_sha256: str | None
    preferred_manifest_path: str
    fallback_allowed_when_manifest_absent: bool
    policy_bundle_id_required: bool
    contract_surface_id: str | None = None
    contract_surface_sha256: str | None = None
    contract_surface_registry_path: str | None = None
    contract_surface_algorithm: str | None = None
    substrate_repo_commit_sha: str | None = None
    validated_ref_type: str | None = None
    validated_ref: str | None = None


def load_contract_lock(path: Path = DEFAULT_CONTRACT_LOCK_PATH) -> ContractLock:
    raw: dict[str, Any] = read_json(path)
    manifest_loading = raw.get("manifest_first_loading", {})
    surface = raw.get("contract_surface_lock") if isinstance(raw.get("contract_surface_lock"), dict) else {}
    lock = ContractLock(
        contract_repo=str(raw.get("contract_repo", "")),
        contract_ref_type=str(raw.get("contract_ref_type", "")),
        contract_sha=str(raw.get("contract_sha", "")),
        archive_tree_sha256=raw.get("archive_tree_sha256"),
        substrate_repo_commit_sha=raw.get("substrate_repo_commit_sha"),
        preferred_manifest_path=str(manifest_loading.get("preferred_path", "")),
        fallback_allowed_when_manifest_absent=bool(manifest_loading.get("fallback_allowed_when_manifest_absent", True)),
        policy_bundle_id_required=bool(manifest_loading.get("policy_bundle_id_required", False)),
        contract_surface_id=surface.get("surface_id"),
        contract_surface_sha256=surface.get("surface_sha256"),
        contract_surface_registry_path=surface.get("surface_registry_path", "registry/contract-surface-registry.json"),
        contract_surface_algorithm=surface.get("hash_algorithm"),
    )
    missing = [
        field
        for field in ("contract_repo", "contract_ref_type", "contract_sha", "preferred_manifest_path")
        if getattr(lock, field) in ("", None)
    ]
    if missing:
        raise ValueError(f"contracts.lock.json is missing required fields: {missing}")
    if lock.contract_ref_type != "git_sha":
        raise ValueError(f"unsupported contract_ref_type: {lock.contract_ref_type}")
    if len(lock.contract_sha) != 40:
        raise ValueError("contracts.lock.json contract_sha must be a full 40-character git SHA")
    if lock.archive_tree_sha256 is not None and len(lock.archive_tree_sha256) != 64:
        raise ValueError("contracts.lock.json archive_tree_sha256 must be a 64-character SHA-256 hex digest")
    if lock.contract_surface_sha256 is not None and len(lock.contract_surface_sha256) != 64:
        raise ValueError("contract_surface_lock.surface_sha256 must be a 64-character SHA-256 hex digest")
    if lock.contract_surface_sha256 is not None and lock.contract_surface_algorithm != HASH_ALGORITHM:
        raise ValueError("contract_surface_lock.hash_algorithm is unsupported")
    if lock.fallback_allowed_when_manifest_absent:
        raise ValueError("contracts.lock.json must fail closed when the manifest is absent")
    if not lock.policy_bundle_id_required:
        raise ValueError("contracts.lock.json must require policy_bundle_id")
    return lock


def contract_lock_record(lock: ContractLock) -> dict[str, Any]:
    return {
        "contract_repo": lock.contract_repo,
        "contract_ref_type": lock.contract_ref_type,
        "contract_sha": lock.contract_sha,
        "archive_tree_sha256": lock.archive_tree_sha256,
        "substrate_repo_commit_sha": lock.substrate_repo_commit_sha,
        "contract_surface_id": lock.contract_surface_id,
        "contract_surface_sha256": lock.contract_surface_sha256,
        "contract_surface_registry_path": lock.contract_surface_registry_path,
        "validated_ref_type": lock.validated_ref_type,
        "validated_ref": lock.validated_ref,
        "preferred_manifest_path": lock.preferred_manifest_path,
        "fallback_allowed_when_manifest_absent": lock.fallback_allowed_when_manifest_absent,
        "policy_bundle_id_required": lock.policy_bundle_id_required,
    }


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


def archive_tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in {".git", "__pycache__", ".pytest_cache", ".ruff_cache"} for part in relative.parts):
            continue
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _matches(rel: str, pattern: str) -> bool:
    rel = rel.replace("\\", "/")
    pattern = pattern.replace("\\", "/")
    if fnmatch.fnmatch(rel, pattern):
        return True
    if pattern.endswith("/**"):
        return rel.startswith(pattern[:-3].rstrip("/") + "/")
    if pattern.endswith("/**/*"):
        return rel.startswith(pattern[:-5].rstrip("/") + "/")
    if "/**/" in pattern and fnmatch.fnmatch(rel, pattern.replace("/**/", "/")):
        return True
    return False


def _git_show_bytes(root: Path, ref: str, rel_path: str) -> bytes | None:
    try:
        return subprocess.run(
            ["git", "show", f"{ref}:{rel_path}"],
            cwd=root,
            capture_output=True,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def _git_object_exists(root: Path, ref: str) -> bool:
    try:
        subprocess.run(
            ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
            cwd=root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def _git_ls_tree(root: Path, ref: str) -> list[str] | None:
    try:
        raw = subprocess.run(
            ["git", "ls-tree", "-r", "-z", "--name-only", ref],
            cwd=root,
            capture_output=True,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return sorted(rel for rel in raw.decode("utf-8").split("\0") if rel)


def _compute_contract_surface_hash(
    root: Path,
    *,
    surface_id: str,
    registry_path: str,
    commit_ref: str | None = None,
) -> str:
    git_dir = _git_dir(root)
    use_git = commit_ref is not None and git_dir is not None
    registry_bytes: bytes | None = None
    if use_git:
        registry_bytes = _git_show_bytes(root, commit_ref, registry_path)
        if registry_bytes is None:
            raise ValueError(
                f"substrate git tree does not contain locked commit {commit_ref} or registry {registry_path}"
            )
    else:
        registry_file = root / registry_path
        if not registry_file.exists():
            raise ValueError("contract surface registry missing")
        registry_bytes = registry_file.read_bytes()
    try:
        registry = json.loads(registry_bytes.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"contract surface registry is not valid JSON: {exc}") from exc
    surface = None
    for candidate in registry.get("surfaces", []):
        if candidate.get("surface_id") == surface_id:
            surface = candidate
            break
    if surface is None:
        raise ValueError(f"unknown contract surface id: {surface_id}")
    include_patterns = list(surface.get("include_patterns", []))
    exclude_patterns = list(surface.get("exclude_patterns", []))
    items: list[tuple[str, str, int]] = []
    if use_git:
        rel_paths = _git_ls_tree(root, commit_ref)
        if rel_paths is None:
            raise ValueError(f"cannot enumerate substrate git tree at {commit_ref}")
        for rel in rel_paths:
            if any(part in {".git", "__pycache__", ".pytest_cache", ".ruff_cache"} for part in Path(rel).parts):
                continue
            if not any(_matches(rel, pat) for pat in include_patterns):
                continue
            if any(_matches(rel, pat) for pat in exclude_patterns):
                continue
            data = _git_show_bytes(root, commit_ref, rel)
            if data is None:
                raise ValueError(f"cannot read {rel} from substrate git tree {commit_ref}")
            items.append((rel, hashlib.sha256(data).hexdigest(), len(data)))
    else:
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            if any(part in {".git", "__pycache__", ".pytest_cache", ".ruff_cache"} for part in Path(rel).parts):
                continue
            if not any(_matches(rel, pat) for pat in include_patterns):
                continue
            if any(_matches(rel, pat) for pat in exclude_patterns):
                continue
            data = path.read_bytes()
            items.append((rel, hashlib.sha256(data).hexdigest(), len(data)))
    if not items:
        raise ValueError("contract surface selected zero files")
    digest = hashlib.sha256()
    digest.update(HASH_ALGORITHM.encode("utf-8"))
    digest.update(b"\0")
    digest.update(surface_id.encode("utf-8"))
    digest.update(b"\0")
    for rel, file_hash, size in items:
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\0")
        digest.update(str(size).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def validate_contract_checkout(*, substrate_root: Path, lock_path: Path = DEFAULT_CONTRACT_LOCK_PATH, allow_test_fixture: bool = True) -> ContractLock:
    lock = load_contract_lock(lock_path)
    root = substrate_root.resolve()
    if root == TEST_FIXTURE_SUBSTRATE_ROOT and allow_test_fixture:
        return lock
    if root.name != lock.contract_repo:
        raise ValueError(f"substrate path {root} does not match locked contract repo {lock.contract_repo}")

    if lock.contract_surface_sha256:
        commit_ref = lock.substrate_repo_commit_sha or lock.contract_sha
        git_dir = _git_dir(root)
        if git_dir is None:
            raise ValueError(
                "contracts.lock.json pins contract_surface_lock to committed Git tree bytes "
                "(substrate_repo_commit_sha / contract_sha), but substrate_root is not a git checkout. "
                "Use a full Semantic Substrate clone so committed blob bytes can be validated, "
                "rather than mutable working-tree bytes that may differ on Windows (CRLF vs LF)."
            )
        if not _git_object_exists(root, commit_ref):
            raise ValueError(
                f"Pinned Semantic Substrate commit {commit_ref} is not present in the substrate git object database. "
                "Fetch that commit from origin or point substrate_root at a checkout that contains it."
            )
        observed = _compute_contract_surface_hash(
            root,
            surface_id=lock.contract_surface_id or "lawfirm_os_semantic_substrate.consumer_contract_surface.v1",
            registry_path=lock.contract_surface_registry_path or "registry/contract-surface-registry.json",
            commit_ref=commit_ref,
        )
        if observed != lock.contract_surface_sha256:
            raise ValueError(
                f"substrate contract surface hash {observed} does not match contracts.lock.json surface hash {lock.contract_surface_sha256}"
            )
        return ContractLock(**{**lock.__dict__, "validated_ref_type": "contract_surface_sha256", "validated_ref": observed})

    # Legacy whole-repo commit/archive behavior.
    head = resolve_git_head(root)
    if head is not None:
        if head != lock.contract_sha:
            raise ValueError(f"substrate git SHA {head} does not match contracts.lock.json SHA {lock.contract_sha}")
        return ContractLock(**{**lock.__dict__, "validated_ref_type": "git_sha", "validated_ref": head})
    if lock.archive_tree_sha256 is None:
        raise ValueError(
            f"substrate path {root} is not a readable git checkout and contracts.lock.json does not include explicit archive_tree_sha256"
        )
    observed_tree_hash = archive_tree_sha256(root)
    if observed_tree_hash != lock.archive_tree_sha256:
        raise ValueError(
            "substrate archive tree hash "
            f"{observed_tree_hash} does not match contracts.lock.json archive_tree_sha256 {lock.archive_tree_sha256}"
        )
    return ContractLock(**{**lock.__dict__, "validated_ref_type": "archive_tree_sha256", "validated_ref": observed_tree_hash})
