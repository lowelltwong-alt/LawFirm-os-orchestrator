# AI Table Of Contents

Canonical machine name: `LawFirm-os-orchestrator`. Plane: execution.

This repo executes bounded local workflows and builds evidence packets. It consumes the Semantic Substrate read-only and does not define canonical schemas, route IDs, event classes, governance doctrine, or promotion authority.

## Start Here

- `AI_WORK_START_HERE.md` - current AI work router and stop conditions.
- `AGENTS.md` - agent-facing boundary rules.
- `README.md` - project purpose, quickstart, and safety posture.
- `RECENT_WORK.md` - latest local changes and validation notes.

## Contract Authority

- `contracts.lock.json` - pins the substrate checkout at `LawFirm-os-semantic-substrate` commit `43991155f0286e6d8bc5ba0bfe6b42407b1b3f12`.
- `.ai/control/governance-dependency-map-mirror.json` - local mirror of the upstream governance dependency map; it cannot override `LawFirm-os-semantic-substrate`.
- `scripts/validate_governance_dependency_map_mirror.py` - fail-closed check for mirror shape and watched governance paths.
- `config/validation-runtime-policy.yaml` - local validation runtime policy requiring the long-ceiling pytest wrapper.
- `registry/intake-orchestrator-adoption-review-registry.json` - candidate-only Orchestrator owner review docket for intake-to-budget workflow and carrier rejection capture/appeal interfaces.
- `scripts/validate_intake_orchestrator_adoption_review.py` - fail-closed check that the intake review docket remains candidate-only and does not assign canonical route/event/Lake/connector authority.
- `docs/INTAKE_OWNER_REVIEW_PACKET.md` - candidate execution artifact for synthetic intake owner-review packets.
- `src/lawfirm_os_orchestrator/intake/owner_review.py` - deterministic local packet builder for human pauses, rejection buckets, budget actuals variance, and Lake preview-only handoff.
- `docs/INTAKE_LAKE_ADMISSION_REVIEW_PACKET.md` - candidate execution artifact for packaging owner-review evidence into Exception Lake owner-review record-family summaries.
- `src/lawfirm_os_orchestrator/intake/lake_admission_review.py` - deterministic local packet builder for Lake admission-review blockers, source-hash status, idempotency keys, and no-write controls.
- `docs/INTAKE_NO_WRITE_VERTICAL_SLICE_DEMO.md` - Orchestrator-owned no-write cross-repo demo path for Intake -> owner review -> Lake admission review -> attorney review report.
- `src/lawfirm_os_orchestrator/intake/vertical_slice_demo.py` - deterministic local demo builder with sibling surface checks and no-write controls.
- `docs/LITIGATION_SIMULATION_ADAPTER_EXECUTION_PLAN.md` - future no-write adapter plan for Albers/ALS-style litigation simulator tools; no connector or real-data authority.
- Substrate `manifests/contract_manifest.v1.json` - canonical orchestrator-facing manifest. Loading is manifest-first.
- Substrate `registry/exception-route-registry.json` - canonical `route_id` and `event_class` authority.
- Substrate `registry/governance-dependency-map.json` - canonical governance-facing dependency map and child mirror update gate.
- Substrate `governance/AI_STRATEGY_DOCTRINE.md` - proposed AI strategy doctrine to consult, not override; not canon until approved in Semantic Substrate.
- Substrate `governance/DECISION_BOTTLENECK_AND_DECISION_MODELS.md` - canonical decision-bottleneck and decision-model doctrine.
- Substrate `governance/LITIGATION_SIMULATION_ADAPTER_BOUNDARY.md` and `governance/REAL_WORK_SHADOW_MODE_PILOT_GATES.md` - canonical future simulator and real-work shadow-mode boundaries.
- Substrate `registry/decision-model-registry.seed.json` - canonical seed decision-model registry consumed by orchestration guidance.
- `docs/CANONICAL_ROUTE_MAPPING.md` - maps local orchestrator labels to substrate authority and marks unmapped labels as non-canonical.
- `docs/ai-workflow/decision-model-gates.md` - execution-plane guidance for consuming decision-model gates.
- `docs/decisions/ADR-002-ai-strategy-and-decision-bottleneck.md` - accepted ADR for orchestrator consumption of the doctrine.

