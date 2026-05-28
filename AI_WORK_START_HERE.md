# AI_WORK_START_HERE.md

<!-- BEGIN LAWFIRM_OS_BOOTSTRAP -->
Managed bootstrap for AI-assisted work in the LawFirm OS multi-repo workspace. Route through the canonical AI front door and Skill-Agent Control Plane, but preserve local repo operating doctrine.

Required bootstrap read order:

1. AGENTS.md
2. skill-agent-manifest.json
3. Semantic Substrate registry/ai-front-door-registry.json
4. Semantic Substrate registry/skill-agent-control-plane-registry.json
5. Semantic Substrate governance/SKILL_AGENT_CONTROL_PLANE_BOUNDARY.md

Repo: LawFirm-os-orchestrator
Plane: execution plane
Repo purpose: Execution adapters, approvals, run ledgers, model/tool routing, and evidence packet assembly.
This repo must not own: Canonical schemas, canonical lifecycle states, legal document indexing, raw legal payload storage.

Run workspace preservation and control-plane validation before reporting success on managed patch work.
<!-- END LAWFIRM_OS_BOOTSTRAP -->

## Load before orchestration work: AI strategy and decision models

Before changing orchestration behavior, model routing, tool authority, approval gates, autonomy policy, or evidence-packet structure, load the Semantic Substrate strategy and decision-model doctrine.

Required read order:

```text
../LawFirm-os-semantic-substrate/registry/ai-front-door-registry.json
../LawFirm-os-semantic-substrate/AI_TABLE_OF_CONTENTS.md
../LawFirm-os-semantic-substrate/governance/AI_STRATEGY_DOCTRINE.md
../LawFirm-os-semantic-substrate/governance/DECISION_BOTTLENECK_AND_DECISION_MODELS.md
../LawFirm-os-semantic-substrate/registry/decision-model-registry.seed.json
```

Operating interpretation:

1. The Orchestrator executes decision models; it does not invent them.
2. Model output is proposal-only.
3. Evidence packets are decision-support units, not canon.
4. Throughput means accepted, decision-ready packets per reviewer hour, not raw model output.
5. Vendor/model/framework choice is an adapter decision under policy, not AI strategy.
6. Every high-stakes run should carry `decision_model_id` in the run ledger and evidence packet.
7. If a run has no applicable decision model, downgrade to `needs_review` or block until governance supplies one.

Design rule:

```text
No autonomous escalation in capability without a decision model, evidence minimum, approval rule, and revocation path.
```

<!-- BEGIN REPO_SPECIFIC_INSTRUCTIONS -->
# AI Work Start Here

Canonical machine name: `LawFirm-os-orchestrator`. Plane: execution.
Sibling repos: `LawFirm-os-semantic-substrate` (control plane), `exceptions-lake-runtime-main` (evidence plane).
For authority order across repos, read the substrate's `governance/CROSS_REPO_MAP.md`.

Route: `orchestrator.mvp.classify_exception`
Mode: `synthetic_only_local_first`
PR02/PR03/PR04 local routes: `classify-autonomy`, `select-harness`, `watch-green-lanes`, `generate-codex-task`
V1 seed read-first doc: `docs/seed/00_CODEX_READ_FIRST.md`
Cross-repo route mapping: `docs/CANONICAL_ROUTE_MAPPING.md`
Allowed paths: `src/lawfirm_os_orchestrator/**`, `tests/**`, `examples/**`, `docs/**`, `config/**`, `contracts.lock.json`
Forbidden paths: Semantic Substrate and Exceptions Lake runtime repos except through documented patches.
Contract surfaces touched (read-only): canonical orchestrator manifest at substrate `manifests/contract_manifest.v1.json`, `registry/exception-route-registry.json`, `registry/orchestrator-contract-export.json`, governance boundary docs.
Loading discipline: manifest-first; required manifest fields (`manifest_id`, `manifest_version`, `policy_bundle_id`, `canonical_schema_keys`, `registry_refs`) must not be silently defaulted. Fail-closed on SHA drift or missing required fields.
Autonomy discipline: risk color controls authority; hardness controls harness depth; leverage controls priority; stakes modeling remains PR07.
Green-lane discipline: green lanes are conditional; signals may downgrade green to yellow/red; humans restore green authority.
Task-packet discipline: Codex task packets are inert build instructions only and must not execute tools, code, Git, models, network, Substrate writes, or Lake writes.
Validation plan: run `python -m pytest`, `python scripts/check_safety.py --stdout json`, evals, and CLI smoke tests.
Stop conditions: see `docs/decisions/synthetic_only_policy.md`.

<!-- END REPO_SPECIFIC_INSTRUCTIONS -->

## Skill-Agent Control Plane References

- skill-agent-manifest.json
- Semantic Substrate registry/skill-agent-control-plane-registry.json
- Semantic Substrate registry/skill-agent-lifecycle-policy-registry.json
- Semantic Substrate registry/skill-agent-quality-scoring-registry.json
- Semantic Substrate scripts/validate_skill_agent_control_plane.py

## Validation Commands

    python -m pytest -q
    python ../LawFirm-os-semantic-substrate/scripts/validate_skill_agent_control_plane.py --workspace ..
