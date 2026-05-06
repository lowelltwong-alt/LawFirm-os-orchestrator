from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from lawfirm_os_orchestrator.domain.models import CanonicalRoute, SubstrateManifest
from lawfirm_os_orchestrator.util.hashing import sha256_file
from lawfirm_os_orchestrator.util.json_io import read_json


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
    """Read-only substrate client. Intentionally exposes no write methods."""

    def __init__(self, root: Path):
        self.root = root.resolve()

    def load_snapshot(self) -> SubstrateSnapshot:
        manifest_path = self.root / "manifests" / "contract_manifest.v1.json"
        if not manifest_path.exists():
            manifest_path = self.root / "registry" / "orchestrator-contract-export.json"
        route_path = self.root / "registry" / "exception-route-registry.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Missing manifest: {manifest_path}")
        if not route_path.exists():
            raise FileNotFoundError(f"Missing route registry: {route_path}")
        manifest_raw = read_json(manifest_path)
        manifest = SubstrateManifest(
            manifest_id=manifest_raw.get("manifest_id") or manifest_raw.get("contract_name") or "manifest-v1",
            manifest_version=manifest_raw.get("manifest_version") or manifest_raw.get("export_version") or "1.0",
            policy_bundle_id=manifest_raw.get("policy_bundle_id") or "runtime-policy-v1",
            canonical_schema_keys=manifest_raw.get("canonical_schema_keys") or manifest_raw.get("draft_schema_keys") or [],
            registry_refs=manifest_raw.get("registry_refs") or manifest_raw.get("draft_registries") or [],
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