Required manifest fields include `manifest_id`, `manifest_version`, `policy_bundle_id`, `canonical_schema_keys`, and `registry_refs`. The reader fails closed if the manifest is missing or required fields are absent; `policy_bundle_id` must not be silently defaulted.

## AI Strategy Doctrine Dependency

- Consult, do not override, `../LawFirm-os-semantic-substrate/governance/AI_STRATEGY_DOCTRINE.md` for AI strategy, model/provider strategy, vendor lock-in, proprietary context, Legal Context Bundles, context quality, structured matter records, institutional knowledge encoding, Shannon / entropy / uncertainty framing, skill trust, AI governance boundaries, model routing policy, and orchestration governance.
- Runtime repos remain consumers of this doctrine and do not become semantic authority.
- This TOC does not imply automatic runtime routing unless an existing Semantic Substrate routing registry supports that behavior.

## Commands And Local Surfaces

- `ENDPOINTS_AND_COMMANDS.md` - current CLI commands and local-only script surfaces.
- `DATA_FLOW_MAP.md` - current execution-plane data flow.
- `scripts/run_full_pytest.py` - policy-backed pytest wrapper; direct pytest invocation is blocked.
- `scripts/run_evals.py` - offline classify-exception eval runner.
- `scripts/run_shadow_eval.py` - local proposal-only shadow eval runner.
- `scripts/build_upgrade_proposal.py` - local upgrade proposal packet builder.
- `scripts/render_codex_task.py` - inert Codex task draft renderer.
- `scripts/check_safety.py` - safety regression check.
- `tests/test_intake_owner_review_packet.py` - intake owner-review packet regression coverage.
- `tests/test_intake_lake_admission_review_packet.py` - intake Lake admission-review packet regression coverage.
- `tests/test_intake_vertical_slice_demo.py` - no-write cross-repo vertical-slice demo regression coverage.

## Learning And Research

- `config/research_sources.yaml` - pre-PR07, metadata-only, non-authoritative source-class mirror. It does not authorize crawling, scheduled jobs, model calls, external APIs, external writes, or production research automation.
- `src/lawfirm_os_orchestrator/discovery/` - local-only Research Radar import helpers.
- `src/lawfirm_os_orchestrator/learning/` - proposal-only learning objects, scoring, shadow evals, proposal packets, recommendations, and task draft rendering.
- `src/lawfirm_os_orchestrator/autonomy/` - PR02 local autonomy gate and PR03 green-lane watcher. Risk color controls authority.
- `src/lawfirm_os_orchestrator/harness/` - PR02 hardness, leverage, harness selection, and PR04 inert Codex task packet generation. Hardness controls harness depth; leverage controls priority.
- `src/lawfirm_os_orchestrator/research/` - PR03 local research-signal record ingestion for watcher inputs. This is not live Research Radar automation.

Phase 2 is partially implemented as local-only scaffolding. Research signals, algorithm insights, shadow evals, upgrade proposals, recommendations, and Codex task drafts are inert artifacts unless a human separately approves future work.

PR02 is implemented as execution-plane local records and CLI artifacts only. It does not define canonical schemas, route IDs, event classes, governance doctrine, or promotion decisions. PR07 will add fuller stakes and reversibility modeling.

PR03 is implemented as local green-lane assumption watching. It may recommend downgrades to yellow/red but never restores green.

PR04 is implemented as local inert Codex task packet generation. It compresses iteration context without granting authority or executing work. PR05/PR06/PR07 remain future phases.

The intake Orchestrator adoption review docket records future owner decisions for intake-to-budget workflow control, carrier rejection capture, appeal result learning, and budget actuals comparison without creating canonical authority. The local intake owner-review packet builder is a candidate execution artifact only; it remains synthetic-only, blocks on missing human/decision-model gates, and keeps Lake handoff preview-only. The local intake Lake admission-review packet builder packages that owner-review evidence for Exception Lake owner review while preserving no-write, no-SQLite, no-raw-payload, and no-canon-mapping controls.

## Hard Boundaries

- no Semantic Substrate writes
- no local canonical route or event-class authority
- no real client or matter data
- no live Research Radar automation
- no live web crawling
- no scheduled jobs
- no live model calls
- no external API calls
- no external writes
- no Git operations from inside the application
- Exception Lake mode remains disabled by default and not attempted unless explicitly configured
