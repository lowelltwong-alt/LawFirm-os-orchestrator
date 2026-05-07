# Canonical Route Mapping Contract

This document maps orchestrator-local route and action labels to the canonical Law Firm OS Semantic Substrate route authority.

Canonical names (from substrate `governance/CROSS_REPO_MAP.md`):

- Substrate: `LawFirm-os-semantic-substrate`
- Orchestrator: `LawFirm-os-orchestrator` (this repo)
- Evidence Lake: `exceptions-lake-runtime-main`

Authoritative substrate sources (paths relative to a local substrate checkout pinned via `contracts.lock.json`):

- `manifests/contract_manifest.v1.json`
- `registry/exception-route-registry.json`
- `registry/orchestrator-contract-export.json`
- `governance/CROSS_REPO_MAP.md`
- `governance/ORCHESTRATOR_BOUNDARY.md`
- `governance/AI_CONTROL_PLANE_BOUNDARY.md`

## Boundary rule

Orchestrator route labels in this repo are operational workflow labels for local execution and planning. They are **not** canonical truth.

Canonical route meaning is defined only by the substrate's `route_id` + `event_class` values in `registry/exception-route-registry.json`. The orchestrator must not invent canonical `route_id` or `event_class` values. It may only reference and validate against the substrate's allowlist.

## Substrate canonical route authority (current)

- `route.retrieval_miss.v1` -> `event_class: retrieval_miss`
- `route.workflow_escalation.v1` -> `event_class: workflow_escalation`
- `route.authority_conflict_override.v1` -> `event_class: authority_conflict_override`

Canonical raw actions (from the substrate route registry):

- allowed raw actions: `route_for_review`, `aggregate_pressure`, `attach_evidence_only`
- prohibited direct actions: `canonical_ontology_write`, `taxonomy_rewrite`, `schema_mutation`, `policy_overwrite`, `address_system_mutation`

## Orchestrator local route label mapping

The orchestrator emits run records and evidence packets. Its local route labels are operational entrypoints. They map to canonical authority only when an exception event is emitted with a canonical `event_class`.

| Orchestrator local label | Local scope | Canonical mapping status | Canonical route_id | Canonical event_class | Notes |
|---|---|---|---|---|---|
| `orchestrator.mvp.classify_exception` | synthetic exception classification CLI route | Partially mapped | `route.retrieval_miss.v1` or `route.workflow_escalation.v1` or `route.authority_conflict_override.v1` | `retrieval_miss` or `workflow_escalation` or `authority_conflict_override` | Local CLI route; canonical mapping depends on the validated payload `event_class`. |
| `orchestrator.mvp.shadow_eval` | shadow eval run | Unmapped (operational eval route) | TBD | TBD | Local eval route; not a canonical exception class. |
| `orchestrator.mvp.upgrade_proposal_build` | local upgrade proposal scaffolding | Unmapped (proposal scaffolding route) | TBD | TBD | Builds local proposal evidence only; does not emit canonical exception events. |
| `orchestrator.mvp.research_radar_local_import` | Research Radar local import | Unmapped (discovery scaffolding route) | TBD | TBD | Local-only file import. No live crawl, no external APIs, no scheduled jobs. |
| `orchestrator.mvp.codex_task_packet_build` | local Codex task packet drafting | Unmapped (proposal scaffolding route) | TBD | TBD | Drafts task packets for human review. Does not execute Codex, Git, patches, model calls, or network calls. |

## Orchestrator action label mapping

| Orchestrator action label | Canonical mapping status | Substrate canonical action | Notes |
|---|---|---|---|
| `classify_exception` | Partially mapped | `route_for_review` | Canonical when a valid exception event is routed for review with a canonical `event_class`. |
| `build_pressure_candidate` | Partially mapped | `aggregate_pressure` | Canonical only when sourced from governed exception evidence. |
| `attach_evidence_packet` | Mapped (evidence handling) | `attach_evidence_only` | Applies when attaching review evidence without mutation authority. |
| `request_human_approval` | Unmapped/TBD | TBD | Operational request; not a canonical exception action. |
| `refresh_contract_lock` | Unmapped/TBD | TBD | Contract maintenance operation. |

## Required orchestrator interpretation

1. Orchestrator routes are implementation labels.
2. Substrate `route_id` and `event_class` are the only canonical authority.
3. If the orchestrator emits or handles exception events, the payload must use one of the substrate canonical `event_class` values and validate against `registry/exception-route-registry.json`.
4. Unmapped/TBD entries are intentionally non-canonical orchestrator operations and must not be treated as canonical route IDs.
5. The orchestrator must not write into the substrate repo path.
6. The orchestrator must fail-closed on contract-lock SHA drift.

## Hard prohibitions

- no real client data, matter data, or privileged content
- no external writes
- no live model calls in the MVP
- no scheduled jobs
- no live Research Radar collection, external APIs, or autonomous research execution
- no canon mutation
- no invented `route_id` or `event_class`
