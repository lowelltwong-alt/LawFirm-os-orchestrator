# Recent Work

## Agent-hostile control layer completed

Completed the first mature agent-hostile control layer across LawFirm OS.

- Semantic Substrate now owns canonical agent-control schemas and registries.
- Orchestrator enforces substrate-backed prompt, tool, endpoint, and revocation controls.
- Evidence packets record agent-control provenance, including source, registry path, registry hash, contract SHA, and per-registry hashes.
- Consumer repos refreshed `contracts.lock.json` to the new Substrate contract surface.
- Prompt integrity hashing is LF-normalized for cross-platform stability across Windows CRLF and canonical LF text artifacts.

Authority boundary:
- Semantic Substrate owns governance contracts and canonical meaning.
- Orchestrator owns runtime enforcement and evidence-packet assembly.
- Exception Lake and other consumers remain pinned to Substrate contracts and must not redefine canon.

Related merged work:
- Semantic Substrate: agent-hostile control contracts.
- Orchestrator: substrate-backed enforcement.
- Orchestrator: prompt-integrity LF normalization.
- Exception Lake, Skills Registry, and Legal Knowledge Runtime: contract lock refreshes.

## 2026-05-07 - Kernel A+ Runtime-Safe Handoff Patch

- Added explicit archive-tree contract validation mode alongside the existing git SHA lock. Git checkouts still validate against `contract_sha`; extracted archives validate only against the separate `archive_tree_sha256` lock field.
- Recorded contract validation results in ledger records, `substrate_snapshot.json`, and `packet.json`.
- Added `lake/envelope.py` to map orchestrator classifications into Exception Lake `exception-event` payloads using route-owned fields from the Substrate route registry.
- Wired `runtime-safe` Lake mode to the Exception Lake API behind dual opt-in: `--lake-mode runtime-safe` plus `LAWFIRM_OS_ORCHESTRATOR_ALLOW_RUNTIME_SAFE=true`.
- Added cross-repo smoke coverage for live sibling Substrate loading and final evidence packet manifest/hash integrity.
- Preserved default Lake mode as disabled, synthetic-only input policy, no Substrate writes, no route/event invention, and fail-closed contract behavior.

## 2026-05-07 - Substrate Contract Lock Sync

- Refreshed `contracts.lock.json` to pin the currently released Semantic Substrate commit `43991155f0286e6d8bc5ba0bfe6b42407b1b3f12`.
- Updated the contract-lock regression expectation and AI table of contents so runtime checks, documentation, and the attached substrate export agree.
- Aligned the read-only route model with substrate-owned route metadata fields (`destination_loop`, `allowed_follow_on_families`) exposed by the released substrate checkout.
- Removed local defaults from `SubstrateManifest` required fields so direct model construction cannot silently supply manifest authority values.
- Contract surfaces between the older `d2ac7f504e67aa00985fbe53aa5350f940e8b529` pin and `43991155f0286e6d8bc5ba0bfe6b42407b1b3f12` were checked across manifest, registry, schema, governance, and front-door paths; no contract-surface content drift was found.
- No schemas, route IDs, event classes, runtime authority, Research Radar automation, model calls, external APIs, external writes, Substrate writes, or Exception Lake writes were added.

## PR04 - Inert Codex task packet builder

- Added local Codex task packet generation from opportunity, scorecard, autonomy, and harness inputs.
- Added inert agent review plan construction for review-scope records only.
- Added CLI command `generate-codex-task`.
- Preserved authority boundaries: packets are build instructions only and do not execute Codex, Git, patches, tests, models, tools, network, Substrate writes, or Lake writes.
- Left PR05, PR06, and PR07 as future phases.

## PR03 - Orchestrator green-lane assumption watcher

- Added local green-lane passport and assumption-signal mapping support.
- Added deterministic red/yellow trigger detection and downgrade-only reclassification output.
- Added CLI command `watch-green-lanes`.
- Preserved green authority boundary: agents may downgrade or recommend green-candidate, but humans restore green.
- Preserved local-only operation: no live Research Radar automation, model calls, scheduled jobs, external APIs, external writes, Git execution, Semantic Substrate writes, or Exception Lake writes.

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
