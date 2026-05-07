# Recent Work

## PR02 - Orchestrator autonomy gate and harness selector

- Added local deterministic autonomy classification for red/yellow/green execution-plane decisions.
- Added local hardness scoring, leverage scoring, and harness plan selection.
- Added CLI commands `classify-autonomy` and `select-harness`.
- Updated safety scanning so new local-only modules cannot import process or network modules.
- Preserved substrate authority: no canonical route IDs, event classes, schemas, governance doctrine, or promotion authority are defined here.
- Preserved runtime boundaries: no live Research Radar automation, model calls, scheduled jobs, external APIs, external writes, Semantic Substrate writes, or Exception Lake writes.

## 2026-05-06 - Phase 2 Front-Door Documentation Completion

Codex task / PR: Final verification gap cleanup for root AI front-door docs.

Files changed:
- Added `AI_TABLE_OF_CONTENTS.md` to orient future AI work around execution-plane boundaries, manifest-first substrate consumption, current command surfaces, and local-only Phase 2 learning/research scaffolds.
- Added `ENDPOINTS_AND_COMMANDS.md` to list current CLI and script surfaces. The document states that the repo has no HTTP server, daemon, MCP server mode, production connectors, live Research Radar automation, model calls, external APIs, or external writes.
- Added `DATA_FLOW_MAP.md` with Mermaid-ready execution-plane flow and sequence diagrams. The map shows control-plane read-only substrate consumption, local ledger/evidence packet output, disabled-by-default Exception Lake handoff, proposal-only learning artifacts, and human-approved promotion outside runtime.

Schemas changed:
- None.

Contracts changed:
- None. `contracts.lock.json` unchanged.

Runtime behavior changed:
- None.

Risk color:
- Green. Documentation-only front-door completion.

Harness level:
- H0 documentation alignment plus existing validation.

## 2026-05-06 — Cross-Repo Coherence Patch 3: Substrate Manifest Consumption And Canonical Route Mapping

Codex task / PR: Cross-repo coherence fix train Patch 3 (orchestrator side).

Files changed:
- Updated `src/lawfirm_os_orchestrator/substrate/reader.py` to consume the canonical orchestrator manifest (`manifests/contract_manifest.v1.json`) directly. Removed the silent fallback to `registry/orchestrator-contract-export.json` and removed the `or`-chained alias mapping. Added `REQUIRED_MANIFEST_FIELDS` and a fail-closed missing-fields check. The reader no longer silently defaults `policy_bundle_id`.
- Refreshed `contracts.lock.json` to pin the substrate at commit `d2ac7f504e67aa00985fbe53aa5350f940e8b529` (substrate Patch 1 + Patch 2). Renamed `contract_repo` to the canonical `LawFirm-os-semantic-substrate`. Renamed `generated_by` to `LawFirm-os-orchestrator`. Added `contract_repo_human_label`, `manifest_first_loading` block, and an expanded `non_claims` list (live model calls, scheduled jobs, live research crawling, external APIs, external writes, invented route_id/event_class).
- Added non-authoritative metadata header to `config/research_sources.yaml`: `phase: pre-pr07-draft`, `non_authoritative: true`, `metadata_only: true`, and explicit `authorizes_*: false` flags for live collection, external API use, model calls, external writes, and scheduled jobs. Cross-references substrate `registry/research-radar-source-registry.json`.
- Added `docs/CANONICAL_ROUTE_MAPPING.md` modeled on the Exception Lake pattern. Maps orchestrator local route labels (e.g. `orchestrator.mvp.classify_exception`, `orchestrator.mvp.shadow_eval`) to substrate canonical `route_id`/`event_class` values. States the "operational labels are not canonical" boundary rule explicitly.
- Updated `README.md` with canonical names, manifest-first loading discipline, contract-lock fields, and an expanded safety-boundaries list.
- Updated `AGENTS.md` with canonical names, manifest-first loading reference, and a CANONICAL_ROUTE_MAPPING.md read pointer.
- Updated `AI_WORK_START_HERE.md` with canonical names, sibling-repo references, manifest-first loading discipline, and an expanded allowed-paths list (`config/**`, `contracts.lock.json`).

Schemas changed:
- None.

Commands/endpoints changed:
- None. CLI surface unchanged.

Data flow changed:
- Substrate consumption is now manifest-first only. Fallback to `registry/orchestrator-contract-export.json` removed. Required manifest fields fail-close on absence.

Tests added/updated:
- None added in this patch. Existing test fixture `tests/fixtures/substrate/manifests/contract_manifest.v1.json` already carries all required fields and is preserved.

Risk color:
- Yellow. Tightens contract consumption with fail-closed semantics.

Hardness/harness level:
- H2. Planner plus implementation plus tests.

Leverage rationale:
- Eliminates silent shape coercion. The reader now requires the canonical manifest with all stable fields. Future schema/registry/manifest changes in the substrate must be accompanied by an explicit lock refresh, surfacing coupling that was previously hidden.

Follow-up:
- Patch 4 will refresh `exceptions-lake-runtime-main/contracts.lock.json` against substrate `d2ac7f5` and replace placeholder repo identity with the canonical `LawFirm-os-semantic-substrate`.

Out-of-scope cleanups (deferred):
- `src/lawfirm_os_orchestrator/domain/models.py:50` keeps `policy_bundle_id: str = "runtime-policy-v1"` as a dataclass default. This default is no longer reachable through the reader (the reader now requires the field from the manifest). The default can be removed in a separate cleanup PR if any direct construction of `SubstrateManifest` would be unaffected.
