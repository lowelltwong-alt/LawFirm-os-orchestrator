from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from lawfirm_os_orchestrator.domain.models import CanonicalRoute, SubstrateManifest
from lawfirm_os_orchestrator.util.hashing import sha256_file
from lawfirm_os_orchestrator.util.json_io import read_json


CANONICAL_MANIFEST_RELATIVE_PATH = Path("manifests") / "contract_manifest.v1.json"
ROUTE_REGISTRY_RELATIVE_PATH = Path("registry") / "exception-route-registry.json"

REQUIRED_MANIFEST_FIELDS = (
    "manifest_id",
    "manifest_version",
    "policy_bundle_id",
    "canonical_schema_keys",
    "registry_refs",
)


@dataclass(frozen=True)
class SubstrateSnapshot:
    root: Path
    manifest: SubstrateManifest
    manifest_hash: str
    routes: list[CanonicalRoute]
    route_registry_hash: str

    @property
    def allowed_route_ids(self) -> list[str]:
        return [route.route_id for route in self.routes]

    @property
    def allowed_event_classes(self) -> list[str]:
        return [route.event_class for route in self.routes]

    def event_class_for_route(self, route_id: str) -> str | None:
        for route in self.routes:
            if route.route_id == route_id:
                return route.event_class
        return None


class PathSubstrateClient:
    """Read-only substrate client. Intentionally exposes no write methods.

    The substrate must publish manifests/contract_manifest.v1.json (the
    canonical orchestrator-facing manifest). Loading is fail-closed when
    the manifest is missing or any required field is absent. See the
    substrate's governance/ORCHESTRATOR_BOUNDARY.md for the field contract.
    """

    def __init__(self, root: Path):
        self.root = root.resolve()

    def load_snapshot(self) -> SubstrateSnapshot:
        manifest_path = self.root / CANONICAL_MANIFEST_RELATIVE_PATH
        route_path = self.root / ROUTE_REGISTRY_RELATIVE_PATH
        if not manifest_path.exists():
            raise FileNotFoundError(
                "Missing canonical orchestrator manifest at "
                f"{manifest_path}. The substrate must publish "
                "manifests/contract_manifest.v1.json. See the substrate's "
                "governance/ORCHESTRATOR_BOUNDARY.md for required keys."
            )
        if not route_path.exists():
            raise FileNotFoundError(f"Missing route registry: {route_path}")
        manifest_raw = read_json(manifest_path)
        missing = [field for field in REQUIRED_MANIFEST_FIELDS if manifest_raw.get(field) is None]
        if missing:
            raise ValueError(
                f"Canonical orchestrator manifest {manifest_path} is missing "
                f"required fields: {missing}. See the substrate's "
                "governance/ORCHESTRATOR_BOUNDARY.md."
            )
        manifest = SubstrateManifest(
            manifest_id=manifest_raw["manifest_id"],
            manifest_version=manifest_raw["manifest_version"],
            policy_bundle_id=manifest_raw["policy_bundle_id"],
            canonical_schema_keys=manifest_raw["canonical_schema_keys"],
            registry_refs=manifest_raw["registry_refs"],
        )
        route_raw = read_json(route_path)
        routes = [CanonicalRoute.model_validate(route) for route in route_raw.get("routes", [])]
        if not routes:
            raise ValueError("Route registry contains no routes")
        return SubstrateSnapshot(
            root=self.root,
            manifest=manifest,
            manifest_hash=sha256_file(manifest_path),
            routes=routes,
            route_registry_hash=sha256_file(route_path),
        )
